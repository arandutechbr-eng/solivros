import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { StudyBookPage } from "./StudyBookPage";
import { getContentBook } from "../services/content";

vi.mock("../services/content", () => ({
  getContentBook: vi.fn(),
}));

describe("StudyBookPage", () => {
  it("mostra livro, capítulos e parágrafos do 5.json", async () => {
    vi.mocked(getContentBook).mockResolvedValue({
      source_file: "5.json",
      book_id: 5,
      title: "1.000 Questões para a Transpetro",
      subtitle: "Língua Portuguesa",
      page_count: 187,
      chapter_count: 18,
      paragraph_count: 750,
      question_count: 500,
      chapters: [
        {
          id: "01-ortografia",
          number: 1,
          title: "Ortografia",
          start_page: 3,
          end_page: 5,
          paragraph_count: 12,
          question_count: 13,
        },
      ],
    });

    render(
      <MemoryRouter>
        <StudyBookPage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("1.000 Questões para a Transpetro")).toBeInTheDocument();
    });
    expect(screen.getByText(/Ortografia/)).toBeInTheDocument();
    expect(screen.getByText("Fonte original: 5.json")).toBeInTheDocument();
  });
});
