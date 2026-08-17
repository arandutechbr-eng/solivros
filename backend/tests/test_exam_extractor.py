from hashlib import sha256
from pathlib import Path

from app.services.exam_extractor import _parse_gabarito, extract_exam_questions
from app.services.storage_service import extracted_json_path


def test_extracts_official_questions_and_gabarito() -> None:
    path = extracted_json_path(5)
    assert path.exists()
    before = sha256(path.read_bytes()).hexdigest()

    questions = extract_exam_questions(path)

    after = sha256(path.read_bytes()).hexdigest()
    assert before == after
    assert len(questions) == 500
    assert {question.number for question in questions} == set(range(1, 501))
    assert all(4 <= len(question.options) <= 5 for question in questions)
    assert all(sum(1 for option in question.options if option.is_correct) == 1 for question in questions)

    first = next(question for question in questions if question.number == 1)
    assert first.correct_letter == "C"
    assert first.source_file == "5.json"
    assert first.chapter_title


def test_gabarito_has_all_official_answers() -> None:
    import json

    path = extracted_json_path(5)
    payload = json.loads(path.read_text(encoding="utf-8"))
    gabarito = _parse_gabarito(payload["pages"])
    assert len(gabarito) == 500
    assert gabarito[1] == "C"
    assert gabarito[500] == "C"


def test_source_file_is_not_written(tmp_path: Path) -> None:
    path = extracted_json_path(5)
    original = path.read_bytes()
    extract_exam_questions(path)
    assert path.read_bytes() == original
    assert not (tmp_path / "5.json").exists()
