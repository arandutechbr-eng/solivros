from enum import Enum


class BookStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    EXTRACTED = "EXTRACTED"
    STRUCTURED = "STRUCTURED"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    ERROR = "ERROR"


class ParagraphType(str, Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    SUBHEADING = "subheading"
    QUOTE = "quote"
    FOOTNOTE = "footnote"
    CAPTION = "caption"
