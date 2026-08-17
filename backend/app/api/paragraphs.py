from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.paragraph import ParagraphResponse, ParagraphUpdate
from app.services import paragraph_service

router = APIRouter(prefix="/paragraphs", tags=["paragraphs"])


@router.put("/{paragraph_id}", response_model=ParagraphResponse)
def update_paragraph(
    paragraph_id: int, payload: ParagraphUpdate, db: Session = Depends(get_db)
) -> ParagraphResponse:
    return paragraph_service.update_paragraph(db, paragraph_id, payload)


@router.delete("/{paragraph_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paragraph(paragraph_id: int, db: Session = Depends(get_db)) -> None:
    paragraph_service.delete_paragraph(db, paragraph_id)
