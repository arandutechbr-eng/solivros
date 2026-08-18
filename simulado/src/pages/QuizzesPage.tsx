import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useSubject } from "../context/SubjectContext";
import { getContent, startQuiz } from "../services/simulado";
import type { ChapterSummary } from "../types";

export function QuizzesPage() {
  const navigate = useNavigate();
  const { subjectId, subject } = useSubject();
  const [chapters, setChapters] = useState<ChapterSummary[]>([]);
  const [chapterId, setChapterId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    setChapterId("");
    getContent(subjectId)
      .then((book) => setChapters(book.chapters))
      .catch(() => setError("Não foi possível carregar os tópicos."));
  }, [subjectId]);

  async function begin(mode: "quick" | "medium" | "full") {
    setStarting(true);
    try {
      const attempt = await startQuiz({ mode, subject_id: subjectId });
      navigate(`/simulados/${attempt.id}`);
    } catch {
      setError("Não foi possível iniciar o simulado.");
    } finally {
      setStarting(false);
    }
  }

  async function beginChapter() {
    if (!chapterId) return;
    setStarting(true);
    try {
      const attempt = await startQuiz({ mode: "chapter", subject_id: subjectId, chapter_id: chapterId });
      navigate(`/simulados/${attempt.id}`);
    } catch {
      setError("Não foi possível iniciar o simulado do tópico.");
    } finally {
      setStarting(false);
    }
  }

  return (
    <section className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold text-white">Escolha seu simulado</h1>
        <p className="mt-2 text-slate-400">
          {subject
            ? `Questões oficiais de ${subject.title} — caderno ${subject.source_file}.`
            : "Todas as questões vêm do gabarito oficial do caderno extraído."}
        </p>
      </div>

      {error && <p className="text-sm text-rose-300">{error}</p>}

      <div className="grid gap-4 md:grid-cols-2">
        <ModeCard title="Simulado rápido" detail="10 questões · ~10 minutos" action="Começar" onClick={() => begin("quick")} disabled={starting} />
        <ModeCard title="Simulado médio" detail="20 questões · ~20 minutos" action="Começar" onClick={() => begin("medium")} disabled={starting} />
        <ModeCard title="Simulado completo" detail="50 questões · ~50 minutos" action="Começar" onClick={() => begin("full")} disabled={starting} />
        <Link
          to="/simulados/personalizado"
          className="rounded-2xl border border-slate-800 bg-slate-900 p-5 hover:border-amber-400/40"
        >
          <p className="text-lg font-medium text-white">Personalizado</p>
          <p className="mt-2 text-sm text-slate-400">Quantidade, tópico, dificuldade e tempo.</p>
          <p className="mt-4 text-sm font-medium text-amber-300">Configurar →</p>
        </Link>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
        <h2 className="text-lg font-medium text-white">Por capítulo</h2>
        <div className="mt-4 flex flex-wrap gap-3">
          <select
            value={chapterId}
            onChange={(event) => setChapterId(event.target.value)}
            className="min-w-72 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
          >
            <option value="">Escolha um tópico</option>
            {chapters.map((chapter) => (
              <option key={chapter.id} value={chapter.id}>
                {chapter.number}. {chapter.title} ({chapter.question_count})
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={beginChapter}
            disabled={!chapterId || starting}
            className="rounded-lg bg-amber-400 px-4 py-2 text-sm font-medium text-slate-950 disabled:opacity-50"
          >
            Começar
          </button>
        </div>
      </div>
    </section>
  );
}

function ModeCard({
  title,
  detail,
  action,
  onClick,
  disabled,
}: {
  title: string;
  detail: string;
  action: string;
  onClick: () => void;
  disabled: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="rounded-2xl border border-slate-800 bg-slate-900 p-5 text-left hover:border-amber-400/40 disabled:opacity-60"
    >
      <p className="text-lg font-medium text-white">{title}</p>
      <p className="mt-2 text-sm text-slate-400">{detail}</p>
      <p className="mt-4 text-sm font-medium text-amber-300">{action} →</p>
    </button>
  );
}
