import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getReaderBook } from "../services/books";
import type { ReaderBook } from "../types/book";

export function BookReadPage() {
  const { id } = useParams();
  const bookId = Number(id);
  const [book, setBook] = useState<ReaderBook | null>(null);
  const [index, setIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getReaderBook(bookId)
      .then((data) => {
        setBook(data);
        setIndex(0);
      })
      .catch(() => setError("Este livro ainda não está publicado."));
  }, [bookId]);

  if (error) {
    return (
      <div className="space-y-3">
        <p className="text-slate-600">{error}</p>
        <Link to={`/books/${bookId}`} className="text-sm text-teal-800 hover:underline">
          Voltar ao livro
        </Link>
      </div>
    );
  }

  if (!book) {
    return <p className="text-slate-500">Carregando leitor...</p>;
  }

  const chapter = book.chapters[index];
  const previous = index > 0 ? book.chapters[index - 1] : null;
  const next = index < book.chapters.length - 1 ? book.chapters[index + 1] : null;

  return (
    <article className="mx-auto max-w-2xl space-y-10">
      <header className="space-y-2 text-center">
        <h1 className="font-serif text-4xl text-slate-900">{book.title}</h1>
        <p className="text-slate-600">{book.author}</p>
      </header>

      <nav className="rounded-lg border border-slate-200 bg-white p-4">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Índice</p>
        <ol className="space-y-1">
          {book.chapters.map((item, chapterIndex) => (
            <li key={item.id}>
              <button
                type="button"
                onClick={() => setIndex(chapterIndex)}
                className={`text-left text-sm ${chapterIndex === index ? "font-medium text-teal-800" : "text-slate-600 hover:underline"}`}
              >
                {item.title}
              </button>
            </li>
          ))}
        </ol>
      </nav>

      {chapter && (
        <section className="space-y-6">
          <h2 className="font-serif text-2xl text-slate-900">{chapter.title}</h2>
          {chapter.paragraphs.map((paragraph) => (
            <p
              key={paragraph.id}
              className={
                paragraph.type === "heading" || paragraph.type === "subheading"
                  ? "font-serif text-xl text-slate-900"
                  : paragraph.type === "quote"
                    ? "border-l-2 border-slate-300 pl-4 font-serif italic text-slate-700"
                    : "font-serif text-lg leading-8 text-slate-800"
              }
            >
              {paragraph.content}
            </p>
          ))}
        </section>
      )}

      <div className="flex justify-between border-t border-slate-200 pt-6 text-sm">
        {previous ? (
          <button type="button" onClick={() => setIndex(index - 1)} className="text-teal-800 hover:underline">
            ← {previous.title}
          </button>
        ) : (
          <span />
        )}
        {next ? (
          <button type="button" onClick={() => setIndex(index + 1)} className="text-teal-800 hover:underline">
            {next.title} →
          </button>
        ) : (
          <span />
        )}
      </div>
    </article>
  );
}
