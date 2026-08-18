import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getAttempt, startQuiz } from "../services/simulado";
import type { AttemptDetail } from "../types";

export function ResultPage() {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const id = Number(attemptId);
  const [attempt, setAttempt] = useState<AttemptDetail | null>(null);
  const [onlyWrong, setOnlyWrong] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    getAttempt(id)
      .then(setAttempt)
      .catch(() => setError("Resultado não encontrado."));
  }, [id]);

  const visible = useMemo(() => {
    if (!attempt) return [];
    return onlyWrong ? attempt.questions.filter((question) => question.is_correct === false) : attempt.questions;
  }, [attempt, onlyWrong]);

  async function retry() {
    if (!attempt) return;
    const next = await startQuiz({
      mode: attempt.mode as "quick" | "medium" | "full" | "chapter" | "custom",
      subject_id: attempt.subject_id ?? undefined,
      chapter_id: attempt.chapter_id ?? undefined,
      count: attempt.question_count,
      difficulty: attempt.difficulty,
      time_limit_minutes: attempt.time_limit_minutes ?? undefined,
    });
    navigate(`/simulados/${next.id}`);
  }

  if (error) return <p className="text-rose-300">{error}</p>;
  if (!attempt) return <p className="text-slate-400">Carregando resultado...</p>;

  const minutes = Math.floor((attempt.duration_seconds ?? 0) / 60);
  const seconds = (attempt.duration_seconds ?? 0) % 60;

  return (
    <section className="space-y-8">
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center">
        <p className="text-sm uppercase tracking-wide text-amber-300">Simulado concluído</p>
        <p className="mt-4 text-6xl font-semibold text-white">{attempt.score ?? 0}%</p>
        <p className="mt-3 text-slate-300">
          {attempt.correct_answers} / {attempt.question_count} acertos
        </p>
        <p className="mt-2 text-sm text-slate-400">
          {attempt.correct_answers} corretas · {attempt.wrong_answers} incorretas · {minutes}m {seconds}s
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <button type="button" onClick={() => setOnlyWrong(true)} className="rounded-lg bg-slate-800 px-4 py-2 text-sm">
          Revisar erros
        </button>
        <button type="button" onClick={() => setOnlyWrong(false)} className="rounded-lg bg-slate-800 px-4 py-2 text-sm">
          Ver respostas
        </button>
        <button type="button" onClick={retry} className="rounded-lg bg-amber-400 px-4 py-2 text-sm font-medium text-slate-950">
          Refazer simulado
        </button>
        <Link to="/conteudo" className="rounded-lg bg-slate-800 px-4 py-2 text-sm">
          Voltar ao conteúdo
        </Link>
      </div>

      <div className="space-y-4">
        {visible.map((question, index) => (
          <article key={question.id} className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Questão {index + 1} · oficial {question.number} · {question.is_correct ? "acerto" : "erro"}
            </p>
            <p className="mt-2 leading-7 text-slate-100">{question.prompt}</p>
            <p className="mt-3 text-sm text-slate-300">
              Você respondeu: {question.selected_letter ?? "—"} · Correta: {question.correct_letter}
            </p>
            <p className="mt-2 text-sm text-slate-400">{question.explanation}</p>
            <Link to={`/conteudo/${question.source.chapter_id}`} className="mt-3 inline-block text-sm text-amber-300">
              Ver conteúdo relacionado →
            </Link>
          </article>
        ))}
        {visible.length === 0 && <p className="text-slate-400">Nenhum erro neste simulado.</p>}
      </div>
    </section>
  );
}
