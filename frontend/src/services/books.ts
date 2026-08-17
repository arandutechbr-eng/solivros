import { api } from "./api";
import type {
  Book,
  BookStatusPayload,
  Chapter,
  Paragraph,
  ParagraphType,
  ReaderBook,
} from "../types/book";

export async function listBooks(): Promise<Book[]> {
  const { data } = await api.get<Book[]>("/api/books");
  return data;
}

export async function getBook(id: number): Promise<Book> {
  const { data } = await api.get<Book>(`/api/books/${id}`);
  return data;
}

export async function getBookStatus(id: number): Promise<BookStatusPayload> {
  const { data } = await api.get<BookStatusPayload>(`/api/books/${id}/status`);
  return data;
}

export async function createBook(
  payload: FormData,
  onProgress?: (percent: number) => void,
): Promise<Book> {
  const { data } = await api.post<Book>("/api/books", payload, {
    onUploadProgress: (event) => {
      if (!onProgress || !event.total) return;
      onProgress(Math.round((event.loaded * 100) / event.total));
    },
  });
  return data;
}

export async function deleteBook(id: number): Promise<void> {
  await api.delete(`/api/books/${id}`);
}

export async function processBook(id: number): Promise<BookStatusPayload> {
  const { data } = await api.post<BookStatusPayload>(`/api/books/${id}/process`);
  return data;
}

export async function listChapters(bookId: number): Promise<Chapter[]> {
  const { data } = await api.get<Chapter[]>(`/api/books/${bookId}/chapters`);
  return data;
}

export async function createChapter(bookId: number, title: string): Promise<Chapter> {
  const { data } = await api.post<Chapter>(`/api/books/${bookId}/chapters`, { title });
  return data;
}

export async function updateChapter(
  chapterId: number,
  payload: { title?: string; order?: number; number?: number | null },
): Promise<Chapter> {
  const { data } = await api.put<Chapter>(`/api/chapters/${chapterId}`, payload);
  return data;
}

export async function deleteChapter(chapterId: number): Promise<void> {
  await api.delete(`/api/chapters/${chapterId}`);
}

export async function listParagraphs(chapterId: number): Promise<Paragraph[]> {
  const { data } = await api.get<Paragraph[]>(`/api/chapters/${chapterId}/paragraphs`);
  return data;
}

export async function createParagraph(
  chapterId: number,
  payload: { content?: string; type?: ParagraphType; confidence?: number },
): Promise<Paragraph> {
  const { data } = await api.post<Paragraph>(`/api/chapters/${chapterId}/paragraphs`, payload);
  return data;
}

export async function updateParagraph(
  paragraphId: number,
  payload: { content?: string; type?: ParagraphType; order?: number },
): Promise<Paragraph> {
  const { data } = await api.put<Paragraph>(`/api/paragraphs/${paragraphId}`, payload);
  return data;
}

export async function deleteParagraph(paragraphId: number): Promise<void> {
  await api.delete(`/api/paragraphs/${paragraphId}`);
}

export async function approveBook(id: number): Promise<Book> {
  const { data } = await api.post<Book>(`/api/books/${id}/approve`);
  return data;
}

export async function publishBook(id: number): Promise<Book> {
  const { data } = await api.post<Book>(`/api/books/${id}/publish`);
  return data;
}

export async function getReaderBook(id: number): Promise<ReaderBook> {
  const { data } = await api.get<ReaderBook>(`/api/books/${id}/reader`);
  return data;
}
