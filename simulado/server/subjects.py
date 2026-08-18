from dataclasses import dataclass
from pathlib import Path

from .paths import DATA_DIR, STORAGE


@dataclass(frozen=True)
class Subject:
    id: str
    book_id: int
    filename: str
    title: str
    subtitle: str

    @property
    def source_path(self) -> Path:
        return STORAGE / "extracted" / self.filename

    @property
    def data_dir(self) -> Path:
        return DATA_DIR / self.id

    @property
    def questions_path(self) -> Path:
        return self.data_dir / "questions.json"

    @property
    def content_path(self) -> Path:
        return self.data_dir / "content.json"


SUBJECTS: tuple[Subject, ...] = (
    Subject(
        id="portugues",
        book_id=5,
        filename="5.json",
        title="Língua Portuguesa",
        subtitle="Caderno Transpetro — Conhecimentos Gerais",
    ),
    Subject(
        id="matematica",
        book_id=1,
        filename="1.json",
        title="Matemática",
        subtitle="Caderno Transpetro — Conhecimentos Gerais",
    ),
    Subject(
        id="ingles",
        book_id=2,
        filename="2.json",
        title="Língua Inglesa",
        subtitle="Caderno Transpetro — Conhecimentos Gerais",
    ),
)

DEFAULT_SUBJECT_ID = "portugues"


def get_subject(subject_id: str | None) -> Subject:
    wanted = (subject_id or DEFAULT_SUBJECT_ID).strip().lower()
    for subject in SUBJECTS:
        if subject.id == wanted:
            return subject
    raise KeyError(wanted)
