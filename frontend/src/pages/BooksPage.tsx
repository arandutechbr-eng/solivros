import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { StatusBadge } from "../components/StatusBadge";
import { deleteBook, listBooks } from "../services/books";
import type { Book } from "../types/book";

export function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setBooks(await listBooks());
    } catch {
      setError("Não foi possível carregar a lista de livros.");
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function handleDelete(book: Book) {
    if (!window.confirm(`Excluir "${book.title}"?`)) return;
    await deleteBook(book.id);
    await load();
  }

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-semibold tracking-tight text-slate-900">Livros</h1>
        <Link
          to="/books/new"
          className="rounded-md bg-teal-800 px-4 py-2 text-sm font-medium text-white hover:bg-teal-900"
        >
          Novo livro
        </Link>
      </div>

      {error && <p className="text-sm text-red-700">{error}</p>}

      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500">
            <tr>
              <th className="px-4 py-3 font-medium">Título</th>
              <th className="px-4 py-3 font-medium">Autor</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Data</th>
              <th className="px-4 py-3 font-medium">Ações</th>
            </tr>
          </thead>
          <tbody>
            {books.map((book) => (
              <tr key={book.id} className="border-t border-slate-100">
                <td className="px-4 py-3 font-medium text-slate-900">{book.title}</td>
                <td className="px-4 py-3 text-slate-600">{book.author || "—"}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={book.status} />
                </td>
                <td className="px-4 py-3 text-slate-600">
                  {new Date(book.created_at).toLocaleDateString("pt-BR")}
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-3">
                    <Link to={`/books/${book.id}`} className="text-teal-800 hover:underline">
                      Abrir
                    </Link>
                    <button type="button" onClick={() => void handleDelete(book)} className="text-red-700 hover:underline">
                      Excluir
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {books.length === 0 && (
              <tr>
                <td className="px-4 py-8 text-slate-500" colSpan={5}>
                  Nenhum livro cadastrado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
