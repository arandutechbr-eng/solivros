import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useSubject } from "../context/SubjectContext";
import { getContent, getProgress, startQuiz } from "../services/simulado";
import type { ContentBook, Progress } from "../types";

export function DashboardPage() {
  const navigate = useNavigate();
  const { subjects, subjectId, subject, setSubjectId } = useSubject();
  const [progress, setProgress] = useState<Progress | null>(null);
  const [book, setBook] = useState<ContentBook | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    Promise.all([getProgress(), getContent(subjectId)])
      .then(([nextProgress, nextBook]) => {
        setProgress(nextProgress);
        setBook(nextBook);
      })
      .catch(() => setError("Não foi possível carregar o painel. Suba o backend em http://127.0.0.1:8001."));
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

  const levelPercent = progress
    ? progress.next_level_xp
      ? Math.min(100, Math.round((progress.xp / progress.next_level_xp) * 100))
      : 100
    : 0;

  return (
    <section className="space-y-8">
      <div>
        <p className="text-sm font-medium uppercase tracking-wide text-amber-300">Plataforma de estudos</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-white">Escolha a matéria</h1>
        <p className="mt-2 text-slate-400">Questões oficiais CESGRANRIO dos cadernos extraídos. Sem itens inventados.</p>
      </div>

      {error && <p className="text-sm text-rose-300">{error}</p>}

      <div className="grid gap-4 md:grid-cols-3">
        {subjects.map((item) => {
          const selected = item.id === subjectId;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => setSubjectId(item.id)}
              className={`rounded-2xl border p-5 text-left transition ${
                selected
                  ? "border-amber-400 bg-slate-900"
                  : "border-slate-800 bg-slate-900 hover:border-amber-400/40"
              }`}
            >
              <p className="text-lg font-medium text-white">{item.title}</p>
              <p className="mt-2 text-sm text-slate-400">{item.subtitle}</p>
              <p className="mt-4 text-sm text-amber-300">
                {item.question_count} questões · {item.chapter_count} tópicos
              </p>
              {selected && <p className="mt-2 text-xs uppercase tracking-wide text-amber-200">Selecionada</p>}
            </button>
          );
        })}
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm text-slate-400">Seu progresso</p>
            <p className="mt-1 text-2xl font-semibold text-white">
              Nível {progress?.level ?? 1} — {progress?.level_name ?? "Iniciante"}
            </p>
          </div>
          <p className="text-sm text-slate-400">{progress?.xp ?? 0} XP</p>
        </div>
        <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-800">
          <div className="h-full rounded-full bg-amber-400" style={{ width: `${levelPercent}%` }} />
        </div>
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <Stat label="Questões respondidas" value={progress?.questions_answered ?? 0} />
          <Stat label="Acertos" value={`${progress?.accuracy ?? 0}%`} />
          <Stat label="Simulados feitos" value={progress?.quizzes_completed ?? 0} />
        </div>
      </div>

      <div>
        <h2 className="text-lg font-medium text-white">
          Começar um simulado de {subject?.title ?? book?.title ?? "esta matéria"}
        </h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <StartCard title="Simulado rápido" detail="10 questões oficiais · ~10 min" onClick={() => begin("quick")} disabled={starting} />
          <StartCard title="Simulado médio" detail="20 questões oficiais · ~20 min" onClick={() => begin("medium")} disabled={starting} />
          <StartCard title="Simulado completo" detail="50 questões oficiais · ~50 min" onClick={() => begin("full")} disabled={starting} />
          <Link
            to="/simulados"
            className="rounded-2xl border border-slate-800 bg-slate-900 p-5 transition hover:border-amber-400/40"
          >
            <p className="text-lg font-medium text-white">Por capítulo ou personalizado</p>
            <p className="mt-2 text-sm text-slate-400">Escolha o tópico, a quantidade e a dificuldade.</p>
          </Link>
        </div>
      </div>

      {progress?.last_chapter_id && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">Continuar estudando</p>
          <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
            <p className="text-white">Último tópico aberto no caderno</p>
            <Link
              to={`/conteudo/${progress.last_chapter_id}`}
              className="rounded-lg bg-amber-400 px-4 py-2 text-sm font-medium text-slate-950"
            >
              Continuar
            </Link>
          </div>
        </div>
      )}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: number | string }) {
  return (
    <div>
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-white">{value}</p>
    </div>
  );
}

function StartCard({
  title,
  detail,
  onClick,
  disabled,
}: {
  title: string;
  detail: string;
  onClick: () => void;
  disabled: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="rounded-2xl border border-slate-800 bg-slate-900 p-5 text-left transition hover:border-amber-400/40 disabled:opacity-60"
    >
      <p className="text-lg font-medium text-white">{title}</p>
      <p className="mt-2 text-sm text-slate-400">{detail}</p>
      <p className="mt-4 text-sm font-medium text-amber-300">Começar →</p>
    </button>
  );
}
