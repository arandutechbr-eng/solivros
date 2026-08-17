from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chapter import ChapterResponse, ChapterUpdate
from app.schemas.paragraph import ParagraphCreate, ParagraphResponse
from app.services import chapter_service, paragraph_service

router = APIRouter(tags=["chapters"])


@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)) -> ChapterResponse:
    return chapter_service.get_chapter(db, chapter_id)


@router.put("/chapters/{chapter_id}", response_model=ChapterResponse)
def update_chapter(
    chapter_id: int, payload: ChapterUpdate, db: Session = Depends(get_db)
) -> ChapterResponse:
    return chapter_service.update_chapter(db, chapter_id, payload)


@router.delete("/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chapter(chapter_id: int, db: Session = Depends(get_db)) -> None:
    chapter_service.delete_chapter(db, chapter_id)


@router.get("/chapters/{chapter_id}/paragraphs", response_model=list[ParagraphResponse])
def list_chapter_paragraphs(chapter_id: int, db: Session = Depends(get_db)) -> list[ParagraphResponse]:
    return paragraph_service.list_paragraphs(db, chapter_id)


@router.post(
    "/chapters/{chapter_id}/paragraphs",
    response_model=ParagraphResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_chapter_paragraph(
    chapter_id: int, payload: ParagraphCreate, db: Session = Depends(get_db)
) -> ParagraphResponse:
    return paragraph_service.create_paragraph(db, chapter_id, payload)
