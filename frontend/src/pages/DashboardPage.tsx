import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { StatusBadge } from "../components/StatusBadge";
import { listBooks } from "../services/books";
import type { Book } from "../types/book";

export function DashboardPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listBooks()
      .then(setBooks)
      .catch(() => setError("Não foi possível carregar os livros."));
  }, []);

  const total = books.length;
  const processing = books.filter((book) => book.status === "PROCESSING").length;
  const review = books.filter((book) => book.status === "REVIEW").length;
  const published = books.filter((book) => book.status === "PUBLISHED").length;
  const recent = books.slice(0, 5);

  return (
    <section className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-900">Dashboard</h1>
        <p className="mt-2 text-slate-600">Acompanhe o acervo em digitalização e publicação.</p>
      </div>

      {error && <p className="text-sm text-red-700">{error}</p>}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total de livros" value={total} />
        <StatCard label="Em processamento" value={processing} />
        <StatCard label="Em revisão" value={review} />
        <StatCard label="Publicados" value={published} />
      </div>

      <div className="rounded-lg border border-slate-200 bg-white">
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <h2 className="font-medium text-slate-900">Livros recentes</h2>
          <Link to="/books" className="text-sm text-teal-800 hover:underline">
            Ver todos
          </Link>
        </div>
        <ul>
          {recent.length === 0 && <li className="px-5 py-6 text-sm text-slate-500">Nenhum livro ainda.</li>}
          {recent.map((book) => (
            <li key={book.id} className="flex items-center justify-between border-b border-slate-100 px-5 py-3 last:border-0">
              <div>
                <Link to={`/books/${book.id}`} className="font-medium text-slate-900 hover:underline">
                  {book.title}
                </Link>
                <p className="text-sm text-slate-500">{book.author || "Autor não informado"}</p>
              </div>
              <StatusBadge status={book.status} />
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}
