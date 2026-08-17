import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getContentBook } from "../services/content";
import type { ContentBook } from "../types/content";

export function StudyBookPage() {
  const [book, setBook] = useState<ContentBook | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getContentBook()
      .then(setBook)
      .catch(() => setError("Não foi possível carregar o conteúdo do livro."));
  }, []);

  if (error) {
    return <p className="text-red-700">{error}</p>;
  }

  if (!book) {
    return <p className="text-slate-500">Carregando conteúdo...</p>;
  }

  return (
    <section className="space-y-8">
      <div>
        <p className="text-sm font-medium uppercase tracking-wide text-teal-800">Estudos</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">{book.title}</h1>
        <p className="mt-2 text-slate-600">{book.subtitle}</p>
        <p className="mt-1 text-sm text-slate-500">Fonte original: {book.source_file}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Stat label="Capítulos / tópicos" value={book.chapter_count} />
        <Stat label="Blocos de conteúdo" value={book.paragraph_count} />
        <Stat label="Questões no original" value={book.question_count} />
      </div>

      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-5 py-4">
          <h2 className="font-medium text-slate-900">Capítulos</h2>
        </div>
        <ul>
          {book.chapters.map((chapter) => (
            <li key={chapter.id} className="border-b border-slate-100 last:border-0">
              <Link
                to={`/study/chapters/${chapter.id}`}
                className="flex items-center justify-between px-5 py-4 hover:bg-slate-50"
              >
                <div>
                  <p className="font-medium text-slate-900">
                    {chapter.number}. {chapter.title}
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    Páginas {chapter.start_page}–{chapter.end_page} · {chapter.paragraph_count} trechos ·{" "}
                    {chapter.question_count} questões
                  </p>
                </div>
                <span className="text-sm text-teal-800">Abrir →</span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}
