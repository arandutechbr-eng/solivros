from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OptionRecord:
    letter: str
    text: str
    is_correct: bool


@dataclass(frozen=True)
class QuestionRecord:
    id: int
    number: int
    exam_source: str
    prompt: str
    stimulus: str | None
    explanation: str
    difficulty: str
    chapter_id: str
    chapter_title: str
    page: int
    paragraph_id: str
    correct_letter: str
    source_file: str
    subject_id: str
    options: tuple[OptionRecord, ...]


@dataclass
class ParagraphRecord:
    id: str
    page: int
    order: int
    kind: str
    text: str
    question_number: int | None = None
    exam_source: str | None = None


@dataclass
class ChapterRecord:
    id: str
    number: int
    title: str
    start_page: int
    end_page: int
    paragraphs: list[ParagraphRecord] = field(default_factory=list)

    @property
    def paragraph_count(self) -> int:
        return len(self.paragraphs)

    @property
    def question_count(self) -> int:
        return sum(1 for paragraph in self.paragraphs if paragraph.kind == "question")


@dataclass
class BookRecord:
    source_file: str
    title: str
    subtitle: str
    page_count: int
    question_count: int
    subject_id: str
    chapters: list[ChapterRecord]
