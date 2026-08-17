from pydantic import BaseModel, ConfigDict


class ContentParagraphResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    page: int
    order: int
    kind: str
    text: str
    question_number: int | None = None
    exam_source: str | None = None


class ContentChapterSummary(BaseModel):
    id: str
    number: int
    title: str
    start_page: int
    end_page: int
    paragraph_count: int
    question_count: int


class ContentChapterDetail(ContentChapterSummary):
    paragraphs: list[ContentParagraphResponse]


class ContentBookResponse(BaseModel):
    source_file: str
    book_id: int | None
    title: str
    subtitle: str
    page_count: int
    chapter_count: int
    paragraph_count: int
    question_count: int
    chapters: list[ContentChapterSummary]
