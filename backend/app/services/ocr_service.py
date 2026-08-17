from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import BytesIO

import pymupdf
import pytesseract
from PIL import Image

from app.config import settings
from app.services.extraction_service import save_extracted_pages


@dataclass(frozen=True)
class OCRResult:
    text: str
    confidence: float


class OCRProvider(ABC):
    @abstractmethod
    def extract(self, image: bytes) -> OCRResult:
        raise NotImplementedError


class TesseractOCRProvider(OCRProvider):
    def __init__(self, language: str | None = None) -> None:
        self.language = language or settings.tesseract_lang

    def extract(self, image: bytes) -> OCRResult:
        pil_image = Image.open(BytesIO(image))
        text = pytesseract.image_to_string(pil_image, lang=self.language) or ""
        data = pytesseract.image_to_data(pil_image, lang=self.language, output_type=pytesseract.Output.DICT)
        confidences = [int(value) for value in data.get("conf", []) if str(value).isdigit() and int(value) >= 0]
        average = (sum(confidences) / len(confidences) / 100) if confidences else 0.5
        return OCRResult(text=text, confidence=max(0.0, min(average, 1.0)))


def get_ocr_provider() -> OCRProvider:
    return TesseractOCRProvider()


def extract_pdf_with_ocr(book_id: int, file_path: str, provider: OCRProvider | None = None) -> dict:
    ocr = provider or get_ocr_provider()
    document = pymupdf.open(file_path)
    pages: list[dict] = []
    try:
        for index, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
            result = ocr.extract(pixmap.tobytes("png"))
            pages.append(
                {
                    "page": index,
                    "text": result.text,
                    "ocr": True,
                    "confidence": round(result.confidence, 4),
                }
            )
    finally:
        document.close()

    payload = save_extracted_pages(book_id, pages)
    payload["ocr"] = True
    payload["is_textual"] = False
    return payload
