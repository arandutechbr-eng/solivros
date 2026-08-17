from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.chapter import Chapter
from app.schemas.chapter import ChapterCreate, ChapterUpdate
from app.services.book_service import get_book


class ChapterNotFoundError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Capítulo não encontrado")


def list_chapters(db: Session, book_id: int) -> list[Chapter]:
    get_book(db, book_id)
    stmt = select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.order, Chapter.id)
    return list(db.scalars(stmt).all())


def get_chapter(db: Session, chapter_id: int) -> Chapter:
    chapter = db.get(Chapter, chapter_id)
    if chapter is None:
        raise ChapterNotFoundError()
    return chapter


def _next_chapter_order(db: Session, book_id: int) -> int:
    current = db.scalar(select(func.max(Chapter.order)).where(Chapter.book_id == book_id))
    return 0 if current is None else current + 1


def create_chapter(db: Session, book_id: int, payload: ChapterCreate) -> Chapter:
    get_book(db, book_id)
    order = payload.order if payload.order is not None else _next_chapter_order(db, book_id)
    chapter = Chapter(
        book_id=book_id,
        title=payload.title.strip(),
        number=payload.number,
        order=order,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


def update_chapter(db: Session, chapter_id: int, payload: ChapterUpdate) -> Chapter:
    chapter = get_chapter(db, chapter_id)
    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"] is not None:
        data["title"] = data["title"].strip()
    for field, value in data.items():
        setattr(chapter, field, value)
    db.commit()
    db.refresh(chapter)
    return chapter


def delete_chapter(db: Session, chapter_id: int) -> None:
    chapter = get_chapter(db, chapter_id)
    db.delete(chapter)
    db.commit()
