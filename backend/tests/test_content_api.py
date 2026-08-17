from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_content_endpoints() -> None:
    book = client.get("/api/content")
    assert book.status_code == 200
    payload = book.json()
    assert payload["source_file"] == "5.json"
    assert payload["page_count"] == 187
    assert payload["chapter_count"] >= 16
    assert payload["question_count"] == 500
    assert payload["chapters"]

    chapters = client.get("/api/content/chapters")
    assert chapters.status_code == 200
    first = chapters.json()[0]
    detail = client.get(f"/api/content/chapters/{first['id']}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["paragraphs"]
    paragraph_id = body["paragraphs"][0]["id"]
    paragraph = client.get(f"/api/content/paragraphs/{paragraph_id}")
    assert paragraph.status_code == 200
    assert paragraph.json()["id"] == paragraph_id
