import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { StimulusBlock } from "../components/StimulusBlock";
import { answerQuestion, finishQuiz, getAttempt } from "../services/simulado";
import type { AnswerFeedback, AttemptDetail } from "../types";

export function TakeQuizPage() {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const id = Number(attemptId);
  const [attempt, setAttempt] = useState<AttemptDetail | null>(null);
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<AnswerFeedback | null>(null);
  const [showSource, setShowSource] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    getAttempt(id)
      .then((data) => {
        if (data.status === "finished") {
          navigate(`/resultados/${data.id}`, { replace: true });
          return;
        }
        const firstOpen = data.questions.findIndex((question) => question.selected_letter == null);
        setAttempt(data);
        setIndex(firstOpen === -1 ? 0 : firstOpen);
      })
      .catch(() => setError("Simulado não encontrado."));
  }, [id, navigate]);

  const question = attempt?.questions[index];
  const progress = useMemo(() => {
    if (!attempt) return 0;
    return Math.round((attempt.answered_count / attempt.question_count) * 100);
  }, [attempt]);

  async function submit() {
    if (!attempt || !question || !selected) return;
    setSaving(true);
    try {
      const result = await answerQuestion(attempt.id, question.id, selected);
      setFeedback(result);
      const refreshed = await getAttempt(attempt.id);
      setAttempt(refreshed);
    } catch {
      setError("Não foi possível registrar a resposta.");
    } finally {
      setSaving(false);
    }
  }

  async function goNext() {
    if (!attempt) return;
    setFeedback(null);
    setSelected(null);
    setShowSource(false);
    if (index + 1 >= attempt.questions.length) {
      const finished = await finishQuiz(attempt.id);
      navigate(`/resultados/${finished.id}`);
      return;
    }
    setIndex((current) => current + 1);
  }

  if (error) return <p className="text-rose-300">{error}</p>;
  if (!attempt || !question) return <p className="text-slate-400">Carregando simulado...</p>;

  const alreadyAnswered = question.selected_letter != null;
  const correctLetter = feedback?.correct_letter ?? question.correct_letter;
  const isCorrect = feedback?.is_correct ?? question.is_correct;

  return (
    <section className="mx-auto max-w-3xl space-y-6">
      <div>
        <p className="text-sm text-slate-400">{attempt.title}</p>
        <h1 className="mt-1 text-2xl font-semibold text-white">
          Questão {index + 1} de {attempt.question_count}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Oficial {question.number} · {question.exam_source} · {question.source.chapter}
        </p>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-slate-800">
        <div className="h-full bg-amber-400" style={{ width: `${progress}%` }} />
      </div>

      {question.stimulus && <StimulusBlock stimulus={question.stimulus} />}

      <article id="questao" className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <p className="whitespace-pre-wrap leading-7 text-slate-100">{question.prompt}</p>
        <div className="mt-6 space-y-3">
          {question.options.map((option) => {
            const active = (selected ?? question.selected_letter) === option.letter;
            const showCorrect = alreadyAnswered && option.letter === correctLetter;
            const showWrong = alreadyAnswered && active && option.letter !== correctLetter;
            return (
              <button
                key={option.letter}
                type="button"
                disabled={alreadyAnswered}
                onClick={() => setSelected(option.letter)}
                className={`block w-full rounded-xl border px-4 py-3 text-left ${
                  showCorrect
                    ? "border-emerald-400 bg-emerald-400/10"
                    : showWrong
                      ? "border-rose-400 bg-rose-400/10"
                      : active
                        ? "border-amber-400 bg-amber-400/10"
                        : "border-slate-700 hover:border-slate-500"
                }`}
              >
                <span className="mr-3 font-semibold text-amber-300">{option.letter})</span>
                <span className="text-slate-100">{option.text}</span>
              </button>
            );
          })}
        </div>
      </article>

      {alreadyAnswered && (
        <div className={`rounded-2xl border p-5 ${isCorrect ? "border-emerald-500/40 bg-emerald-500/10" : "border-rose-500/40 bg-rose-500/10"}`}>
          <p className="font-medium text-white">{isCorrect ? "Correto!" : "Incorreto"}</p>
          {!isCorrect && <p className="mt-1 text-sm text-slate-200">Resposta correta: {correctLetter}</p>}
          <p className="mt-3 text-sm leading-6 text-slate-200">{feedback?.explanation ?? question.explanation}</p>
          <button type="button" onClick={() => setShowSource((value) => !value)} className="mt-3 text-sm text-amber-300">
            {showSource ? "Ocultar fonte" : "Ver trecho do livro"}
          </button>
          {showSource && (
            <p className="mt-3 text-sm text-slate-300">
              {question.source.chapter} · página {question.source.page} · {question.source.paragraph_id} ·{" "}
              {question.source.source_file}
            </p>
          )}
        </div>
      )}

      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => {
            setIndex((current) => Math.max(0, current - 1));
            setFeedback(null);
            setSelected(null);
            setShowSource(false);
          }}
          disabled={index === 0}
          className="text-sm text-slate-400 disabled:opacity-40"
        >
          Anterior
        </button>
        {!alreadyAnswered ? (
          <button
            type="button"
            onClick={submit}
            disabled={!selected || saving}
            className="rounded-lg bg-amber-400 px-4 py-2 text-sm font-medium text-slate-950 disabled:opacity-50"
          >
            Responder
          </button>
        ) : (
          <button type="button" onClick={goNext} className="rounded-lg bg-amber-400 px-4 py-2 text-sm font-medium text-slate-950">
            {index + 1 >= attempt.question_count ? "Finalizar" : "Próxima"}
          </button>
        )}
      </div>

      <Link to={`/conteudo/${question.source.chapter_id}`} className="block text-sm text-slate-500 hover:text-amber-300">
        Ver conteúdo relacionado →
      </Link>
    </section>
  );
}
