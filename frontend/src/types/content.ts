export type ContentBlockKind = "paragraph" | "heading" | "question" | "stimulus";

export interface ContentParagraph {
  id: string;
  page: number;
  order: number;
  kind: ContentBlockKind | string;
  text: string;
  question_number: number | null;
  exam_source: string | null;
}

export interface ContentChapterSummary {
  id: string;
  number: number;
  title: string;
  start_page: number;
  end_page: number;
  paragraph_count: number;
  question_count: number;
}

export interface ContentChapterDetail extends ContentChapterSummary {
  paragraphs: ContentParagraph[];
}

export interface ContentBook {
  source_file: string;
  book_id: number | null;
  title: string;
  subtitle: string;
  page_count: number;
  chapter_count: number;
  paragraph_count: number;
  question_count: number;
  chapters: ContentChapterSummary[];
}
