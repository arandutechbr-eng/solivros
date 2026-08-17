export type BookStatus =
  | "UPLOADED"
  | "PROCESSING"
  | "EXTRACTED"
  | "STRUCTURED"
  | "REVIEW"
  | "APPROVED"
  | "PUBLISHED"
  | "ERROR";

export type ParagraphType =
  | "paragraph"
  | "heading"
  | "subheading"
  | "quote"
  | "footnote"
  | "caption";

export interface Book {
  id: number;
  title: string;
  author: string;
  isbn: string | null;
  description: string | null;
  status: BookStatus;
  original_filename: string | null;
  raw_text_path: string | null;
  page_count: number | null;
  created_at: string;
  updated_at: string;
  chapter_count?: number;
  paragraph_count?: number;
}

export interface BookStatusPayload {
  id: number;
  status: BookStatus;
  page_count: number | null;
  raw_text_path: string | null;
}

export interface Chapter {
  id: number;
  book_id: number;
  number: number | null;
  title: string;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface Paragraph {
  id: number;
  chapter_id: number;
  content: string;
  order: number;
  type: ParagraphType;
  confidence: number;
  created_at: string;
  updated_at: string;
}

export interface ReaderParagraph {
  id: number;
  content: string;
  type: ParagraphType;
  order: number;
  confidence: number;
}

export interface ReaderChapter {
  id: number;
  title: string;
  number: number | null;
  order: number;
  paragraphs: ReaderParagraph[];
}

export interface ReaderBook {
  id: number;
  title: string;
  author: string;
  status: BookStatus;
  chapters: ReaderChapter[];
}
