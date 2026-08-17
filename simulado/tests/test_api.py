from fastapi.testclient import TestClient

from server.main import app


def test_content_and_quick_quiz_flow() -> None:
    client = TestClient(app)
    content = client.get("/api/content")
    assert content.status_code == 200
    book = content.json()
    assert book["source_file"] == "5.json"
    assert book["question_count"] == 500
    assert book["chapters"]

    chapter_id = book["chapters"][0]["id"]
    detail = client.get(f"/api/content/chapters/{chapter_id}")
    assert detail.status_code == 200
    assert detail.json()["paragraphs"]

    started = client.post("/api/quizzes/start", json={"mode": "quick"})
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
