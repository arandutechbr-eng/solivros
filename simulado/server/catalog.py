from __future__ import annotations

import json
from functools import lru_cache

from sqlalchemy.orm import Session

from .models import UserProgress
from .records import BookRecord, ChapterRecord, OptionRecord, ParagraphRecord, QuestionRecord
from .subjects import DEFAULT_SUBJECT_ID, SUBJECTS, Subject, get_subject

GUEST_USER_ID = 1


def list_subjects() -> list[Subject]:
    return list(SUBJECTS)


@lru_cache(maxsize=8)
def load_book(subject_id: str = DEFAULT_SUBJECT_ID) -> BookRecord:
    subject = get_subject(subject_id)
    if subject.content_path.exists():
        payload = json.loads(subject.content_path.read_text(encoding="utf-8"))
        return _book_from_payload(payload, subject)
    return _book_from_source(subject)


@lru_cache(maxsize=8)
def load_questions(subject_id: str = DEFAULT_SUBJECT_ID) -> tuple[QuestionRecord, ...]:
    subject = get_subject(subject_id)
    if subject.questions_path.exists():
        payload = json.loads(subject.questions_path.read_text(encoding="utf-8"))
        return tuple(_question_from_payload(item, subject) for item in payload)
    return _questions_from_source(subject)


def question_map() -> dict[int, QuestionRecord]:
    mapping: dict[int, QuestionRecord] = {}
    for subject in SUBJECTS:
        for question in load_questions(subject.id):
            mapping[question.id] = question
    return mapping


def find_chapter(chapter_id: str) -> tuple[Subject, ChapterRecord]:
    for subject in SUBJECTS:
        book = load_book(subject.id)
        for chapter in book.chapters:
            if chapter.id == chapter_id:
                return subject, chapter
    raise KeyError(chapter_id)


def ensure_catalog(db: Session) -> None:
    if db.get(UserProgress, GUEST_USER_ID) is None:
        db.add(UserProgress(user_id=GUEST_USER_ID))
        db.commit()


def _book_from_payload(payload: dict, subject: Subject) -> BookRecord:
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
        source_file=payload.get("source_file") or subject.filename,
        title=payload.get("title") or subject.title,
        subtitle=payload.get("subtitle") or subject.subtitle,
        page_count=payload["page_count"],
        question_count=payload["question_count"],
        subject_id=subject.id,
        chapters=chapters,
    )


def _question_from_payload(item: dict, subject: Subject) -> QuestionRecord:
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
        source_file=item.get("source_file") or subject.filename,
        subject_id=item.get("subject_id") or subject.id,
        options=tuple(
            OptionRecord(
                letter=option["letter"],
                text=option["text"],
                is_correct=option["is_correct"],
            )
            for option in item.get("options") or []
        ),
    )


def _prefix_chapter_id(subject: Subject, chapter_id: str) -> str:
    if chapter_id.startswith(f"{subject.id}-"):
        return chapter_id
    return f"{subject.id}-{chapter_id}"


def _book_from_source(subject: Subject) -> BookRecord:
    from app.services.content_parser import parse_extracted_book

    if not subject.source_path.exists():
        raise FileNotFoundError(f"Catálogo não encontrado: {subject.content_path} ou {subject.source_path}")
    book = parse_extracted_book(subject.source_path, source_file=subject.filename)
    return BookRecord(
        source_file=book.source_file,
        title=subject.title,
        subtitle=subject.subtitle,
        page_count=book.page_count,
        question_count=book.question_count,
        subject_id=subject.id,
        chapters=[
            ChapterRecord(
                id=_prefix_chapter_id(subject, chapter.id),
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


def _questions_from_source(subject: Subject) -> tuple[QuestionRecord, ...]:
    from app.services.exam_extractor import extract_exam_questions

    if not subject.source_path.exists():
        raise FileNotFoundError(f"Catálogo não encontrado: {subject.questions_path} ou {subject.source_path}")
    book = _book_from_source(subject)
    chapter_by_old = {chapter.id.removeprefix(f"{subject.id}-"): chapter.id for chapter in book.chapters}
    return tuple(
        QuestionRecord(
            id=item.id,
            number=item.number,
            exam_source=item.exam_source,
            prompt=item.prompt,
            stimulus=item.stimulus,
            explanation=item.explanation,
            difficulty=item.difficulty,
            chapter_id=chapter_by_old.get(item.chapter_id, _prefix_chapter_id(subject, item.chapter_id)),
            chapter_title=item.chapter_title,
            page=item.page,
            paragraph_id=item.paragraph_id,
            correct_letter=item.correct_letter,
            source_file=item.source_file,
            subject_id=subject.id,
            options=tuple(
                OptionRecord(letter=option.letter, text=option.text, is_correct=option.is_correct)
                for option in item.options
            ),
        )
        for item in extract_exam_questions(subject.source_path)
    )
