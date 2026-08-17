from dataclasses import dataclass

import pymupdf

TEXT_CHARS_PER_PAGE_THRESHOLD = 40


@dataclass(frozen=True)
class PdfAnalysis:
    page_count: int
    total_chars: int
    is_textual: bool
    sample_text: str


def analyze_pdf(file_path: str) -> PdfAnalysis:
    document = pymupdf.open(file_path)
    try:
        page_count = document.page_count
        total_chars = 0
        sample_parts: list[str] = []

        for index, page in enumerate(document):
            text = page.get_text("text") or ""
            total_chars += len(text.strip())
            if index < 3:
                sample_parts.append(text)

        average_chars = total_chars / page_count if page_count else 0
        is_textual = average_chars >= TEXT_CHARS_PER_PAGE_THRESHOLD
        return PdfAnalysis(
            page_count=page_count,
            total_chars=total_chars,
            is_textual=is_textual,
            sample_text="\n".join(sample_parts),
        )
    finally:
        document.close()
