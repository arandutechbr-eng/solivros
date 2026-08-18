from fastapi.testclient import TestClient

from server.main import app


def test_content_and_quick_quiz_flow() -> None:
    client = TestClient(app)
    content = client.get("/api/content", params={"subject": "portugues"})
    assert content.status_code == 200
    book = content.json()
    assert book["source_file"] == "5.json"
    assert book["subject_id"] == "portugues"
    assert book["question_count"] == 500
    assert book["chapters"]
    assert book["chapters"][0]["id"].startswith("portugues-")

    chapter_id = book["chapters"][0]["id"]
    detail = client.get(f"/api/content/chapters/{chapter_id}")
    assert detail.status_code == 200
    assert detail.json()["paragraphs"]

    started = client.post("/api/quizzes/start", json={"mode": "quick", "subject_id": "portugues"})
    assert started.status_code == 200
    attempt = started.json()
    assert attempt["question_count"] == 10
    question = attempt["questions"][0]
    assert question["correct_letter"] is None
    assert all(option["is_correct"] is None for option in question["options"])

    letter = question["options"][0]["letter"]
    answered = client.post(
        f"/api/attempts/{attempt['id']}/answer",
        json={"question_id": question["id"], "selected_letter": letter},
    )
    assert answered.status_code == 200
    feedback = answered.json()
    assert feedback["correct_letter"] in {"A", "B", "C", "D", "E"}
    assert "5.json" in feedback["explanation"]

    finished = client.post(f"/api/attempts/{attempt['id']}/finish")
    assert finished.status_code == 200
    assert finished.json()["status"] == "finished"

    progress = client.get("/api/progress")
    assert progress.status_code == 200
    assert progress.json()["questions_answered"] >= 1


def test_subjects_and_math_english_quizzes() -> None:
    client = TestClient(app)
    subjects = client.get("/api/subjects")
    assert subjects.status_code == 200
    items = {item["id"]: item for item in subjects.json()}
    assert set(items) == {"portugues", "matematica", "ingles"}
    assert items["portugues"]["source_file"] == "5.json"
    assert items["matematica"]["source_file"] == "1.json"
    assert items["ingles"]["source_file"] == "2.json"
    assert items["matematica"]["question_count"] > 0
    assert items["ingles"]["question_count"] > 0

    math_content = client.get("/api/content", params={"subject": "matematica"})
    assert math_content.status_code == 200
    assert math_content.json()["chapters"][0]["id"].startswith("matematica-")

    math_quiz = client.post("/api/quizzes/start", json={"mode": "quick", "subject_id": "matematica"})
    assert math_quiz.status_code == 200
    assert math_quiz.json()["subject_id"] == "matematica"
    assert math_quiz.json()["question_count"] == 10

    english_quiz = client.post("/api/quizzes/start", json={"mode": "quick", "subject_id": "ingles"})
    assert english_quiz.status_code == 200
    assert english_quiz.json()["subject_id"] == "ingles"
    assert english_quiz.json()["questions"][0]["id"] >= 20000


def test_reading_passage_is_attached_to_question() -> None:
    from server.catalog import load_questions

    question = next(item for item in load_questions("portugues") if item.number == 463)
    assert question.stimulus
    assert "viagem" in question.stimulus.lower()
    assert "desconhecido" in question.stimulus.lower()

