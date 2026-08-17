from .models import QuizAnswer, QuizAttempt
from .records import QuestionRecord
from .schemas import OptionPublic, QuestionPublic, SourceRef


def source_of(question: QuestionRecord) -> SourceRef:
    return SourceRef(
        chapter_id=question.chapter_id,
        chapter=question.chapter_title,
        page=question.page,
        paragraph_id=question.paragraph_id,
        source_file=question.source_file,
    )


def serialize_question(
    question: QuestionRecord,
    *,
    reveal: bool,
    answer: QuizAnswer | None = None,
) -> QuestionPublic:
    return QuestionPublic(
        id=question.id,
        number=question.number,
        exam_source=question.exam_source,
        prompt=question.prompt,
        stimulus=question.stimulus,
        difficulty=question.difficulty,
        options=[
            OptionPublic(
                letter=option.letter,
                text=option.text,
                is_correct=option.is_correct if reveal else None,
            )
            for option in question.options
        ],
        source=source_of(question),
        selected_letter=answer.selected_letter if answer else None,
        is_correct=answer.is_correct if answer else None,
        correct_letter=question.correct_letter if reveal else None,
        explanation=question.explanation if reveal else None,
    )


def attempt_answered_count(attempt: QuizAttempt) -> int:
    return len(attempt.answers)
