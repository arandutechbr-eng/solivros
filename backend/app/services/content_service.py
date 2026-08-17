from functools import lru_cache
from pathlib import Path

from app.services.content_parser import ContentBook, ContentChapter, ContentParagraph, parse_extracted_book
from app.services.storage_service import extracted_json_path

SOURCE_BOOK_ID = 5


class ContentNotFoundError(Exception):
    pass


@lru_cache(maxsize=1)
def load_book() -> ContentBook:
    path = extracted_json_path(SOURCE_BOOK_ID)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de conteúdo não encontrado: {path}")
    return parse_extracted_book(path, source_file=path.name)


def get_book() -> ContentBook:
    return load_book()


def list_chapters() -> list[ContentChapter]:
    return get_book().chapters


def get_chapter(chapter_id: str) -> ContentChapter:
    for chapter in list_chapters():
        if chapter.id == chapter_id:
            return chapter
    raise ContentNotFoundError(chapter_id)


def get_paragraph(paragraph_id: str) -> tuple[ContentChapter, ContentParagraph]:
    for chapter in list_chapters():
        for paragraph in chapter.paragraphs:
            if paragraph.id == paragraph_id:
                return chapter, paragraph
    raise ContentNotFoundError(paragraph_id)


def content_file_path() -> Path:
    return extracted_json_path(SOURCE_BOOK_ID)
