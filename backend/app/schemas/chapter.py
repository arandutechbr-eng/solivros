from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChapterCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    number: int | None = None
    order: int | None = Field(default=None, ge=0)


class ChapterUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    number: int | None = None
    order: int | None = Field(default=None, ge=0)


class ChapterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    number: int | None
    title: str
    order: int
    created_at: datetime
    updated_at: datetime
