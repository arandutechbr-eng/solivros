import { FormEvent, type ReactNode, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getContent, startQuiz } from "../services/simulado";
import type { ChapterSummary } from "../types";

export function CustomQuizPage() {
  const navigate = useNavigate();
  const [chapters, setChapters] = useState<ChapterSummary[]>([]);
  const [count, setCount] = useState(10);
  const [chapterId, setChapterId] = useState("");
  const [difficulty, setDifficulty] = useState("all");
  const [timeLimit, setTimeLimit] = useState(15);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    getContent()
      .then((book) => setChapters(book.chapters))
      .catch(() => setError("Não foi possível carregar os tópicos."));
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setStarting(true);
    try {
      const attempt = await startQuiz({
        mode: "custom",
        count,
        chapter_id: chapterId || undefined,
        difficulty,
        time_limit_minutes: timeLimit || undefined,
      });
      navigate(`/simulados/${attempt.id}`);
    } catch {
      setError("Não há questões oficiais para esse recorte.");
    } finally {
      setStarting(false);
    }
  }

  return (
    <section className="mx-auto max-w-xl space-y-6">
      <div>
        <Link to="/simulados" className="text-sm text-amber-300 hover:underline">
          ← Voltar
        </Link>
        <h1 className="mt-3 text-3xl font-semibold text-white">Simulado personalizado</h1>
      </div>

      {error && <p className="text-sm text-rose-300">{error}</p>}

      <form onSubmit={onSubmit} className="space-y-5 rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <Field label="Quantidade">
          <input
            type="number"
            min={1}
            max={100}
            value={count}
            onChange={(event) => setCount(Number(event.target.value))}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
          />
        </Field>
        <Field label="Capítulo">
          <select
            value={chapterId}
            onChange={(event) => setChapterId(event.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
          >
            <option value="">Todos os tópicos</option>
            {chapters.map((chapter) => (
              <option key={chapter.id} value={chapter.id}>
                {chapter.title}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Dificuldade">
          <select
            value={difficulty}
            onChange={(event) => setDifficulty(event.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
          >
            <option value="all">Todas</option>
            <option value="easy">Fácil</option>
            <option value="medium">Média</option>
            <option value="hard">Difícil</option>
          </select>
        </Field>
        <Field label="Tempo (minutos)">
          <input
            type="number"
            min={1}
            max={180}
            value={timeLimit}
            onChange={(event) => setTimeLimit(Number(event.target.value))}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
          />
        </Field>
        <button
          type="submit"
          disabled={starting}
          className="w-full rounded-lg bg-amber-400 px-4 py-2 font-medium text-slate-950 disabled:opacity-50"
        >
          Começar
        </button>
      </form>
    </section>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block space-y-2">
      <span className="text-sm text-slate-300">{label}</span>
      {children}
    </label>
  );
}
