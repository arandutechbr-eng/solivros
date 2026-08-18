import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, expect, test, vi } from "vitest";
import { SubjectProvider } from "../context/SubjectContext";
import { DashboardPage } from "./DashboardPage";

vi.mock("../services/simulado", () => ({
  getProgress: vi.fn(),
  getContent: vi.fn(),
  getSubjects: vi.fn(),
  startQuiz: vi.fn(),
}));

import { getContent, getProgress, getSubjects } from "../services/simulado";

beforeEach(() => {
  vi.mocked(getSubjects).mockResolvedValue([
    {
      id: "portugues",
      title: "Língua Portuguesa",
      subtitle: "Caderno Transpetro — Conhecimentos Gerais",
      question_count: 500,
      chapter_count: 17,
      source_file: "5.json",
    },
    {
      id: "matematica",
      title: "Matemática",
      subtitle: "Caderno Transpetro — Conhecimentos Gerais",
      question_count: 200,
      chapter_count: 10,
      source_file: "1.json",
    },
    {
      id: "ingles",
      title: "Língua Inglesa",
      subtitle: "Caderno Transpetro — Conhecimentos Gerais",
      question_count: 150,
      chapter_count: 8,
      source_file: "2.json",
    },
  ]);
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
    title: "Língua Portuguesa",
    subtitle: "Língua Portuguesa — Conhecimentos Gerais",
    page_count: 187,
    chapter_count: 17,
    paragraph_count: 700,
    question_count: 500,
    subject_id: "portugues",
    chapters: [],
  });
});

test("mostra matérias e atalhos de simulado", async () => {
  render(
    <MemoryRouter>
      <SubjectProvider>
        <DashboardPage />
      </SubjectProvider>
    </MemoryRouter>,
  );

  expect(await screen.findByText("Escolha a matéria")).toBeInTheDocument();
  expect(screen.getByText("Língua Portuguesa")).toBeInTheDocument();
  expect(screen.getByText("Matemática")).toBeInTheDocument();
  expect(screen.getByText("Língua Inglesa")).toBeInTheDocument();
  expect(screen.getByText("Simulado rápido")).toBeInTheDocument();
  expect(screen.getByText("Simulado completo")).toBeInTheDocument();
});
