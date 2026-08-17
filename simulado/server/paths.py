import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND = REPO_ROOT / "backend"
STORAGE = REPO_ROOT / "storage"
SOURCE_JSON = STORAGE / "extracted" / "5.json"
DATA_DIR = ROOT / "data"
QUESTIONS_JSON = DATA_DIR / "questions.json"
CONTENT_JSON = DATA_DIR / "content.json"
DATABASE_PATH = Path(os.environ.get("SIMULADO_DATABASE_PATH", STORAGE / "simulado-app.db"))

if BACKEND.exists() and str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
