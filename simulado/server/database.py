import os
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool

from .paths import DATABASE_PATH


def _database_url() -> str:
    url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
    )
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    if os.environ.get("VERCEL"):
        return "sqlite:////tmp/simulado.db"
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DATABASE_PATH}"


def _connect_args(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


DATABASE_URL = _database_url()
IS_POSTGRES = DATABASE_URL.startswith("postgresql")

_engine_kwargs: dict = {
    "connect_args": _connect_args(DATABASE_URL),
    "pool_pre_ping": True,
}
if os.environ.get("VERCEL") or IS_POSTGRES:
    _engine_kwargs["poolclass"] = NullPool

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


_ready = False


def _ensure_subject_column() -> None:
    with engine.begin() as connection:
        if DATABASE_URL.startswith("sqlite"):
            columns = [row[1] for row in connection.execute(text("PRAGMA table_info(quiz_attempts)"))]
            if "subject_id" not in columns:
                connection.execute(text("ALTER TABLE quiz_attempts ADD COLUMN subject_id VARCHAR(32)"))
        elif IS_POSTGRES:
            connection.execute(
                text("ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS subject_id VARCHAR(32)")
            )


def init_db() -> None:
    global _ready
    if _ready:
        return
    from .catalog import ensure_catalog

    Base.metadata.create_all(bind=engine)
    _ensure_subject_column()
    db = SessionLocal()
    try:
        ensure_catalog(db)
    finally:
        db.close()
    _ready = True


def get_db() -> Generator[Session, None, None]:
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
