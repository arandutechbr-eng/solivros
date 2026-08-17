from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BookStatus, ParagraphType


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(default="", max_length=255)
    isbn: str | None = Field(default=None, max_length=32)
    description: str | None = None


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, max_length=255)
    isbn: str | None = Field(default=None, max_length=32)
    description: str | None = None


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    isbn: str | None
    description: str | None
    status: BookStatus
    original_filename: str | None
    raw_text_path: str | None
    page_count: int | None
    created_at: datetime
    updated_at: datetime


class BookDetailResponse(BookResponse):
    chapter_count: int
    paragraph_count: int


class BookStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: BookStatus
    page_count: int | None
    raw_text_path: str | None


class ReaderParagraph(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    type: ParagraphType
    order: int
    confidence: float


class ReaderChapter(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    number: int | None
    order: int
    paragraphs: list[ReaderParagraph]


class ReaderBookResponse(BaseModel):
    id: int
    title: str
    author: str
    status: BookStatus
    chapters: list[ReaderChapter]
