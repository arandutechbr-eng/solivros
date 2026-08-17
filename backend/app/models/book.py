from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, utc_now
from app.models.enums import BookStatus

if TYPE_CHECKING:
    from app.models.chapter import Chapter


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    isbn: Mapped[str | None] = mapped_column(String(32), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=BookStatus.UPLOADED.value)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    original_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    raw_text_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    chapters: Mapped[list["Chapter"]] = relationship(
        "Chapter",
        back_populates="book",
        cascade="all, delete-orphan",
        order_by="Chapter.order",
    )
