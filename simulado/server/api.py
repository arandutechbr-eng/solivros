from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from . import quiz_service
from .catalog import find_chapter, list_subjects, load_book
from .database import get_db
from .schemas import (
    AnswerFeedback,
    AnswerRequest,
    AttemptDetail,
    AttemptSummary,
    ChapterDetail,
    ChapterSummary,
    ContentBook,
    ParagraphPublic,
    ProgressResponse,
    StartQuizRequest,
    SubjectPublic,
)
from .serializers import attempt_answered_count, serialize_question, source_of
from .subjects import DEFAULT_SUBJECT_ID

router = APIRouter(prefix="/api")


@router.get("/subjects", response_model=list[SubjectPublic])
def get_subjects() -> list[SubjectPublic]:
    items: list[SubjectPublic] = []
    for subject in list_subjects():
        try:
            book = load_book(subject.id)
        except FileNotFoundError:
            continue
        chapters = [chapter for chapter in book.chapters if chapter.title.upper() != "GABARITO"]
        items.append(
            SubjectPublic(
                id=subject.id,
                title=subject.title,
                subtitle=subject.subtitle,
                question_count=book.question_count,
                chapter_count=len(chapters),
                source_file=book.source_file,
            )
        )
    return items


@router.get("/content", response_model=ContentBook)
def get_content(subject: str = Query(default=DEFAULT_SUBJECT_ID)) -> ContentBook:
    try:
        book = load_book(subject)
    except (KeyError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail="Matéria não encontrada") from exc
    chapters = [chapter for chapter in book.chapters if chapter.title.upper() != "GABARITO"]
    return ContentBook(
        source_file=book.source_file,
        title=book.title,
        subtitle=book.subtitle,
        page_count=book.page_count,
        chapter_count=len(chapters),
        paragraph_count=sum(chapter.paragraph_count for chapter in chapters),
        question_count=book.question_count,
        subject_id=book.subject_id,
        chapters=[_chapter_summary(chapter) for chapter in chapters],
    )


@router.get("/content/chapters", response_model=list[ChapterSummary])
def list_chapters(subject: str = Query(default=DEFAULT_SUBJECT_ID)) -> list[ChapterSummary]:
    try:
        book = load_book(subject)
    except (KeyError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail="Matéria não encontrada") from exc
    return [_chapter_summary(chapter) for chapter in book.chapters if chapter.title.upper() != "GABARITO"]


@router.get("/content/chapters/{chapter_id}", response_model=ChapterDetail)
def get_chapter(chapter_id: str) -> ChapterDetail:
    try:
        _, chapter = find_chapter(chapter_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Capítulo não encontrado") from exc
    summary = _chapter_summary(chapter)
    return ChapterDetail(
        **summary.model_dump(),
        paragraphs=[
            ParagraphPublic(
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


@router.post("/quizzes/start", response_model=AttemptDetail)
def start_quiz(payload: StartQuizRequest, db: Session = Depends(get_db)) -> AttemptDetail:
    try:
        attempt = quiz_service.start_quiz(
            db,
            mode=payload.mode,
            subject_id=payload.subject_id,
            chapter_id=payload.chapter_id,
            count=payload.count,
            difficulty=payload.difficulty,
            time_limit_minutes=payload.time_limit_minutes,
        )
    except quiz_service.QuizError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return _attempt_detail(db, attempt)


@router.get("/attempts", response_model=list[AttemptSummary])
def list_attempts(db: Session = Depends(get_db)) -> list[AttemptSummary]:
    return [_attempt_summary(attempt) for attempt in quiz_service.list_attempts(db)]


@router.get("/attempts/{attempt_id}", response_model=AttemptDetail)
def get_attempt(attempt_id: int, db: Session = Depends(get_db)) -> AttemptDetail:
    try:
        attempt = quiz_service.get_attempt(db, attempt_id)
    except quiz_service.QuizError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return _attempt_detail(db, attempt)


@router.post("/attempts/{attempt_id}/answer", response_model=AnswerFeedback)
def answer_question(attempt_id: int, payload: AnswerRequest, db: Session = Depends(get_db)) -> AnswerFeedback:
    try:
        record, xp_earned = quiz_service.answer_question(
            db, attempt_id, payload.question_id, payload.selected_letter
        )
        attempt = quiz_service.get_attempt(db, attempt_id)
        question = next(item for item in quiz_service.questions_for_attempt(attempt) if item.id == payload.question_id)
    except quiz_service.QuizError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except StopIteration as exc:
        raise HTTPException(status_code=404, detail="Questão não encontrada") from exc
    return AnswerFeedback(
        question_id=record.question_id,
        selected_letter=record.selected_letter,
        is_correct=record.is_correct,
        correct_letter=question.correct_letter,
        explanation=question.explanation,
        source=source_of(question),
        xp_earned=xp_earned,
    )


@router.post("/attempts/{attempt_id}/finish", response_model=AttemptDetail)
def finish_quiz(attempt_id: int, db: Session = Depends(get_db)) -> AttemptDetail:
    try:
        attempt = quiz_service.finish_quiz(db, attempt_id)
    except quiz_service.QuizError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return _attempt_detail(db, attempt)


@router.get("/progress", response_model=ProgressResponse)
def get_progress(db: Session = Depends(get_db)) -> ProgressResponse:
    progress = quiz_service.get_progress(db)
    accuracy = (
        round((progress.questions_correct / progress.questions_answered) * 100, 1)
        if progress.questions_answered
        else 0.0
    )
    return ProgressResponse(
        xp=progress.xp,
        level=progress.level,
        level_name=progress.level_name,
        questions_answered=progress.questions_answered,
        questions_correct=progress.questions_correct,
        quizzes_completed=progress.quizzes_completed,
        current_streak=progress.current_streak,
        accuracy=accuracy,
        last_chapter_id=progress.last_chapter_id,
        last_attempt_id=progress.last_attempt_id,
        next_level_xp=quiz_service.next_level_xp(progress.xp),
    )


def _chapter_summary(chapter) -> ChapterSummary:
    return ChapterSummary(
        id=chapter.id,
        number=chapter.number,
        title=chapter.title,
        start_page=chapter.start_page,
        end_page=chapter.end_page,
        paragraph_count=chapter.paragraph_count,
        question_count=chapter.question_count,
    )


def _attempt_summary(attempt) -> AttemptSummary:
    return AttemptSummary(
        id=attempt.id,
        mode=attempt.mode,
        title=attempt.title,
        subject_id=attempt.subject_id,
        chapter_id=attempt.chapter_id,
        question_count=attempt.question_count,
        difficulty=attempt.difficulty,
        time_limit_minutes=attempt.time_limit_minutes,
        status=attempt.status,
        score=attempt.score,
        correct_answers=attempt.correct_answers,
        wrong_answers=attempt.wrong_answers,
        duration_seconds=attempt.duration_seconds,
        started_at=attempt.started_at,
        finished_at=attempt.finished_at,
        answered_count=attempt_answered_count(attempt),
    )


def _attempt_detail(db: Session, attempt) -> AttemptDetail:
    answers = {answer.question_id: answer for answer in attempt.answers}
    reveal = attempt.status == "finished"
    questions = []
    for question in quiz_service.questions_for_attempt(attempt):
        answer = answers.get(question.id)
        questions.append(serialize_question(question, reveal=reveal or answer is not None, answer=answer))
    summary = _attempt_summary(attempt)
    return AttemptDetail(**summary.model_dump(), questions=questions)
