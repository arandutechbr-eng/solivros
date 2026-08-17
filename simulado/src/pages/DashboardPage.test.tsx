import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, expect, test, vi } from "vitest";
import { DashboardPage } from "./DashboardPage";

vi.mock("../services/simulado", () => ({
  getProgress: vi.fn(),
  getContent: vi.fn(),
  startQuiz: vi.fn(),
}));

import { getContent, getProgress } from "../services/simulado";

beforeEach(() => {
  vi.mocked(getProgress).mockResolvedValue({
    xp: 0,
    level: 1,
    level_name: "Iniciante",
    questions_answered: 0,
    questions_correct: 0,
    quizzes_completed: 0,
    current_streak: 0,
    accuracy: 0,
    last_chapter_id: null,
    last_attempt_id: null,
    next_level_xp: 200,
  });
  vi.mocked(getContent).mockResolvedValue({
    source_file: "5.json",
    title: "1.000 Questões para a Transpetro",
    subtitle: "Língua Portuguesa — Conhecimentos Gerais",
    page_count: 187,
    chapter_count: 17,
    paragraph_count: 700,
    question_count: 500,
    chapters: [],
  });
});

test("mostra atalhos de simulado", async () => {
  render(
    <MemoryRouter>
      <DashboardPage />
    </MemoryRouter>,
  );

  expect(await screen.findByText("1.000 Questões para a Transpetro")).toBeInTheDocument();
  expect(screen.getByText("Simulado rápido")).toBeInTheDocument();
  expect(screen.getByText("Simulado completo")).toBeInTheDocument();
});
