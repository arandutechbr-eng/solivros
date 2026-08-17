from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ParagraphType


class ParagraphCreate(BaseModel):
    content: str = ""
    type: ParagraphType = ParagraphType.PARAGRAPH
    confidence: float = Field(default=1.0, ge=0, le=1)
    order: int | None = Field(default=None, ge=0)


class ParagraphUpdate(BaseModel):
    content: str | None = None
    type: ParagraphType | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    order: int | None = Field(default=None, ge=0)


class ParagraphResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chapter_id: int
    content: str
    order: int
    type: ParagraphType
    confidence: float
    created_at: datetime
    updated_at: datetime
