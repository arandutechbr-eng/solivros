from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.enums import BookStatus
from app.schemas.book import BookCreate, BookUpdate


class BookNotFoundError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")


def list_books(db: Session) -> list[Book]:
    return list(db.scalars(select(Book).order_by(Book.created_at.desc())).all())


def get_book(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise BookNotFoundError()
    return book


def create_book(
    db: Session,
    payload: BookCreate,
    original_filename: str | None = None,
    original_file_path: str | None = None,
) -> Book:
    book = Book(
        title=payload.title.strip(),
        author=payload.author.strip(),
        isbn=payload.isbn.strip() if payload.isbn else None,
        description=payload.description,
        status=BookStatus.UPLOADED.value,
        original_filename=original_filename,
        original_file_path=original_file_path,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(db: Session, book_id: int, payload: BookUpdate) -> Book:
    book = get_book(db, book_id)
    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"] is not None:
        data["title"] = data["title"].strip()
    if "author" in data and data["author"] is not None:
        data["author"] = data["author"].strip()
    if "isbn" in data and data["isbn"] is not None:
        data["isbn"] = data["isbn"].strip()
    for field, value in data.items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> None:
    book = get_book(db, book_id)
    db.delete(book)
    db.commit()
