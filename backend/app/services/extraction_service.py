import json
from pathlib import Path
from typing import Any

import pymupdf

from app.services.storage_service import extracted_json_path


def extract_text_from_pdf(
    book_id: int,
    file_path: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    document = pymupdf.open(file_path)
    try:
        pages: list[dict[str, Any]] = []
        for index, page in enumerate(document, start=1):
            pages.append({"page": index, "text": page.get_text("text") or ""})
        payload: dict[str, Any] = {"book_id": book_id, "pages": pages}
        if extra:
            payload.update(extra)
    finally:
        document.close()

    output_path = extracted_json_path(book_id)
    _write_json(output_path, payload)
    return payload


def save_extracted_pages(book_id: int, pages: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {"book_id": book_id, "pages": pages}
    _write_json(extracted_json_path(book_id), payload)
    return payload


def load_extracted_pages(book_id: int) -> dict[str, Any]:
    path = extracted_json_path(book_id)
    if not path.exists():
        raise FileNotFoundError(f"Texto extraído não encontrado para o livro {book_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
