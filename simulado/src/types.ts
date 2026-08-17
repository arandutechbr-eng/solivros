export type OptionPublic = {
  letter: string;
  text: string;
  is_correct: boolean | null;
};

export type SourceRef = {
  chapter_id: string;
  chapter: string;
  page: number;
  paragraph_id: string;
  source_file: string;
};

export type QuestionPublic = {
  id: number;
  number: number;
  exam_source: string;
  prompt: string;
  stimulus: string | null;
  difficulty: string;
  options: OptionPublic[];
  source: SourceRef;
  selected_letter: string | null;
  is_correct: boolean | null;
  correct_letter: string | null;
  explanation: string | null;
};

export type ChapterSummary = {
  id: string;
  number: number;
  title: string;
  start_page: number;
  end_page: number;
  paragraph_count: number;
  question_count: number;
};

export type ParagraphPublic = {
  id: string;
  page: number;
  order: number;
  kind: string;
  text: string;
  question_number: number | null;
  exam_source: string | null;
};

export type ChapterDetail = ChapterSummary & {
  paragraphs: ParagraphPublic[];
};

export type ContentBook = {
  source_file: string;
  title: string;
  subtitle: string;
  page_count: number;
  chapter_count: number;
  paragraph_count: number;
  question_count: number;
  chapters: ChapterSummary[];
};

export type AttemptSummary = {
  id: number;
  mode: string;
  title: string;
  chapter_id: string | null;
  question_count: number;
  difficulty: string;
  time_limit_minutes: number | null;
  status: string;
  score: number | null;
  correct_answers: number;
  wrong_answers: number;
  duration_seconds: number | null;
  started_at: string;
  finished_at: string | null;
  answered_count: number;
};

export type AttemptDetail = AttemptSummary & {
  questions: QuestionPublic[];
};

export type AnswerFeedback = {
  question_id: number;
  selected_letter: string;
  is_correct: boolean;
  correct_letter: string;
  explanation: string;
  source: SourceRef;
  xp_earned: number;
};

export type Progress = {
  xp: number;
  level: number;
  level_name: string;
  questions_answered: number;
  questions_correct: number;
  quizzes_completed: number;
  current_streak: number;
  accuracy: number;
  last_chapter_id: string | null;
  last_attempt_id: number | null;
  next_level_xp: number | null;
};

export type StartQuizPayload = {
  mode: "quick" | "medium" | "full" | "chapter" | "custom";
  chapter_id?: string;
  count?: number;
  difficulty?: string;
  time_limit_minutes?: number;
};
