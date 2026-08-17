from app.services.structure_service import structure_pages


def test_detects_named_chapters() -> None:
    pages = [
        {"page": 1, "text": "CAPITULO I\n\nEm um lugar da Mancha."},
        {"page": 2, "text": "CAPITULO II\n\nSaindo o fidalgo."},
    ]
    chapters = structure_pages(pages)
    assert len(chapters) == 2
    assert chapters[0].title == "CAPITULO I"
    assert chapters[0].number == 1
    assert "Mancha" in chapters[0].paragraphs[0].content
    assert chapters[1].title == "CAPITULO II"


def test_falls_back_to_single_chapter() -> None:
    pages = [{"page": 1, "text": "Um texto corrido sem marcadores de capitulo."}]
    chapters = structure_pages(pages)
    assert len(chapters) == 1
    assert chapters[0].title == "Conteúdo"
    assert chapters[0].paragraphs[0].content
