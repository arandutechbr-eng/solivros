from pathlib import Path

import pymupdf

from app.services.extraction_service import extract_text_from_pdf
from app.services.pdf_service import analyze_pdf


def _create_textual_pdf(path: Path) -> None:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "CAPITULO I\n\nEm um lugar da Mancha, de cujo nome nao quero lembrar-me, nao ha muito tempo que vivia um fidalgo dos de lanca em cabidal.",
    )
    document.save(path)
    document.close()


def test_detects_textual_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "textual.pdf"
    _create_textual_pdf(pdf_path)
    analysis = analyze_pdf(str(pdf_path))
    assert analysis.page_count == 1
    assert analysis.is_textual is True
    assert analysis.total_chars > 20


def test_extracts_text_by_page(tmp_path: Path, monkeypatch) -> None:
    pdf_path = tmp_path / "textual.pdf"
    _create_textual_pdf(pdf_path)
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    from app.services import storage_service

    monkeypatch.setattr(storage_service, "storage_root", lambda: tmp_path)
    extracted = extract_text_from_pdf(99, str(pdf_path))
    assert extracted["book_id"] == 99
    assert extracted["pages"][0]["page"] == 1
    assert "Mancha" in extracted["pages"][0]["text"]
