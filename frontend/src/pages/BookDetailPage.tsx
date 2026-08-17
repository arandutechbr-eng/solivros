import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { StatusBadge } from "../components/StatusBadge";
import { approveBook, getBook, getBookStatus, processBook, publishBook } from "../services/books";
import type { Book } from "../types/book";

const ACTIVE_STATUSES = new Set(["UPLOADED", "PROCESSING", "EXTRACTED", "STRUCTURED"]);

export function BookDetailPage() {
  const { id } = useParams();
  const bookId = Number(id);
  const [book, setBook] = useState<Book | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function load() {
    setBook(await getBook(bookId));
  }

  useEffect(() => {
    void load().catch(() => setError("Não foi possível carregar o livro."));
  }, [bookId]);

  useEffect(() => {
    if (!book || !ACTIVE_STATUSES.has(book.status)) return;
    const timer = window.setInterval(() => {
      void getBookStatus(bookId).then((status) => {
        if (status.status !== book.status) {
          void load();
        }
      });
    }, 2000);
    return () => window.clearInterval(timer);
  }, [book, bookId]);

  async function handleProcess() {
    setBusy(true);
    setError(null);
    try {
      await processBook(bookId);
      await load();
    } catch {
      setError("Não foi possível iniciar o processamento.");
    } finally {
      setBusy(false);
    }
  }

  async function handleApprove() {
    setBusy(true);
    setError(null);
    try {
      await approveBook(bookId);
      await load();
    } catch {
      setError("Não foi possível aprovar o livro.");
    } finally {
      setBusy(false);
    }
  }

  async function handlePublish() {
    setBusy(true);
    setError(null);
    try {
      await publishBook(bookId);
      await load();
    } catch {
      setError("Publique somente após aprovar um livro com capítulos e conteúdo.");
    } finally {
      setBusy(false);
    }
  }

  if (!book) {
    return <p className="text-slate-500">{error ?? "Carregando..."}</p>;
  }

  return (
    <section className="space-y-8">
      <div>
        <p className="text-sm text-slate-500">Livro #{book.id}</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">{book.title}</h1>
        <p className="mt-2 text-slate-600">{book.author || "Autor não informado"}</p>
        <div className="mt-3">
          <StatusBadge status={book.status} />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Metric label="Páginas" value={book.page_count ?? "—"} />
        <Metric label="Capítulos" value={book.chapter_count ?? "—"} />
        <Metric label="Parágrafos" value={book.paragraph_count ?? "—"} />
      </div>

      {error && <p className="text-sm text-red-700">{error}</p>}

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          disabled={busy}
          onClick={() => void handleProcess()}
          className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm hover:bg-slate-50 disabled:opacity-60"
        >
          Processar
        </button>
        <Link to={`/books/${book.id}/review`} className="rounded-md bg-teal-800 px-4 py-2 text-sm font-medium text-white hover:bg-teal-900">
          Abrir revisão
        </Link>
        <button
          type="button"
          disabled={busy}
          onClick={() => void handleApprove()}
          className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm hover:bg-slate-50 disabled:opacity-60"
        >
          Aprovar
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => void handlePublish()}
          className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm hover:bg-slate-50 disabled:opacity-60"
        >
          Publicar
        </button>
        <Link to={`/books/${book.id}/read`} className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm hover:bg-slate-50">
          Abrir leitor
        </Link>
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}
