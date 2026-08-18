from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _in_docker() -> bool:
    return Path("/.dockerenv").exists()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", Path(".env")),
        extra="ignore",
    )

    database_url: str = "postgresql://publisher:publisher@postgres:5432/publisher"
    storage_path: str = "/app/storage"
    max_upload_size_mb: int = 200
    ocr_enabled: bool = True
    tesseract_lang: str = "por"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    def model_post_init(self, __context: object) -> None:
        if _in_docker():
            return
        storage = PROJECT_ROOT / "storage"
        storage.mkdir(parents=True, exist_ok=True)
        if self.storage_path.startswith("/app/") or not Path(self.storage_path).exists():
            self.storage_path = str(storage)
        if "@postgres:" in self.database_url or self.database_url.startswith("postgresql://publisher:publisher@postgres"):
            db_path = (storage / "publisher.db").resolve().as_posix()
            self.database_url = f"sqlite:///{db_path}"
        self.ocr_enabled = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
