import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("DATABASE_URL", "postgresql://publisher:publisher@127.0.0.1:5432/publisher")
os.environ.setdefault("STORAGE_PATH", str(ROOT / "storage"))
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("OCR_ENABLED", "false")
