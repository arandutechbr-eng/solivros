from io import BytesIO

import pymupdf
from fastapi.testclient import TestClient

from app.main import app
from app.services.processing_service import process_book

client = TestClient(app)


def _pdf_bytes() -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "CAPITULO I\n\nEm um lugar da Mancha, de cujo nome nao quero lembrar-me, nao ha muito tempo que vivia um fidalgo.")
    page2 = document.new_page()
    page2.insert_text((72, 72), "CAPITULO II\n\nSaindo o nosso fidalgo de sua casa pela porta do corral, montou no seu rocim.")
    buffer = BytesIO()
    document.save(buffer)
    document.close()
    return buffer.getvalue()


def test_upload_create_update_and_publish(tmp_path, monkeypatch) -> None:
    from app.services import storage_service

    monkeypatch.setattr(storage_service, "original_dir", lambda: tmp_path)
    monkeypatch.setattr(storage_service, "extracted_dir", lambda: tmp_path)

    response = client.post(
        "/api/books",
        data={"title": "Livro de Teste", "author": "Autora"},
        files={"pdf": ("amostra.pdf", _pdf_bytes(), "application/pdf")},
    )
    assert response.status_code == 201
    book = response.json()
    book_id = book["id"]
    assert book["status"] == "UPLOADED"
    assert book["original_filename"] == "amostra.pdf"

    listed = client.get("/api/books")
    assert listed.status_code == 200
    assert any(item["id"] == book_id for item in listed.json())

    status = client.get(f"/api/books/{book_id}/status")
    assert status.status_code == 200

    from app.database import SessionLocal

    db = SessionLocal()
    try:
        processed = process_book(db, book_id)
        assert processed.status == "REVIEW"
        chapters = client.get(f"/api/books/{book_id}/chapters").json()
        assert len(chapters) >= 1
        paragraphs = client.get(f"/api/chapters/{chapters[0]['id']}/paragraphs").json()
        assert paragraphs
        updated = client.put(
            f"/api/paragraphs/{paragraphs[0]['id']}",
            json={"content": "Paragrafo revisado manualmente."},
        )
        assert updated.status_code == 200
        assert updated.json()["content"] == "Paragrafo revisado manualmente."

        approved = client.post(f"/api/books/{book_id}/approve")
        assert approved.status_code == 200
        published = client.post(f"/api/books/{book_id}/publish")
        assert published.status_code == 200
        assert published.json()["status"] == "PUBLISHED"
        reader = client.get(f"/api/books/{book_id}/reader")
        assert reader.status_code == 200
        assert reader.json()["title"] == "Livro de Teste"
    finally:
        db.close()
        client.delete(f"/api/books/{book_id}")
