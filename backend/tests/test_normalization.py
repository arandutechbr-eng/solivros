from app.services.normalization_service import _join_hyphenated_words, normalize_pages


def test_join_hyphenated_words() -> None:
    assert _join_hyphenated_words("pala-\nvra extra") == "palavra extra"


def test_normalize_repeated_headers() -> None:
    pages = [
        {"page": 1, "text": "Header\n\nPrimeiro paragrafo.\n\nHeader"},
        {"page": 2, "text": "Header\n\nSegundo paragrafo.\n\nHeader"},
    ]
    normalized = normalize_pages(pages)
    assert "Header" not in normalized[0]["text"]
    assert "Primeiro paragrafo." in normalized[0]["text"]
    assert "Segundo paragrafo." in normalized[1]["text"]


def test_collapse_excessive_blank_lines() -> None:
    pages = [{"page": 1, "text": "A\n\n\n\nB"}]
    normalized = normalize_pages(pages)
    assert normalized[0]["text"] == "A\n\nB"
