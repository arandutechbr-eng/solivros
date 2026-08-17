from pathlib import Path

from app.config import settings


def storage_root() -> Path:
    root = Path(settings.storage_path)
    root.mkdir(parents=True, exist_ok=True)
    return root


def original_dir() -> Path:
    path = storage_root() / "original"
    path.mkdir(parents=True, exist_ok=True)
    return path


def extracted_dir() -> Path:
    path = storage_root() / "extracted"
    path.mkdir(parents=True, exist_ok=True)
    return path


def processed_dir() -> Path:
    path = storage_root() / "processed"
    path.mkdir(parents=True, exist_ok=True)
    return path


def original_pdf_path(file_id: str) -> Path:
    return original_dir() / f"{file_id}.pdf"


def extracted_json_path(book_id: int) -> Path:
    return extracted_dir() / f"{book_id}.json"
