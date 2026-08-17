import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getContentChapter } from "../services/content";
import type { ContentChapterDetail, ContentParagraph } from "../types/content";

const KIND_LABEL: Record<string, string> = {
  question: "Questão",
  stimulus: "Texto-base",
  heading: "Título",
  paragraph: "Parágrafo",
};

export function StudyChapterPage() {
  const { chapterId } = useParams();
  const [chapter, setChapter] = useState<ContentChapterDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!chapterId) return;
    getContentChapter(chapterId)
      .then(setChapter)
      .catch(() => setError("Capítulo não encontrado."));
  }, [chapterId]);

  if (error) {
    return <p className="text-red-700">{error}</p>;
  }

  if (!chapter) {
    return <p className="text-slate-500">Carregando capítulo...</p>;
  }

  return (
    <section className="space-y-6">
      <div>
        <Link to="/study" className="text-sm text-teal-800 hover:underline">
          ← Todos os capítulos
        </Link>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">{chapter.title}</h1>
        <p className="mt-2 text-sm text-slate-500">
          Páginas {chapter.start_page}–{chapter.end_page} · {chapter.paragraph_count} trechos · {chapter.question_count}{" "}
          questões no original
        </p>
      </div>

      <div className="space-y-4">
        {chapter.paragraphs.map((paragraph) => (
          <ContentBlock key={paragraph.id} paragraph={paragraph} />
        ))}
      </div>
    </section>
  );
}

function ContentBlock({ paragraph }: { paragraph: ContentParagraph }) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-5">
      <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-slate-500">
        <span className="rounded-full bg-slate-100 px-2 py-1 font-medium text-slate-700">
          {KIND_LABEL[paragraph.kind] ?? paragraph.kind}
        </span>
        <span>p. {paragraph.page}</span>
        <span className="font-mono">{paragraph.id}</span>
        {paragraph.question_number != null && <span>nº {paragraph.question_number}</span>}
        {paragraph.exam_source && <span>{paragraph.exam_source}</span>}
      </div>
      <p className="whitespace-pre-wrap leading-7 text-slate-800">{paragraph.text}</p>
    </article>
  );
}
