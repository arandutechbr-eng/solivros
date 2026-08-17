from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enums import BookStatus
from app.schemas.book import BookCreate, BookDetailResponse, BookResponse, BookStatusResponse, BookUpdate
from app.schemas.chapter import ChapterCreate, ChapterResponse
from app.services import book_service, chapter_service, processing_service, publication_service, upload_service

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[BookResponse])
def list_books(db: Session = Depends(get_db)) -> list[BookResponse]:
    return book_service.list_books(db)


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    background_tasks: BackgroundTasks,
    title: str = Form(..., min_length=1, max_length=255),
    author: str = Form(""),
    isbn: str | None = Form(None),
    description: str | None = Form(None),
    pdf: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> BookResponse:
    _, destination = await upload_service.save_pdf_upload(pdf)
    payload = BookCreate(title=title, author=author, isbn=isbn, description=description)
    book = book_service.create_book(
        db,
        payload,
        original_filename=Path(pdf.filename or "upload.pdf").name,
        original_file_path=str(destination),
    )
    background_tasks.add_task(processing_service.process_book_task, book.id)
    return book


@router.get("/{book_id}", response_model=BookDetailResponse)
def get_book(book_id: int, db: Session = Depends(get_db)) -> BookDetailResponse:
    return publication_service.get_book_detail(db, book_id)


@router.get("/{book_id}/status", response_model=BookStatusResponse)
def get_book_status(book_id: int, db: Session = Depends(get_db)) -> BookStatusResponse:
    return book_service.get_book(db, book_id)


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)) -> BookResponse:
    return book_service.update_book(db, book_id, payload)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)) -> None:
    book_service.delete_book(db, book_id)


@router.post("/{book_id}/process", response_model=BookStatusResponse)
def process_book(
    book_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> BookStatusResponse:
    book = book_service.get_book(db, book_id)
    if not book.original_file_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Livro sem PDF original")
    if book.status == BookStatus.PROCESSING.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Livro já está em processamento")
    background_tasks.add_task(processing_service.process_book_task, book.id)
    return book


@router.get("/{book_id}/chapters", response_model=list[ChapterResponse])
def list_book_chapters(book_id: int, db: Session = Depends(get_db)) -> list[ChapterResponse]:
    return chapter_service.list_chapters(db, book_id)


@router.post("/{book_id}/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
def create_book_chapter(
    book_id: int, payload: ChapterCreate, db: Session = Depends(get_db)
) -> ChapterResponse:
    return chapter_service.create_chapter(db, book_id, payload)
