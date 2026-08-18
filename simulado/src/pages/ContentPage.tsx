import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useSubject } from "../context/SubjectContext";
import { getContent } from "../services/simulado";
import type { ContentBook } from "../types";

export function ContentPage() {
  const { subjectId, subject } = useSubject();
  const [book, setBook] = useState<ContentBook | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setBook(null);
    getContent(subjectId)
      .then(setBook)
      .catch(() => setError("Não foi possível carregar o conteúdo do caderno."));
  }, [subjectId]);

  if (error) return <p className="text-rose-300">{error}</p>;
  if (!book) return <p className="text-slate-400">Carregando conteúdo...</p>;

  return (
    <section className="space-y-8">
      <div>
        <p className="text-sm font-medium uppercase tracking-wide text-amber-300">Conteúdo</p>
        <h1 className="mt-1 text-3xl font-semibold text-white">{book.title}</h1>
        <p className="mt-2 text-slate-400">{book.subtitle}</p>
        <p className="mt-1 text-sm text-slate-500">
          Fonte original: {book.source_file} · {book.question_count} questões oficiais
          {subject ? ` · ${subject.title}` : ""}
        </p>
      </div>

      <ul className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
        {book.chapters.map((chapter) => (
          <li key={chapter.id} className="border-b border-slate-800 last:border-0">
            <Link to={`/conteudo/${chapter.id}`} className="flex items-center justify-between px-5 py-4 hover:bg-slate-800/60">
              <div>
                <p className="font-medium text-white">
                  {chapter.number}. {chapter.title}
                </p>
                <p className="mt-1 text-sm text-slate-400">
                  Páginas {chapter.start_page}–{chapter.end_page} · {chapter.question_count} questões
                </p>
              </div>
              <span className="text-sm text-amber-300">Abrir →</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
