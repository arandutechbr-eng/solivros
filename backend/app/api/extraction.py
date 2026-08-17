from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import book_service, extraction_service

router = APIRouter(tags=["extraction"])


@router.get("/books/{book_id}/extracted")
def get_extracted_text(book_id: int, db: Session = Depends(get_db)) -> dict:
    book_service.get_book(db, book_id)
    try:
        return extraction_service.load_extracted_pages(book_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
