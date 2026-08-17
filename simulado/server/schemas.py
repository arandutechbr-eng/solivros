from datetime import datetime

from pydantic import BaseModel, Field


class OptionPublic(BaseModel):
    letter: str
    text: str
    is_correct: bool | None = None


class SourceRef(BaseModel):
    chapter_id: str
    chapter: str
    page: int
    paragraph_id: str
    source_file: str


class QuestionPublic(BaseModel):
    id: int
    number: int
    exam_source: str
    prompt: str
    stimulus: str | None
    difficulty: str
    options: list[OptionPublic]
    source: SourceRef
    selected_letter: str | None = None
    is_correct: bool | None = None
    correct_letter: str | None = None
    explanation: str | None = None


class ChapterSummary(BaseModel):
    id: str
    number: int
    title: str
    start_page: int
    end_page: int
    paragraph_count: int
    question_count: int


class ParagraphPublic(BaseModel):
    id: str
    page: int
    order: int
    kind: str
    text: str
    question_number: int | None = None
    exam_source: str | None = None


class ChapterDetail(ChapterSummary):
    paragraphs: list[ParagraphPublic]


class ContentBook(BaseModel):
    source_file: str
    title: str
    subtitle: str
    page_count: int
    chapter_count: int
    paragraph_count: int
    question_count: int
    chapters: list[ChapterSummary]


class StartQuizRequest(BaseModel):
    mode: str = Field(pattern="^(quick|medium|full|chapter|custom)$")
    chapter_id: str | None = None
    count: int | None = Field(default=None, ge=1, le=100)
    difficulty: str = "all"
    time_limit_minutes: int | None = Field(default=None, ge=1, le=180)


class AnswerRequest(BaseModel):
    question_id: int
    selected_letter: str = Field(min_length=1, max_length=1)


class AttemptSummary(BaseModel):
    id: int
    mode: str
    title: str
    chapter_id: str | None
    question_count: int
    difficulty: str
    time_limit_minutes: int | None
    status: str
    score: int | None
    correct_answers: int
    wrong_answers: int
    duration_seconds: int | None
    started_at: datetime
    finished_at: datetime | None
    answered_count: int


class AttemptDetail(AttemptSummary):
    questions: list[QuestionPublic]


class AnswerFeedback(BaseModel):
    question_id: int
    selected_letter: str
    is_correct: bool
    correct_letter: str
    explanation: str
    source: SourceRef
    xp_earned: int


class ProgressResponse(BaseModel):
    xp: int
    level: int
    level_name: str
    questions_answered: int
    questions_correct: int
    quizzes_completed: int
    current_streak: int
    accuracy: float
    last_chapter_id: str | None
    last_attempt_id: int | None
    next_level_xp: int | None
