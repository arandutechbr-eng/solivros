import { api } from "./api";
import type {
  AnswerFeedback,
  AttemptDetail,
  AttemptSummary,
  ChapterDetail,
  ContentBook,
  Progress,
  StartQuizPayload,
} from "../types";

export async function getContent(): Promise<ContentBook> {
  const { data } = await api.get<ContentBook>("/api/content");
  return data;
}

export async function getChapter(chapterId: string): Promise<ChapterDetail> {
  const { data } = await api.get<ChapterDetail>(`/api/content/chapters/${chapterId}`);
  return data;
}

export async function startQuiz(payload: StartQuizPayload): Promise<AttemptDetail> {
  const { data } = await api.post<AttemptDetail>("/api/quizzes/start", payload);
  return data;
}

export async function getAttempt(attemptId: number): Promise<AttemptDetail> {
  const { data } = await api.get<AttemptDetail>(`/api/attempts/${attemptId}`);
  return data;
}

export async function listAttempts(): Promise<AttemptSummary[]> {
  const { data } = await api.get<AttemptSummary[]>("/api/attempts");
  return data;
}

export async function answerQuestion(
  attemptId: number,
  questionId: number,
  selectedLetter: string,
): Promise<AnswerFeedback> {
  const { data } = await api.post<AnswerFeedback>(`/api/attempts/${attemptId}/answer`, {
    question_id: questionId,
    selected_letter: selectedLetter,
  });
  return data;
}

export async function finishQuiz(attemptId: number): Promise<AttemptDetail> {
  const { data } = await api.post<AttemptDetail>(`/api/attempts/${attemptId}/finish`);
  return data;
}

export async function getProgress(): Promise<Progress> {
  const { data } = await api.get<Progress>("/api/progress");
  return data;
}
