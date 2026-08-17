from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.models.enums import ParagraphType

CHAPTER_PATTERN = re.compile(
    r"^(?:cap[íi]tulo|chapter)\s+([ivxlcdm]+|\d+)\b.*$",
    re.IGNORECASE,
)
ROMAN_ONLY_PATTERN = re.compile(r"^(?:I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|\d{1,2})$")
HEADING_PATTERN = re.compile(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9][A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9\s,.\-:]{3,80}$")


@dataclass
class StructuredParagraph:
    content: str
    type: ParagraphType
    confidence: float
    order: int


@dataclass
class StructuredChapter:
    title: str
    number: int | None
    order: int
    paragraphs: list[StructuredParagraph] = field(default_factory=list)


def structure_pages(pages: list[dict[str, Any]]) -> list[StructuredChapter]:
    chapters = _split_chapters(pages)
    populated = [chapter for chapter in chapters if chapter.paragraphs]
    named = [
        chapter
        for chapter in populated
        if chapter.number is not None or CHAPTER_PATTERN.match(chapter.title)
    ]
    if len(named) >= 2:
        preamble = [chapter for chapter in populated if chapter not in named]
        return preamble + named if _has_substantial_content(preamble) else named
    if len(populated) < 2:
        return [_merge_as_single_chapter(chapters)]
    return populated


def _split_chapters(pages: list[dict[str, Any]]) -> list[StructuredChapter]:
    chapters: list[StructuredChapter] = []
    current: StructuredChapter | None = None
    buffer: list[str] = []
    buffer_confidence = 1.0

    def flush() -> None:
        nonlocal buffer, buffer_confidence, current
        if current is None or not buffer:
            buffer = []
            buffer_confidence = 1.0
            return
        content = " ".join(buffer).strip()
        current.paragraphs.append(
            StructuredParagraph(
                content=content,
                type=_classify_paragraph(content),
                confidence=buffer_confidence,
                order=len(current.paragraphs),
            )
        )
        buffer = []
        buffer_confidence = 1.0

    def ensure_chapter() -> StructuredChapter:
        nonlocal current
        if current is None:
            current = StructuredChapter(title="Início", number=None, order=0)
            chapters.append(current)
        return current

    for page in pages:
        confidence = float(page.get("confidence") or (0.7 if page.get("ocr") else 1.0))
        text = page.get("text") or ""
        for raw_line in text.split("\n"):
            line = raw_line.strip()
            if not line:
                flush()
                continue

            chapter_match = CHAPTER_PATTERN.match(line)
            if chapter_match or ROMAN_ONLY_PATTERN.match(line):
                flush()
                number_token = chapter_match.group(1) if chapter_match else line
                current = StructuredChapter(
                    title=line if chapter_match else f"Capítulo {line}",
                    number=_parse_chapter_number(number_token),
                    order=len(chapters),
                )
                chapters.append(current)
                continue

            ensure_chapter()
            buffer.append(line)
            buffer_confidence = min(buffer_confidence, confidence)

    flush()
    return chapters


def _has_substantial_content(chapters: list[StructuredChapter]) -> bool:
    text = " ".join(paragraph.content for chapter in chapters for paragraph in chapter.paragraphs)
    return len(text) >= 80


def _merge_as_single_chapter(chapters: list[StructuredChapter]) -> StructuredChapter:
    merged = StructuredChapter(title="Conteúdo", number=None, order=0)
    for chapter in chapters:
        if chapter.title not in {"Início", "Conteúdo"}:
            merged.paragraphs.append(
                StructuredParagraph(
                    content=chapter.title,
                    type=ParagraphType.HEADING,
                    confidence=1.0,
                    order=len(merged.paragraphs),
                )
            )
        for paragraph in chapter.paragraphs:
            paragraph.order = len(merged.paragraphs)
            merged.paragraphs.append(paragraph)
    if not merged.paragraphs:
        merged.paragraphs.append(
            StructuredParagraph(content="", type=ParagraphType.PARAGRAPH, confidence=1.0, order=0)
        )
    return merged


def _classify_paragraph(content: str) -> ParagraphType:
    if len(content) <= 80 and HEADING_PATTERN.match(content) and not content.endswith("."):
        return ParagraphType.HEADING
    if content.startswith(("“", '"', "«")) and len(content) < 400:
        return ParagraphType.QUOTE
    return ParagraphType.PARAGRAPH


def _parse_chapter_number(value: str) -> int | None:
    if value.isdigit():
        return int(value)
    roman = {
        "I": 1,
        "II": 2,
        "III": 3,
        "IV": 4,
        "V": 5,
        "VI": 6,
        "VII": 7,
        "VIII": 8,
        "IX": 9,
        "X": 10,
        "XI": 11,
        "XII": 12,
    }
    return roman.get(value.upper())
