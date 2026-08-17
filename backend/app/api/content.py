from fastapi import APIRouter, HTTPException, status

from app.schemas.content import (
    ContentBookResponse,
    ContentChapterDetail,
    ContentChapterSummary,
    ContentParagraphResponse,
)
from app.services import content_service
from app.services.content_parser import ContentChapter

router = APIRouter(prefix="/content", tags=["content"])


@router.get("", response_model=ContentBookResponse)
def get_content() -> ContentBookResponse:
    book = content_service.get_book()
    return ContentBookResponse(
        source_file=book.source_file,
        book_id=book.book_id,
        title=book.title,
        subtitle=book.subtitle,
        page_count=book.page_count,
        chapter_count=len(book.chapters),
        paragraph_count=book.paragraph_count,
        question_count=book.question_count,
        chapters=[_chapter_summary(chapter) for chapter in book.chapters],
    )


@router.get("/chapters", response_model=list[ContentChapterSummary])
def list_chapters() -> list[ContentChapterSummary]:
    return [_chapter_summary(chapter) for chapter in content_service.list_chapters()]


@router.get("/chapters/{chapter_id}", response_model=ContentChapterDetail)
def get_chapter(chapter_id: str) -> ContentChapterDetail:
    try:
        chapter = content_service.get_chapter(chapter_id)
    except content_service.ContentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capítulo não encontrado") from exc
    summary = _chapter_summary(chapter)
    return ContentChapterDetail(
        **summary.model_dump(),
        paragraphs=[ContentParagraphResponse.model_validate(paragraph) for paragraph in chapter.paragraphs],
    )


@router.get("/paragraphs/{paragraph_id}", response_model=ContentParagraphResponse)
def get_paragraph(paragraph_id: str) -> ContentParagraphResponse:
    try:
        _, paragraph = content_service.get_paragraph(paragraph_id)
    except content_service.ContentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parágrafo não encontrado") from exc
    return ContentParagraphResponse.model_validate(paragraph)


def _chapter_summary(chapter: ContentChapter) -> ContentChapterSummary:
    return ContentChapterSummary(
        id=chapter.id,
        number=chapter.number,
        title=chapter.title,
        start_page=chapter.start_page,
        end_page=chapter.end_page,
        paragraph_count=chapter.paragraph_count,
        question_count=chapter.question_count,
    )
