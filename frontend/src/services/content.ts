import { api } from "./api";
import type { ContentBook, ContentChapterDetail, ContentChapterSummary } from "../types/content";

export async function getContentBook(): Promise<ContentBook> {
  const { data } = await api.get<ContentBook>("/api/content");
  return data;
}

export async function listContentChapters(): Promise<ContentChapterSummary[]> {
  const { data } = await api.get<ContentChapterSummary[]>("/api/content/chapters");
  return data;
}

export async function getContentChapter(chapterId: string): Promise<ContentChapterDetail> {
  const { data } = await api.get<ContentChapterDetail>(`/api/content/chapters/${chapterId}`);
  return data;
}
