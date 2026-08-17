from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.book import BookResponse, ReaderBookResponse
from app.services import publication_service

router = APIRouter(prefix="/books", tags=["publication"])


@router.post("/{book_id}/approve", response_model=BookResponse)
def approve_book(book_id: int, db: Session = Depends(get_db)) -> BookResponse:
    return publication_service.approve_book(db, book_id)


@router.post("/{book_id}/publish", response_model=BookResponse)
def publish_book(book_id: int, db: Session = Depends(get_db)) -> BookResponse:
    return publication_service.publish_book(db, book_id)


@router.get("/{book_id}/reader", response_model=ReaderBookResponse)
def get_reader(book_id: int, db: Session = Depends(get_db)) -> ReaderBookResponse:
    return publication_service.get_reader_book(db, book_id)
