from __future__ import annotations

import json

from .catalog import _book_from_source, _questions_from_source
from .subjects import SUBJECTS


def export_catalog() -> None:
    for subject in SUBJECTS:
        subject.data_dir.mkdir(parents=True, exist_ok=True)
        book = _book_from_source(subject)
        questions = _questions_from_source(subject)
        subject.content_path.write_text(
            json.dumps(
                {
                    "source_file": book.source_file,
                    "title": book.title,
                    "subtitle": book.subtitle,
                    "page_count": book.page_count,
                    "question_count": len(questions),
                    "subject_id": subject.id,
                    "chapters": [
                        {
                            "id": chapter.id,
                            "number": chapter.number,
                            "title": chapter.title,
                            "start_page": chapter.start_page,
                            "end_page": chapter.end_page,
                            "paragraphs": [
                                {
                                    "id": paragraph.id,
                                    "page": paragraph.page,
                                    "order": paragraph.order,
                                    "kind": paragraph.kind,
                                    "text": paragraph.text,
                                    "question_number": paragraph.question_number,
                                    "exam_source": paragraph.exam_source,
                                }
                                for paragraph in chapter.paragraphs
                            ],
                        }
                        for chapter in book.chapters
                        if chapter.title.upper() != "GABARITO"
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        subject.questions_path.write_text(
            json.dumps(
                [
                    {
                        "id": question.id,
                        "number": question.number,
                        "exam_source": question.exam_source,
                        "prompt": question.prompt,
                        "stimulus": question.stimulus,
                        "explanation": question.explanation,
                        "difficulty": question.difficulty,
                        "chapter_id": question.chapter_id,
                        "chapter_title": question.chapter_title,
                        "page": question.page,
                        "paragraph_id": question.paragraph_id,
                        "correct_letter": question.correct_letter,
                        "source_file": question.source_file,
                        "subject_id": question.subject_id,
                        "options": [
                            {
                                "letter": option.letter,
                                "text": option.text,
                                "is_correct": option.is_correct,
                            }
                            for option in question.options
                        ],
                    }
                    for question in questions
                ],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        print(f"{subject.id}: {len(questions)} questões -> {subject.questions_path}")


if __name__ == "__main__":
    export_catalog()
