from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.book import Book
from app.models.chapter import Chapter
from app.models.enums import BookStatus
from app.models.paragraph import Paragraph
from app.schemas.book import BookDetailResponse, BookResponse, ReaderBookResponse
from app.services.book_service import BookNotFoundError, get_book


def get_book_detail(db: Session, book_id: int) -> BookDetailResponse:
    book = get_book(db, book_id)
    chapter_count = db.scalar(select(func.count(Chapter.id)).where(Chapter.book_id == book_id)) or 0
    paragraph_count = db.scalar(
        select(func.count(Paragraph.id))
        .join(Chapter, Paragraph.chapter_id == Chapter.id)
        .where(Chapter.book_id == book_id)
    ) or 0
    base = BookResponse.model_validate(book)
    return BookDetailResponse(**base.model_dump(), chapter_count=chapter_count, paragraph_count=paragraph_count)


def get_book_with_content(db: Session, book_id: int) -> Book:
    book = db.scalar(
        select(Book)
        .options(selectinload(Book.chapters).selectinload(Chapter.paragraphs))
        .where(Book.id == book_id)
    )
    if book is None:
        raise BookNotFoundError()
    return book


def approve_book(db: Session, book_id: int) -> Book:
    book = get_book(db, book_id)
    if book.status not in {BookStatus.REVIEW.value, BookStatus.STRUCTURED.value, BookStatus.APPROVED.value}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O livro precisa estar em revisão para ser aprovado",
        )
    book.status = BookStatus.APPROVED.value
    db.commit()
    db.refresh(book)
    return book


def publish_book(db: Session, book_id: int) -> Book:
    book = get_book_with_content(db, book_id)
    if book.status != BookStatus.APPROVED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aprove o livro antes de publicar",
        )
    _validate_publication(book)
    book.status = BookStatus.PUBLISHED.value
    db.commit()
    db.refresh(book)
    return book


def get_reader_book(db: Session, book_id: int) -> ReaderBookResponse:
    book = get_book_with_content(db, book_id)
    if book.status != BookStatus.PUBLISHED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Livro ainda não publicado",
        )
    return ReaderBookResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        status=BookStatus(book.status),
        chapters=book.chapters,
    )


def _validate_publication(book: Book) -> None:
    if not book.title.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Livro sem título")
    if not book.chapters:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Livro sem capítulos")
    has_content = any(
        paragraph.content.strip() for chapter in book.chapters for paragraph in chapter.paragraphs
    )
    if not has_content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Capítulos sem conteúdo")
