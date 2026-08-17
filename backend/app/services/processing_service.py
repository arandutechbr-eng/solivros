import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, utc_now
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.enums import BookStatus
from app.models.paragraph import Paragraph
from app.services import extraction_service, normalization_service, ocr_service, pdf_service, structure_service
from app.services.book_service import get_book

logger = logging.getLogger(__name__)


def process_book(db: Session, book_id: int) -> Book:
    book = get_book(db, book_id)
    if not book.original_file_path:
        book.status = BookStatus.ERROR.value
        db.commit()
        raise ValueError("Livro sem arquivo PDF original")

    book.status = BookStatus.PROCESSING.value
    db.commit()

    try:
        analysis = pdf_service.analyze_pdf(book.original_file_path)
        if analysis.is_textual:
            extracted = extraction_service.extract_text_from_pdf(
                book.id,
                book.original_file_path,
                extra={
                    "is_textual": True,
                    "ocr": False,
                    "page_count": analysis.page_count,
                    "total_chars": analysis.total_chars,
                },
            )
        elif settings.ocr_enabled:
            extracted = ocr_service.extract_pdf_with_ocr(book.id, book.original_file_path)
            extracted["page_count"] = analysis.page_count
        else:
            extracted = extraction_service.extract_text_from_pdf(
                book.id,
                book.original_file_path,
                extra={
                    "is_textual": False,
                    "ocr": False,
                    "page_count": analysis.page_count,
                    "total_chars": analysis.total_chars,
                },
            )

        book.raw_text_path = f"extracted/{book.id}.json"
        book.page_count = analysis.page_count
        book.status = BookStatus.EXTRACTED.value
        book.updated_at = utc_now()
        db.commit()

        normalized_pages = normalization_service.normalize_pages(extracted["pages"])
        chapters = structure_service.structure_pages(normalized_pages)
        _replace_book_structure(db, book, chapters)

        book.status = BookStatus.STRUCTURED.value
        book.updated_at = utc_now()
        db.commit()

        book.status = BookStatus.REVIEW.value
        book.updated_at = utc_now()
        db.commit()
        db.refresh(book)
        logger.info("Livro %s estruturado com %s capítulos", book.id, len(chapters))
        return book
    except Exception:
        logger.exception("Falha ao processar livro %s", book_id)
        book.status = BookStatus.ERROR.value
        book.updated_at = utc_now()
        db.commit()
        raise


def process_book_task(book_id: int) -> None:
    db = SessionLocal()
    try:
        process_book(db, book_id)
    except Exception:
        logger.exception("Background task falhou para o livro %s", book_id)
    finally:
        db.close()


def _replace_book_structure(
    db: Session,
    book: Book,
    chapters: list[structure_service.StructuredChapter],
) -> None:
    book.chapters.clear()
    db.flush()
    for chapter_data in chapters:
        chapter = Chapter(
            book_id=book.id,
            title=chapter_data.title,
            number=chapter_data.number,
            order=chapter_data.order,
        )
        for paragraph_data in chapter_data.paragraphs:
            chapter.paragraphs.append(
                Paragraph(
                    content=paragraph_data.content,
                    type=paragraph_data.type.value,
                    confidence=paragraph_data.confidence,
                    order=paragraph_data.order,
                )
            )
        db.add(chapter)
    db.flush()
