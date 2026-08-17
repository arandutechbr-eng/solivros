import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api import router
from .database import init_db

DIST_DIR = Path(__file__).resolve().parents[1] / "dist"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


def _cors_origins() -> list[str]:
    raw = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5174,http://127.0.0.1:5174",
    )
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    extra = os.environ.get("VERCEL_PROJECT_PRODUCTION_URL")
    if extra:
        origins.append(f"https://{extra}")
    preview = os.environ.get("VERCEL_URL")
    if preview:
        origins.append(f"https://{preview}")
    return origins


app = FastAPI(
    title="Solivros Simulados",
    description="Plataforma de simulados com as questões oficiais do caderno 5.json.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "solivros-simulados"}


def _attach_frontend() -> None:
    if not (DIST_DIR / "index.html").exists():
        return
    if hasattr(app, "frontend"):
        app.frontend("/", directory=str(DIST_DIR))
        return
    assets = DIST_DIR / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        candidate = DIST_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(DIST_DIR / "index.html")


_attach_frontend()
