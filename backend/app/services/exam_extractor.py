from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from app.services.content_parser import (
    HASH_PREFIX,
    HEADER_TITLES,
    SOURCE_BOOK_FILE,
    _strip_noise_lines,
    parse_extracted_book,
)

QUESTION_START_RE = re.compile(
    r"(?m)^(?P<number>\d{1,3})\.\s*\((?P<source>[^)]+)\)\s*(?P<body>.*?)(?=^\d{1,3}\.\s*\(|\Z)",
    re.DOTALL,
)
OPTION_RE = re.compile(
    r"(?m)^[ \t]*(?P<letter>[a-e])\)[ \t]*(?P<text>.*?)(?=^[ \t]*[a-e]\)|\Z)",
    re.DOTALL | re.IGNORECASE,
)
GABARITO_HEADING_RE = re.compile(r"Æ\s+GABARITO|^\s*GABARITO\s*$", re.IGNORECASE | re.MULTILINE)
NUMBER_LINE_RE = re.compile(r"^\d{1,3}$")
LETTER_LINE_RE = re.compile(r"^[A-E]$", re.IGNORECASE)

HARD_TOPICS = ("INTERPRETA", "COERENCIA", "COESAO", "COERÊNCIA", "COESÃO")
EASY_TOPICS = ("ORTOGRAFIA", "PONTUA", "ACENTUA", "CRASE")


@dataclass(frozen=True)
class ExtractedOption:
    letter: str
    text: str
    is_correct: bool


@dataclass(frozen=True)
class ExtractedQuestion:
    number: int
    exam_source: str
    prompt: str
    options: tuple[ExtractedOption, ...]
    correct_letter: str
    explanation: str
    difficulty: str
    chapter_id: str
    chapter_title: str
    page: int
    paragraph_id: str
    stimulus: str | None
    source_file: str = SOURCE_BOOK_FILE


def extract_exam_questions(path: Path) -> list[ExtractedQuestion]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    pages: list[dict] = payload.get("pages") or []
    book = parse_extracted_book(path, source_file=path.name)
    gabarito = _parse_gabarito(pages)
    page_to_chapter = _page_chapter_map(book)
    raw_questions = _split_raw_questions(pages)

    extracted: list[ExtractedQuestion] = []
    seen: set[int] = set()
    last_stimulus: str | None = None

    for item in raw_questions:
        number = item["number"]
        if number in seen or number not in gabarito:
            continue
        options = _parse_options(item["body"])
        if len(options) < 4:
            continue
        correct = gabarito[number]
        if not any(option["letter"] == correct for option in options):
            continue

        prompt = _normalize_exam_text(_prompt_without_options(item["body"]))
        if not prompt:
            continue

        stimulus = item.get("stimulus")
        if stimulus:
            last_stimulus = stimulus
        elif item.get("carry_stimulus"):
            stimulus = last_stimulus
        else:
            last_stimulus = None

        chapter = page_to_chapter.get(item["page"])
        if chapter is None:
            continue

        letter_options = tuple(
            ExtractedOption(
                letter=option["letter"],
                text=option["text"],
                is_correct=option["letter"] == correct,
            )
            for option in options
        )
        extracted.append(
            ExtractedQuestion(
                number=number,
                exam_source=item["source"],
                prompt=prompt,
                options=letter_options,
                correct_letter=correct,
                explanation=(
                    f"Gabarito oficial do caderno {path.name}: alternativa {correct}. "
                    f"Questão {number} ({item['source']}), tópico «{chapter['title']}»."
                ),
                difficulty=_difficulty_for(chapter["title"]),
                chapter_id=chapter["id"],
                chapter_title=chapter["title"],
                page=item["page"],
                paragraph_id=f"q-{number}",
                stimulus=stimulus,
                source_file=path.name,
            )
        )
        seen.add(number)

    return extracted


def _parse_gabarito(pages: list[dict]) -> dict[int, str]:
    answers: dict[int, str] = {}
    collecting = False
    tokens: list[tuple[str, str | int]] = []

    for page in pages:
        text = (page.get("text") or "").replace("\r\n", "\n")
        if not collecting:
            match = GABARITO_HEADING_RE.search(text)
            if match is None or int(page["page"]) < 180:
                continue
            collecting = True
            text = text[match.end() :]

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith(HASH_PREFIX):
                continue
            if stripped.startswith("O conteúdo deste livro"):
                continue
            if stripped in HEADER_TITLES or stripped.upper() == "ANOTAÇÕES":
                continue
            if NUMBER_LINE_RE.fullmatch(stripped) and 1 <= int(stripped) <= 500:
                tokens.append(("n", int(stripped)))
            elif LETTER_LINE_RE.fullmatch(stripped):
                tokens.append(("l", stripped.upper()))

    index = 0
    while index < len(tokens) - 1:
        kind, value = tokens[index]
        next_kind, next_value = tokens[index + 1]
        if kind == "n" and next_kind == "l":
            answers[int(value)] = str(next_value)
            index += 2
        else:
            index += 1
    return answers


def _split_raw_questions(pages: list[dict]) -> list[dict]:
    parts: list[tuple[int, str]] = []
    for page in pages:
        page_number = int(page["page"])
        if page_number < 3 or page_number > 182:
            continue
        text = page.get("text") or ""
        if page_number >= 180:
            heading = GABARITO_HEADING_RE.search(text)
            if heading:
                text = text[: heading.start()]
        parts.append((page_number, _strip_noise_lines(text)))

    combined = ""
    index_to_page: list[int] = []
    for page_number, text in parts:
        start = len(combined)
        combined += text + "\n"
        index_to_page.extend([page_number] * (len(combined) - start))

    items: list[dict] = []
    last_end = 0
    for match in QUESTION_START_RE.finditer(combined):
        prefix = combined[last_end : match.start()]
        stimulus = _extract_stimulus(prefix)
        start_index = match.start()
        page = index_to_page[start_index] if start_index < len(index_to_page) else 3
        items.append(
            {
                "number": int(match.group("number")),
                "source": match.group("source").strip(),
                "body": match.group("body"),
                "page": page,
                "stimulus": stimulus,
                "carry_stimulus": not stimulus and _is_short_prefix(prefix),
            }
        )
        last_end = match.end()
    return items


def _extract_stimulus(prefix: str) -> str | None:
    match = re.search(r"(Utilize o texto.*)$", prefix, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    text = _normalize_exam_text(match.group(1))
    return text if len(text) > 40 else None


def _is_short_prefix(prefix: str) -> bool:
    return len(_normalize_exam_text(prefix)) < 80


def _parse_options(body: str) -> list[dict[str, str]]:
    sequences: list[list[dict[str, str]]] = []
    current: list[dict[str, str]] = []
    for match in OPTION_RE.finditer(body):
        letter = match.group("letter").upper()
        text = _normalize_exam_text(match.group("text"))
        if not text:
            continue
        item = {"letter": letter, "text": text}
        if letter == "A":
            if current:
                sequences.append(current)
            current = [item]
            continue
        if current and letter == chr(ord(current[-1]["letter"]) + 1):
            current.append(item)
            continue
        if current:
            sequences.append(current)
        current = []
    if current:
        sequences.append(current)
    valid = [sequence for sequence in sequences if len(sequence) >= 4]
    return valid[-1] if valid else []


def _prompt_without_options(body: str) -> str:
    first = OPTION_RE.search(body)
    return body[: first.start()] if first else body


def _normalize_exam_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _difficulty_for(title: str) -> str:
    upper = title.upper()
    if any(token in upper for token in HARD_TOPICS):
        return "hard"
    if any(token in upper for token in EASY_TOPICS):
        return "easy"
    return "medium"


def _page_chapter_map(book) -> dict[int, dict[str, str]]:
    mapping: dict[int, dict[str, str]] = {}
    study = [chapter for chapter in book.chapters if chapter.title.upper() != "GABARITO"]
    for chapter in study:
        for page in range(chapter.start_page, chapter.end_page + 1):
            mapping[page] = {"id": chapter.id, "title": chapter.title}
    if study:
        last = study[-1]
        for page in range(last.end_page + 1, 183):
            mapping.setdefault(page, {"id": last.id, "title": last.title})
    return mapping
