from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from app.services.content_parser import (
    HASH_PREFIX,
    HEADER_TITLES,
    LICENSE_MARKER,
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
STIMULUS_HEAD_RE = re.compile(r"Utilize o texto|Texto\s+(?:[IVX]+|\d+)\b", re.IGNORECASE)
TEXTO_LABEL_RE = re.compile(r"(?:^|\n)\s*Texto\s+([IVX]+|\d+)\b", re.IGNORECASE)
TRAILING_PASSAGE_RE = re.compile(
    r"(?m)^[ \t]*(?:Utilize o texto|Texto\s+(?:[IVX]+|\d+)\s*$)",
    re.IGNORECASE,
)

HARD_TOPICS = (
    "INTERPRETA",
    "COERENCIA",
    "COESAO",
    "COERÊNCIA",
    "COESÃO",
    "COMBINATÓRIA",
    "COMBINATORIA",
    "LOGARÍTMIC",
    "TRIGONOM",
    "GEOMETRIA ESPACIAL",
    "JUROS COMPOSTOS",
    "PROBABILIDADE",
)
EASY_TOPICS = (
    "ORTOGRAFIA",
    "PONTUA",
    "ACENTUA",
    "CRASE",
    "ADIÇÃO",
    "ADICAO",
    "NÚMEROS NATURAIS",
    "NUMEROS NATURAIS",
    "NÚMEROS INTEIROS",
    "FRAÇÕES",
    "DECIMAIS",
)


@dataclass(frozen=True)
class ExtractedOption:
    letter: str
    text: str
    is_correct: bool


@dataclass(frozen=True)
class ExtractedQuestion:
    id: int
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
    book_id = int(payload.get("book_id") or 0)
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

        available = item.get("stimulus") or last_stimulus
        stimulus = _stimulus_for_prompt(available, prompt)
        trailing = _text_after_options(item["body"])
        if trailing:
            last_stimulus = trailing
        elif item.get("stimulus"):
            last_stimulus = item["stimulus"]

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
                id=book_id * 10_000 + number,
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
            if match is None or int(page["page"]) <= 2:
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


def _gabarito_start_page(pages: list[dict]) -> int:
    for page in pages:
        page_number = int(page["page"])
        if page_number <= 2:
            continue
        if GABARITO_HEADING_RE.search(page.get("text") or ""):
            return page_number
    return max((int(page["page"]) for page in pages), default=3)


def _split_raw_questions(pages: list[dict]) -> list[dict]:
    gabarito_page = _gabarito_start_page(pages)
    parts: list[tuple[int, str]] = []
    for page in pages:
        page_number = int(page["page"])
        if page_number < 3 or page_number > gabarito_page:
            continue
        text = page.get("text") or ""
        if page_number >= gabarito_page - 1:
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
    match = STIMULUS_HEAD_RE.search(prefix)
    if not match:
        return None
    text = _clean_passage(prefix[match.start() :])
    return text if _looks_like_passage(text) else None


def _is_short_prefix(prefix: str) -> bool:
    return len(_normalize_exam_text(prefix)) < 80


def _parse_options(body: str) -> list[dict[str, str]]:
    runs = [options for options, _end in _option_runs(body) if len(options) >= 4]
    return runs[-1] if runs else []


def _option_runs(body: str) -> list[tuple[list[dict[str, str]], int]]:
    sequences: list[tuple[list[dict[str, str]], int]] = []
    current: list[dict[str, str]] = []
    current_end = 0
    for match in OPTION_RE.finditer(body):
        letter = match.group("letter").upper()
        raw_text = match.group("text")
        cut = TRAILING_PASSAGE_RE.search(raw_text)
        if cut:
            text = _normalize_exam_text(raw_text[: cut.start()])
            end = match.start("text") + cut.start()
        else:
            text = _normalize_exam_text(raw_text)
            end = match.end()
        if not text:
            continue
        item = {"letter": letter, "text": text}
        if letter == "A":
            if current:
                sequences.append((current, current_end))
            current = [item]
            current_end = end
            continue
        if current and letter == chr(ord(current[-1]["letter"]) + 1):
            current.append(item)
            current_end = end
            continue
        if current:
            sequences.append((current, current_end))
        current = []
        current_end = 0
    if current:
        sequences.append((current, current_end))
    return sequences


def _text_after_options(body: str) -> str | None:
    runs = [run for run in _option_runs(body) if len(run[0]) >= 4]
    if not runs:
        return None
    rest = _clean_passage(body[runs[-1][1] :])
    return rest if _looks_like_passage(rest) else None


def _clean_passage(text: str) -> str:
    if LICENSE_MARKER in text:
        text = text.split(LICENSE_MARKER)[0]
    return _normalize_exam_text(text)


def _looks_like_passage(text: str) -> bool:
    return len(text) >= 80


def _labeled_passages(passage: str) -> dict[str, str]:
    matches = list(TEXTO_LABEL_RE.finditer(passage))
    if not matches:
        return {}
    labeled: dict[str, str] = {}
    for index, match in enumerate(matches):
        label = match.group(1).upper()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(passage)
        chunk = _normalize_exam_text(passage[match.start() : end])
        if chunk:
            labeled[label] = chunk
    return labeled


def _stimulus_for_prompt(passage: str | None, prompt: str) -> str | None:
    if not passage:
        return None
    labeled = _labeled_passages(passage)
    upper = prompt.upper()
    for label in ("III", "II", "I"):
        if re.search(rf"TEXTO\s+{label}\b", upper) and label in labeled:
            return labeled[label]
    return passage


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
        last_page = max((chapter.end_page for chapter in study), default=last.end_page)
        for page in range(last.end_page + 1, last_page + 8):
            mapping.setdefault(page, {"id": last.id, "title": last.title})
    return mapping
