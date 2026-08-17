from hashlib import sha256
from pathlib import Path

from app.services.content_parser import parse_extracted_book
from app.services.storage_service import extracted_json_path


def test_parse_5_json_structure() -> None:
    path = extracted_json_path(5)
    assert path.exists()
    before = sha256(path.read_bytes()).hexdigest()

    book = parse_extracted_book(path, source_file="5.json")

    after = sha256(path.read_bytes()).hexdigest()
    assert before == after
    assert book.source_file == "5.json"
    assert book.page_count == 187
    assert len(book.chapters) >= 16
    assert book.paragraph_count > 500
    assert book.question_count == 500

    titles = [chapter.title.upper() for chapter in book.chapters]
    assert any("ORTOGRAFIA" in title for title in titles)
    assert any("ADJETIVO" in title for title in titles)
    assert any("INTERPRETAÇÃO DE TEXTOS" in title or "INTERPRETACAO DE TEXTOS" in title for title in titles)
    assert any("GABARITO" in title for title in titles)

    first = book.chapters[0]
    assert first.start_page >= 3
    assert first.paragraphs
    assert all(paragraph.id.startswith("p-") for paragraph in first.paragraphs)
    assert any(paragraph.kind == "question" and paragraph.question_number == 1 for paragraph in first.paragraphs)


def test_paragraph_ids_are_unique() -> None:
    book = parse_extracted_book(extracted_json_path(5), source_file="5.json")
    ids = [paragraph.id for chapter in book.chapters for paragraph in chapter.paragraphs]
    assert len(ids) == len(set(ids))


def test_content_file_is_not_overwritten() -> None:
    path: Path = extracted_json_path(5)
    original = path.read_bytes()
    parse_extracted_book(path)
    assert path.read_bytes() == original
