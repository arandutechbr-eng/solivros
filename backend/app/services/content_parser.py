from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

SOURCE_BOOK_FILE = "5.json"
LICENSE_MARKER = "O conteúdo deste livro eletrônico é licenciado"
HASH_PREFIX = "x1y2z3"

TOC_ENTRY_RE = re.compile(
    r"Æ\s+(?P<title>[^Æ]+?)\.{2,}\s*(?P<page>\d+)",
    re.DOTALL,
)
TOPIC_HEADING_RE = re.compile(r"^Æ\s+(?P<title>.+?)\s*$")
QUESTION_START_RE = re.compile(r"^(?P<number>\d{1,3})\.\s*\((?P<source>[^)]+)\)(?P<rest>.*)$")
STIMULUS_RE = re.compile(r"^Utilize o texto", re.IGNORECASE)
PAGE_NUMBER_RE = re.compile(r"^\d{1,3}$")
NOISE_SNIPPETS = (
    LICENSE_MARKER,
    "sujeitando-se aos infratores",
    "vedada, por quaisquer meios",
    "a sua reprodução, cópia, divulgação",
)
HEADER_TITLES = {
    "LÍNGUA PORTUGUESA",
    "LÍNGUA INGLESA",
    "MATEMÁTICA",
    "SUMÁRIO",
    "ANOTAÇÕES",
    "CONHECIMENTOS GERAIS",
}


@dataclass
class ContentParagraph:
    id: str
    page: int
    order: int
    kind: str
    text: str
    question_number: int | None = None
    exam_source: str | None = None


@dataclass
class ContentChapter:
    id: str
    number: int
    title: str
    start_page: int
    end_page: int
    paragraphs: list[ContentParagraph] = field(default_factory=list)

    @property
    def paragraph_count(self) -> int:
        return len(self.paragraphs)

    @property
    def question_count(self) -> int:
        return sum(1 for paragraph in self.paragraphs if paragraph.kind == "question")


@dataclass
class ContentBook:
    source_file: str
    book_id: int | None
    title: str
    subtitle: str
    page_count: int
    chapters: list[ContentChapter]
    paragraph_count: int
    question_count: int


def parse_extracted_book(path: Path, source_file: str = SOURCE_BOOK_FILE) -> ContentBook:
    payload = json.loads(path.read_text(encoding="utf-8"))
    pages: list[dict[str, Any]] = payload.get("pages") or []
    if not pages:
        raise ValueError("Arquivo de conteúdo sem páginas")

    title, subtitle = _extract_cover_titles(pages[0].get("text") or "")
    toc_entries = _parse_toc(pages)
    heading_pages = _detect_heading_pages(pages)
    chapters_meta = _build_chapter_ranges(toc_entries, heading_pages, len(pages))

    chapters: list[ContentChapter] = [
        ContentChapter(
            id=_slug(meta["title"], index),
            number=index,
            title=meta["title"],
            start_page=meta["start_page"],
            end_page=meta["end_page"],
        )
        for index, meta in enumerate(chapters_meta, start=1)
    ]
    chapter_by_title = {_normalize_title(chapter.title): index for index, chapter in enumerate(chapters)}
    current_index = 0
    first_content_page = chapters[0].start_page if chapters else 3

    for page in pages:
        page_number = int(page["page"])
        if page_number < first_content_page:
            continue
        while current_index + 1 < len(chapters) and page_number >= chapters[current_index + 1].start_page:
            # Stay on the first chapter that starts on this page until a heading switches it.
            if page_number > chapters[current_index + 1].start_page:
                current_index += 1
            else:
                break
        for block in _split_page_blocks(page_number, page.get("text") or ""):
            if block.kind == "heading":
                matched = _match_chapter_index(block.text, chapter_by_title)
                if matched is not None:
                    current_index = matched
                    continue
            chapter = chapters[current_index]
            block.order = len(chapter.paragraphs)
            chapter.paragraphs.append(block)

    all_paragraphs = [paragraph for chapter in chapters for paragraph in chapter.paragraphs]
    question_numbers = {
        paragraph.question_number
        for paragraph in all_paragraphs
        if paragraph.kind == "question" and paragraph.question_number is not None
    }

    return ContentBook(
        source_file=source_file,
        book_id=payload.get("book_id"),
        title=title,
        subtitle=subtitle,
        page_count=int(payload.get("page_count") or len(pages)),
        chapters=chapters,
        paragraph_count=len(all_paragraphs),
        question_count=len(question_numbers),
    )


@lru_cache(maxsize=1)
def parse_default_book(path: str) -> ContentBook:
    return parse_extracted_book(Path(path))


def _extract_cover_titles(text: str) -> tuple[str, str]:
    joined = re.sub(r"\s+", " ", text)
    title = "1.000 Questões para a Transpetro"
    if "TRANSPETRO" in joined.upper():
        title = "1.000 Questões para a Transpetro"
    subtitle = "Conhecimentos Gerais"
    upper = joined.upper()
    if "MATEMÁTICA" in upper or "MATEMATICA" in upper:
        subtitle = "Matemática — Conhecimentos Gerais"
    elif "LÍNGUA INGLESA" in upper or "LINGUA INGLESA" in upper:
        subtitle = "Língua Inglesa — Conhecimentos Gerais"
    elif "LÍNGUA PORTUGUESA" in upper or "LINGUA PORTUGUESA" in upper:
        subtitle = "Língua Portuguesa — Conhecimentos Gerais"
    return title, subtitle


def _parse_toc(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sumario_page = next((page for page in pages if "SUMÁRIO" in (page.get("text") or "").upper()), None)
    if sumario_page is None:
        return []
    text = sumario_page["text"].replace("\r\n", "\n")
    compact = re.sub(r"[\n\t]+", " ", text)
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in TOC_ENTRY_RE.finditer(compact):
        title = _clean_title(match.group("title"))
        key = _normalize_title(title)
        if not title or key in seen:
            continue
        seen.add(key)
        entries.append({"title": title, "printed_page": int(match.group("page"))})
    if "GABARITO" not in seen:
        gabarito = re.search(r"Æ\s+GABARITO.*?(\d{2,3})", compact, re.IGNORECASE)
        if gabarito:
            entries.append({"title": "Gabarito", "printed_page": int(gabarito.group(1))})
    return entries


def _detect_heading_pages(pages: list[dict[str, Any]]) -> dict[str, int]:
    found: dict[str, int] = {}
    for page in pages:
        page_number = int(page["page"])
        if page_number <= 2:
            continue
        for line in (page.get("text") or "").splitlines():
            match = TOPIC_HEADING_RE.match(line.strip())
            if not match:
                continue
            title = _clean_title(match.group("title"))
            key = _normalize_title(title)
            if key and key not in found:
                found[key] = page_number
    return found


def _build_chapter_ranges(
    toc_entries: list[dict[str, Any]],
    heading_pages: dict[str, int],
    page_count: int,
) -> list[dict[str, Any]]:
    offset = 2
    metas: list[dict[str, Any]] = []
    for entry in toc_entries:
        title = entry["title"]
        detected = _match_heading_page(title, heading_pages)
        start_page = detected or (entry["printed_page"] + offset)
        metas.append({"title": title, "start_page": start_page})

    if not metas:
        metas = [{"title": "Conteúdo", "start_page": 3}]

    ranges: list[dict[str, Any]] = []
    for index, meta in enumerate(metas):
        end_page = metas[index + 1]["start_page"] - 1 if index + 1 < len(metas) else page_count
        ranges.append(
            {
                "title": meta["title"],
                "start_page": meta["start_page"],
                "end_page": max(meta["start_page"], end_page),
            }
        )
    return ranges


def _match_chapter_index(title: str, chapter_by_title: dict[str, int]) -> int | None:
    wanted = _normalize_title(title)
    if wanted in chapter_by_title:
        return chapter_by_title[wanted]
    for key, index in chapter_by_title.items():
        if wanted.startswith(key) or key.startswith(wanted[:24]):
            return index
    return None


def _match_heading_page(title: str, heading_pages: dict[str, int]) -> int | None:
    wanted = _normalize_title(title)
    if wanted in heading_pages:
        return heading_pages[wanted]
    for key, page in heading_pages.items():
        if wanted.startswith(key) or key.startswith(wanted[:24]):
            return page
    return None


def _split_page_blocks(page_number: int, text: str) -> list[ContentParagraph]:
    cleaned = _strip_noise_lines(text)
    lines = [line.rstrip() for line in cleaned.splitlines()]
    blocks: list[ContentParagraph] = []
    buffer: list[str] = []
    current_kind = "paragraph"
    question_number: int | None = None
    exam_source: str | None = None
    block_index = 0

    def flush() -> None:
        nonlocal buffer, current_kind, question_number, exam_source, block_index
        content = _join_hyphenated(" ".join(item.strip() for item in buffer if item.strip()))
        if content:
            blocks.append(
                ContentParagraph(
                    id=f"p-{page_number}-{block_index}",
                    page=page_number,
                    order=0,
                    kind=current_kind,
                    text=content,
                    question_number=question_number,
                    exam_source=exam_source,
                )
            )
            block_index += 1
        buffer = []
        current_kind = "paragraph"
        question_number = None
        exam_source = None

    for raw in lines:
        line = raw.strip()
        if not line:
            flush()
            continue

        heading_match = TOPIC_HEADING_RE.match(line)
        question_match = QUESTION_START_RE.match(line)
        if heading_match:
            flush()
            current_kind = "heading"
            buffer = [_clean_title(heading_match.group("title"))]
            flush()
            continue
        if question_match:
            flush()
            current_kind = "question"
            question_number = int(question_match.group("number"))
            exam_source = question_match.group("source").strip()
            rest = question_match.group("rest").strip()
            buffer = [rest] if rest else []
            continue
        if STIMULUS_RE.match(line) or line.lower().startswith("texto "):
            if current_kind != "stimulus":
                flush()
                current_kind = "stimulus"
            buffer.append(line)
            continue
        buffer.append(line)

    flush()
    return blocks


def _strip_noise_lines(text: str) -> str:
    kept: list[str] = []
    for line in text.replace("\r\n", "\n").splitlines():
        stripped = line.strip()
        if any(snippet in stripped for snippet in NOISE_SNIPPETS):
            continue
        if stripped.startswith(HASH_PREFIX):
            continue
        if stripped in HEADER_TITLES:
            continue
        if PAGE_NUMBER_RE.fullmatch(stripped):
            continue
        kept.append(line)
    return "\n".join(kept)


def _join_hyphenated(text: str) -> str:
    return re.sub(r"(\w)-\s+(\w)", r"\1\2", re.sub(r"\s+", " ", text)).strip()


def _clean_title(value: str) -> str:
    title = re.sub(r"\.{2,}", " ", value)
    title = re.sub(r"\s+", " ", title).strip(" .")
    return title


def _normalize_title(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", " ", value.upper()).strip()


def _slug(title: str, number: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"{number:02d}-{slug[:60]}" if slug else f"capitulo-{number:02d}"
