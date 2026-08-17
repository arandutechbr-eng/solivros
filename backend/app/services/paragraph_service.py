from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.paragraph import Paragraph
from app.schemas.paragraph import ParagraphCreate, ParagraphUpdate
from app.services.chapter_service import get_chapter


class ParagraphNotFoundError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Parágrafo não encontrado")


def list_paragraphs(db: Session, chapter_id: int) -> list[Paragraph]:
    get_chapter(db, chapter_id)
    stmt = select(Paragraph).where(Paragraph.chapter_id == chapter_id).order_by(Paragraph.order, Paragraph.id)
    return list(db.scalars(stmt).all())


def get_paragraph(db: Session, paragraph_id: int) -> Paragraph:
    paragraph = db.get(Paragraph, paragraph_id)
    if paragraph is None:
        raise ParagraphNotFoundError()
    return paragraph


def _next_paragraph_order(db: Session, chapter_id: int) -> int:
    current = db.scalar(select(func.max(Paragraph.order)).where(Paragraph.chapter_id == chapter_id))
    return 0 if current is None else current + 1


def create_paragraph(db: Session, chapter_id: int, payload: ParagraphCreate) -> Paragraph:
    get_chapter(db, chapter_id)
    order = payload.order if payload.order is not None else _next_paragraph_order(db, chapter_id)
    paragraph = Paragraph(
        chapter_id=chapter_id,
        content=payload.content,
        type=payload.type.value,
        confidence=payload.confidence,
        order=order,
    )
    db.add(paragraph)
    db.commit()
    db.refresh(paragraph)
    return paragraph


def update_paragraph(db: Session, paragraph_id: int, payload: ParagraphUpdate) -> Paragraph:
    paragraph = get_paragraph(db, paragraph_id)
    data = payload.model_dump(exclude_unset=True)
    if "type" in data and data["type"] is not None:
        data["type"] = data["type"].value
    for field, value in data.items():
        setattr(paragraph, field, value)
    db.commit()
    db.refresh(paragraph)
    return paragraph


def delete_paragraph(db: Session, paragraph_id: int) -> None:
    paragraph = get_paragraph(db, paragraph_id)
    db.delete(paragraph)
    db.commit()
