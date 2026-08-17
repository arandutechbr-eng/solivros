from __future__ import annotations

import json
from functools import lru_cache

from sqlalchemy.orm import Session

from .models import UserProgress
from .paths import CONTENT_JSON, QUESTIONS_JSON, SOURCE_JSON
from .records import BookRecord, ChapterRecord, OptionRecord, ParagraphRecord, QuestionRecord

GUEST_USER_ID = 1


@lru_cache(maxsize=1)
def load_book() -> BookRecord:
    if CONTENT_JSON.exists():
        payload = json.loads(CONTENT_JSON.read_text(encoding="utf-8"))
        return _book_from_payload(payload)
    return _book_from_source()


@lru_cache(maxsize=1)
def load_questions() -> tuple[QuestionRecord, ...]:
    if QUESTIONS_JSON.exists():
        payload = json.loads(QUESTIONS_JSON.read_text(encoding="utf-8"))
        return tuple(_question_from_payload(item) for item in payload)
    return _questions_from_source()


def question_map() -> dict[int, QuestionRecord]:
    return {question.id: question for question in load_questions()}


def ensure_catalog(db: Session) -> None:
    if db.get(UserProgress, GUEST_USER_ID) is None:
        db.add(UserProgress(user_id=GUEST_USER_ID))
        db.commit()


def _book_from_payload(payload: dict) -> BookRecord:
    chapters = [
        ChapterRecord(
            id=chapter["id"],
            number=chapter["number"],
            title=chapter["title"],
            start_page=chapter["start_page"],
            end_page=chapter["end_page"],
            paragraphs=[
                ParagraphRecord(
                    id=paragraph["id"],
                    page=paragraph["page"],
                    order=paragraph["order"],
                    kind=paragraph["kind"],
                    text=paragraph["text"],
                    question_number=paragraph.get("question_number"),
                    exam_source=paragraph.get("exam_source"),
                )
                for paragraph in chapter.get("paragraphs") or []
            ],
        )
        for chapter in payload.get("chapters") or []
    ]
    return BookRecord(
        source_file=payload["source_file"],
        title=payload["title"],
        subtitle=payload["subtitle"],
        page_count=payload["page_count"],
        question_count=payload["question_count"],
        chapters=chapters,
    )


def _question_from_payload(item: dict) -> QuestionRecord:
    return QuestionRecord(
        id=item["id"],
        number=item["number"],
        exam_source=item["exam_source"],
        prompt=item["prompt"],
        stimulus=item.get("stimulus"),
        explanation=item["explanation"],
        difficulty=item["difficulty"],
        chapter_id=item["chapter_id"],
        chapter_title=item["chapter_title"],
        page=item["page"],
        paragraph_id=item["paragraph_id"],
        correct_letter=item["correct_letter"],
        source_file=item["source_file"],
        options=tuple(
            OptionRecord(
                letter=option["letter"],
                text=option["text"],
                is_correct=option["is_correct"],
            )
            for option in item.get("options") or []
        ),
    )


def _book_from_source() -> BookRecord:
    from app.services.content_parser import parse_extracted_book

    if not SOURCE_JSON.exists():
        raise FileNotFoundError(f"Catálogo não encontrado: {CONTENT_JSON} ou {SOURCE_JSON}")
    book = parse_extracted_book(SOURCE_JSON, source_file=SOURCE_JSON.name)
    return BookRecord(
        source_file=book.source_file,
        title=book.title,
        subtitle=book.subtitle,
        page_count=book.page_count,
        question_count=book.question_count,
        chapters=[
            ChapterRecord(
                id=chapter.id,
                number=chapter.number,
                title=chapter.title,
                start_page=chapter.start_page,
                end_page=chapter.end_page,
                paragraphs=[
                    ParagraphRecord(
                        id=paragraph.id,
                        page=paragraph.page,
                        order=paragraph.order,
                        kind=paragraph.kind,
                        text=paragraph.text,
                        question_number=paragraph.question_number,
                        exam_source=paragraph.exam_source,
                    )
                    for paragraph in chapter.paragraphs
                ],
            )
            for chapter in book.chapters
        ],
    )


def _questions_from_source() -> tuple[QuestionRecord, ...]:
    from app.services.exam_extractor import extract_exam_questions

    if not SOURCE_JSON.exists():
        raise FileNotFoundError(f"Catálogo não encontrado: {QUESTIONS_JSON} ou {SOURCE_JSON}")
    return tuple(
        QuestionRecord(
            id=item.number,
            number=item.number,
            exam_source=item.exam_source,
            prompt=item.prompt,
            stimulus=item.stimulus,
            explanation=item.explanation,
            difficulty=item.difficulty,
            chapter_id=item.chapter_id,
            chapter_title=item.chapter_title,
            page=item.page,
            paragraph_id=item.paragraph_id,
            correct_letter=item.correct_letter,
            source_file=item.source_file,
            options=tuple(
                OptionRecord(letter=option.letter, text=option.text, is_correct=option.is_correct)
                for option in item.options
            ),
        )
        for item in extract_exam_questions(SOURCE_JSON)
    )
