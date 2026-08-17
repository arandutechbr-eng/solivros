import re
from collections import Counter
from typing import Any


def normalize_pages(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = [_normalize_page_text(page.get("text") or "") for page in pages]
    headers, footers = _detect_repeated_lines(normalized)

    result: list[dict[str, Any]] = []
    for page, text in zip(pages, normalized, strict=True):
        cleaned = _strip_repeated_edges(text, headers, footers)
        item = dict(page)
        item["text"] = cleaned
        result.append(item)
    return result


def _normalize_page_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _join_hyphenated_words(text)
    lines = [_normalize_spaces(line) for line in text.split("\n")]
    lines = _collapse_empty_lines(lines)
    return "\n".join(lines).strip()


def _normalize_spaces(line: str) -> str:
    return re.sub(r"[ \t]+", " ", line).strip()


def _collapse_empty_lines(lines: list[str]) -> list[str]:
    collapsed: list[str] = []
    empty_run = 0
    for line in lines:
        if line == "":
            empty_run += 1
            if empty_run <= 1:
                collapsed.append("")
            continue
        empty_run = 0
        collapsed.append(line)
    return collapsed


def _join_hyphenated_words(text: str) -> str:
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def _detect_repeated_lines(pages: list[str]) -> tuple[set[str], set[str]]:
    if len(pages) < 2:
        return set(), set()

    header_counter: Counter[str] = Counter()
    footer_counter: Counter[str] = Counter()
    for page in pages:
        lines = [line for line in page.split("\n") if line]
        if not lines:
            continue
        header_counter[lines[0]] += 1
        footer_counter[lines[-1]] += 1

    threshold = max(2, int(len(pages) * 0.5))
    headers = {line for line, count in header_counter.items() if count >= threshold and len(line) <= 80}
    footers = {line for line, count in footer_counter.items() if count >= threshold and len(line) <= 80}
    return headers, footers


def _strip_repeated_edges(text: str, headers: set[str], footers: set[str]) -> str:
    lines = text.split("\n")
    if lines and lines[0] in headers:
        lines = lines[1:]
    if lines and lines[-1] in footers:
        lines = lines[:-1]
    return "\n".join(lines).strip()
