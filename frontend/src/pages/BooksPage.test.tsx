import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { BooksPage } from "./BooksPage";
import { listBooks } from "../services/books";

vi.mock("../services/books", () => ({
  listBooks: vi.fn(),
  deleteBook: vi.fn(),
}));

describe("BooksPage", () => {
  beforeEach(() => {
    vi.mocked(listBooks).mockResolvedValue([
      {
        id: 1,
        title: "Dom Quixote",
        author: "Miguel de Cervantes",
        isbn: null,
        description: null,
        status: "REVIEW",
        original_filename: "livro.pdf",
        raw_text_path: "extracted/1.json",
        page_count: 2,
        created_at: "2026-08-17T12:00:00Z",
        updated_at: "2026-08-17T12:00:00Z",
      },
    ]);
  });

  it("carrega a lista de livros", async () => {
    render(
      <MemoryRouter>
        <BooksPage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("Dom Quixote")).toBeInTheDocument();
    });
    expect(screen.getByText("Miguel de Cervantes")).toBeInTheDocument();
    expect(screen.getByText("Em revisão")).toBeInTheDocument();
  });
});
