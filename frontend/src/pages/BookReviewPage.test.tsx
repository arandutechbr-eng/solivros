import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { BookReviewPage } from "./BookReviewPage";
import { getBook, listChapters, listParagraphs } from "../services/books";

vi.mock("../services/books", () => ({
  getBook: vi.fn(),
  listChapters: vi.fn(),
  listParagraphs: vi.fn(),
  createChapter: vi.fn(),
  createParagraph: vi.fn(),
  deleteChapter: vi.fn(),
  deleteParagraph: vi.fn(),
  updateChapter: vi.fn(),
  updateParagraph: vi.fn(),
}));

vi.mock("../components/ParagraphEditor", () => ({
  ParagraphEditor: ({ content }: { content: string }) => <div>{content}</div>,
}));

describe("BookReviewPage", () => {
  it("abre a tela de revisão com capítulos", async () => {
    vi.mocked(getBook).mockResolvedValue({
      id: 2,
      title: "Dom Quixote",
      author: "Miguel de Cervantes",
      isbn: null,
      description: null,
      status: "REVIEW",
      original_filename: "sample.pdf",
      raw_text_path: "extracted/2.json",
      page_count: 2,
      created_at: "2026-08-17T12:00:00Z",
      updated_at: "2026-08-17T12:00:00Z",
    });
    vi.mocked(listChapters).mockResolvedValue([
      {
        id: 10,
        book_id: 2,
        number: 1,
        title: "CAPITULO I",
        order: 0,
        created_at: "2026-08-17T12:00:00Z",
        updated_at: "2026-08-17T12:00:00Z",
      },
    ]);
    vi.mocked(listParagraphs).mockResolvedValue([
      {
        id: 20,
        chapter_id: 10,
        content: "Em um lugar da Mancha...",
        order: 0,
        type: "paragraph",
        confidence: 1,
        created_at: "2026-08-17T12:00:00Z",
        updated_at: "2026-08-17T12:00:00Z",
      },
    ]);

    render(
      <MemoryRouter initialEntries={["/books/2/review"]}>
        <Routes>
          <Route path="/books/:id/review" element={<BookReviewPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("CAPITULO I")).toBeInTheDocument();
    });
    expect(screen.getByText("Em um lugar da Mancha...")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Salvar alterações" })).toBeInTheDocument();
  });
});
