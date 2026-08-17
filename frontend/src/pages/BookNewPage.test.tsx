import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { BookNewPage } from "./BookNewPage";
import { createBook } from "../services/books";

const navigate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom");
  return { ...actual, useNavigate: () => navigate };
});

vi.mock("../services/books", () => ({
  createBook: vi.fn(),
}));

describe("BookNewPage", () => {
  it("envia o upload de um PDF", async () => {
    const user = userEvent.setup();
    vi.mocked(createBook).mockResolvedValue({
      id: 9,
      title: "Novo Livro",
      author: "Autora",
      isbn: null,
      description: null,
      status: "UPLOADED",
      original_filename: "amostra.pdf",
      raw_text_path: null,
      page_count: null,
      created_at: "2026-08-17T12:00:00Z",
      updated_at: "2026-08-17T12:00:00Z",
    });

    render(
      <MemoryRouter>
        <BookNewPage />
      </MemoryRouter>,
    );

    await user.type(screen.getByLabelText("Título"), "Novo Livro");
    const file = new File(["%PDF-1.4 sample"], "amostra.pdf", { type: "application/pdf" });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    await user.upload(input, file);
    await user.click(screen.getByRole("button", { name: "Enviar PDF" }));

    await waitFor(() => {
      expect(createBook).toHaveBeenCalled();
      expect(navigate).toHaveBeenCalledWith("/books/9");
    });
  });
});
