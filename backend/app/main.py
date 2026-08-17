import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.books import router as books_router
from app.api.chapters import router as chapters_router
from app.api.content import router as content_router
from app.api.extraction import router as extraction_router
from app.api.paragraphs import router as paragraphs_router
from app.api.publication import router as publication_router
from app.config import settings
from app.database import check_db_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Digital Publisher",
    description="Plataforma interna de digitalização e publicação de livros.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books_router, prefix="/api")
app.include_router(chapters_router, prefix="/api")
app.include_router(paragraphs_router, prefix="/api")
app.include_router(extraction_router, prefix="/api")
app.include_router(publication_router, prefix="/api")
app.include_router(content_router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "Digital Publisher API", "docs": "/docs"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "digital-publisher"}


@app.get("/health/db")
def health_db() -> dict[str, str]:
    try:
        check_db_connection()
    except Exception:
        logger.exception("Falha ao conectar no PostgreSQL")
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    return {"status": "ok", "database": "connected"}
