from __future__ import annotations

import json
import random
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .catalog import GUEST_USER_ID, load_questions, question_map
from .models import QuizAnswer, QuizAttempt, UserProgress
from .records import QuestionRecord
from .subjects import SUBJECTS, get_subject

MODE_COUNTS = {"quick": 10, "medium": 20, "full": 50, "chapter": 15}
MODE_TITLES = {
    "quick": "Simulado rápido",
    "medium": "Simulado médio",
    "full": "Simulado completo",
    "chapter": "Simulado por capítulo",
    "custom": "Simulado personalizado",
}
LEVELS = (
    (0, 1, "Iniciante"),
    (200, 2, "Estudante"),
    (500, 3, "Aprendiz"),
    (1000, 4, "Especialista"),
    (2000, 5, "Mestre"),
)


class QuizError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def start_quiz(
    db: Session,
    *,
    mode: str,
    subject_id: str | None,
    chapter_id: str | None,
    count: int | None,
    difficulty: str,
    time_limit_minutes: int | None,
) -> QuizAttempt:
    try:
        subject = _resolve_subject(subject_id, chapter_id)
    except KeyError as exc:
        raise QuizError("Matéria não encontrada.", 404) from exc

    pool = [
        question
        for question in load_questions(subject.id)
        if (not chapter_id or question.chapter_id == chapter_id)
        and (not difficulty or difficulty == "all" or question.difficulty == difficulty)
    ]
    if not pool:
        raise QuizError("Não há questões oficiais para esse recorte.", 404)

    wanted = count or MODE_COUNTS.get(mode, 10)
    selected = random.sample(pool, k=min(wanted, len(pool)))
    title = f"{subject.title} — {MODE_TITLES.get(mode, 'Simulado')}"
    if chapter_id and selected:
        title = f"{title} — {selected[0].chapter_title}"

    attempt = QuizAttempt(
        mode=mode,
        title=title,
        subject_id=subject.id,
        chapter_id=chapter_id,
        question_count=len(selected),
        difficulty=difficulty or "all",
        time_limit_minutes=time_limit_minutes,
        question_ids=json.dumps([question.id for question in selected]),
        status="in_progress",
    )
    db.add(attempt)
    db.flush()
    progress = db.get(UserProgress, GUEST_USER_ID)
    if progress is not None:
        progress.last_chapter_id = chapter_id or selected[0].chapter_id
        progress.last_attempt_id = attempt.id
    db.commit()
    db.refresh(attempt)
    return attempt


def get_attempt(db: Session, attempt_id: int) -> QuizAttempt:
    attempt = db.get(QuizAttempt, attempt_id)
    if attempt is None:
        raise QuizError("Simulado não encontrado.", 404)
    return attempt


def list_attempts(db: Session) -> list[QuizAttempt]:
    return db.query(QuizAttempt).order_by(QuizAttempt.started_at.desc()).all()


def questions_for_attempt(attempt: QuizAttempt) -> list[QuestionRecord]:
    ids = json.loads(attempt.question_ids)
    found = question_map()
    return [found[question_id] for question_id in ids if question_id in found]


def answer_question(db: Session, attempt_id: int, question_id: int, selected_letter: str) -> tuple[QuizAnswer, int]:
    attempt = get_attempt(db, attempt_id)
    if attempt.status != "in_progress":
        raise QuizError("Este simulado já foi finalizado.")

    ids = json.loads(attempt.question_ids)
    if question_id not in ids:
        raise QuizError("Questão não pertence a este simulado.", 404)

    question = question_map().get(question_id)
    if question is None:
        raise QuizError("Questão não encontrada.", 404)

    letter = selected_letter.strip().upper()
    if letter not in {option.letter for option in question.options}:
        raise QuizError("Alternativa inválida.")

    existing = (
        db.query(QuizAnswer)
        .filter(QuizAnswer.attempt_id == attempt.id, QuizAnswer.question_id == question_id)
        .one_or_none()
    )
    if existing is not None:
        raise QuizError("Esta questão já foi respondida.")

    is_correct = letter == question.correct_letter
    record = QuizAnswer(
        attempt_id=attempt.id,
        question_id=question_id,
        selected_letter=letter,
        is_correct=is_correct,
    )
    db.add(record)

    progress = db.get(UserProgress, GUEST_USER_ID)
    xp_earned = 0
    if progress is not None:
        progress.questions_answered += 1
        if is_correct:
            progress.questions_correct += 1
            progress.xp += 10
            xp_earned = 10
        _apply_level(progress)

    db.commit()
    db.refresh(record)
    return record, xp_earned


def finish_quiz(db: Session, attempt_id: int) -> QuizAttempt:
    attempt = get_attempt(db, attempt_id)
    if attempt.status == "finished":
        return attempt

    answers = {answer.question_id: answer for answer in attempt.answers}
    ids = json.loads(attempt.question_ids)
    correct = sum(1 for question_id in ids if answers.get(question_id) and answers[question_id].is_correct)
    answered = sum(1 for question_id in ids if question_id in answers)
    wrong = answered - correct
    score = round((correct / len(ids)) * 100) if ids else 0
    now = datetime.now(timezone.utc)
    started = attempt.started_at
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)

    attempt.status = "finished"
    attempt.correct_answers = correct
    attempt.wrong_answers = wrong
    attempt.score = score
    attempt.finished_at = now
    attempt.duration_seconds = max(0, int((now - started).total_seconds()))

    progress = db.get(UserProgress, GUEST_USER_ID)
    if progress is not None:
        progress.quizzes_completed += 1
        progress.xp += 50
        if score == 100:
            progress.xp += 100
        if score >= 70:
            progress.current_streak += 1
        else:
            progress.current_streak = 0
        progress.last_attempt_id = attempt.id
        if attempt.chapter_id:
            progress.last_chapter_id = attempt.chapter_id
        _apply_level(progress)

    db.commit()
    db.refresh(attempt)
    return attempt


def get_progress(db: Session) -> UserProgress:
    progress = db.get(UserProgress, GUEST_USER_ID)
    if progress is None:
        progress = UserProgress(user_id=GUEST_USER_ID)
        db.add(progress)
        db.commit()
        db.refresh(progress)
    return progress


def _apply_level(progress: UserProgress) -> None:
    current = LEVELS[0]
    for threshold, level, name in LEVELS:
        if progress.xp >= threshold:
            current = (threshold, level, name)
    progress.level = current[1]
    progress.level_name = current[2]


def _resolve_subject(subject_id: str | None, chapter_id: str | None):
    if chapter_id:
        for subject in SUBJECTS:
            if chapter_id.startswith(f"{subject.id}-"):
                return subject
    return get_subject(subject_id)


def next_level_xp(xp: int) -> int | None:
    for threshold, _, _ in LEVELS:
        if xp < threshold:
            return threshold
    return None
