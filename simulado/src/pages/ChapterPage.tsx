import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useSubject } from "../context/SubjectContext";
import { getChapter, startQuiz } from "../services/simulado";
import type { ChapterDetail } from "../types";

const KIND_LABEL: Record<string, string> = {
  question: "Questão",
  stimulus: "Texto-base",
  heading: "Título",
  paragraph: "Parágrafo",
};

export function ChapterPage() {
  const { chapterId } = useParams();
  const navigate = useNavigate();
  const { subjectId, setSubjectId } = useSubject();
  const [chapter, setChapter] = useState<ChapterDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    if (!chapterId) return;
    const prefix = chapterId.split("-")[0];
    if (prefix === "portugues" || prefix === "matematica" || prefix === "ingles") {
      setSubjectId(prefix);
    }
    getChapter(chapterId)
      .then(setChapter)
      .catch(() => setError("Capítulo não encontrado."));
  }, [chapterId, setSubjectId]);

  async function beginChapterQuiz() {
    if (!chapterId) return;
    setStarting(true);
    try {
      const attempt = await startQuiz({ mode: "chapter", subject_id: subjectId, chapter_id: chapterId });
      navigate(`/simulados/${attempt.id}`);
    } catch {
      setError("Não foi possível iniciar o simulado deste tópico.");
    } finally {
      setStarting(false);
    }
  }

  if (error) return <p className="text-rose-300">{error}</p>;
  if (!chapter) return <p className="text-slate-400">Carregando capítulo...</p>;

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link to="/conteudo" className="text-sm text-amber-300 hover:underline">
            ← Todos os tópicos
          </Link>
          <h1 className="mt-3 text-3xl font-semibold text-white">{chapter.title}</h1>
          <p className="mt-2 text-sm text-slate-400">
            Páginas {chapter.start_page}–{chapter.end_page} · {chapter.question_count} questões oficiais
          </p>
        </div>
        <button
          type="button"
          onClick={beginChapterQuiz}
          disabled={starting || chapter.question_count === 0}
          className="rounded-lg bg-amber-400 px-4 py-2 text-sm font-medium text-slate-950 disabled:opacity-50"
        >
          Simulado deste tópico
        </button>
      </div>

      <div className="space-y-4">
        {chapter.paragraphs.map((paragraph) => (
          <article key={paragraph.id} className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-slate-500">
              <span className="rounded-full bg-slate-800 px-2 py-1 text-slate-300">
                {KIND_LABEL[paragraph.kind] ?? paragraph.kind}
              </span>
              <span>p. {paragraph.page}</span>
              {paragraph.question_number != null && <span>nº {paragraph.question_number}</span>}
              {paragraph.exam_source && <span>{paragraph.exam_source}</span>}
            </div>
            <p className="whitespace-pre-wrap leading-7 text-slate-200">{paragraph.text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
