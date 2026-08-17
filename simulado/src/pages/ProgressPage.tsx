import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getProgress, listAttempts } from "../services/simulado";
import type { AttemptSummary, Progress } from "../types";

export function ProgressPage() {
  const [progress, setProgress] = useState<Progress | null>(null);
  const [attempts, setAttempts] = useState<AttemptSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getProgress(), listAttempts()])
      .then(([nextProgress, nextAttempts]) => {
        setProgress(nextProgress);
        setAttempts(nextAttempts);
      })
      .catch(() => setError("Não foi possível carregar o desempenho."));
  }, []);

  if (error) return <p className="text-rose-300">{error}</p>;
  if (!progress) return <p className="text-slate-400">Carregando desempenho...</p>;

  const finished = attempts.filter((attempt) => attempt.status === "finished" && attempt.score != null);
  const best = finished.reduce((max, attempt) => Math.max(max, attempt.score ?? 0), 0);
  const average = finished.length
    ? Math.round(finished.reduce((sum, attempt) => sum + (attempt.score ?? 0), 0) / finished.length)
    : 0;

  return (
    <section className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold text-white">Meu desempenho</h1>
        <p className="mt-2 text-slate-400">
          Nível {progress.level} — {progress.level_name} · {progress.xp} XP
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Média de acertos" value={`${average}%`} />
        <Stat label="Melhor pontuação" value={`${best}%`} />
        <Stat label="Simulados" value={progress.quizzes_completed} />
        <Stat label="Questões respondidas" value={progress.questions_answered} />
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900">
        <div className="border-b border-slate-800 px-5 py-4">
          <h2 className="font-medium text-white">Histórico</h2>
        </div>
        <ul>
          {attempts.length === 0 && <li className="px-5 py-6 text-sm text-slate-400">Nenhum simulado ainda.</li>}
          {attempts.map((attempt) => (
            <li key={attempt.id} className="flex items-center justify-between border-b border-slate-800 px-5 py-4 last:border-0">
              <div>
                <p className="text-white">{attempt.title}</p>
                <p className="mt-1 text-sm text-slate-400">
                  {attempt.answered_count}/{attempt.question_count} respondidas
                  {attempt.score != null ? ` · ${attempt.score}%` : ""}
                </p>
              </div>
              <Link
                to={attempt.status === "finished" ? `/resultados/${attempt.id}` : `/simulados/${attempt.id}`}
                className="text-sm text-amber-300"
              >
                {attempt.status === "finished" ? "Ver resultado" : "Continuar"}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-white">{value}</p>
    </div>
  );
}
