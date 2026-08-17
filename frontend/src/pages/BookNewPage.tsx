import { FormEvent, type ReactNode, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FileDropzone } from "../components/FileDropzone";
import { createBook } from "../services/books";

export function BookNewPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [isbn, setIsbn] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!file) {
      setError("Selecione um PDF.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("title", title);
      form.append("author", author);
      form.append("isbn", isbn);
      form.append("description", description);
      form.append("pdf", file);
      const book = await createBook(form, setProgress);
      navigate(`/books/${book.id}`);
    } catch {
      setError("Falha no upload. Verifique se o arquivo é um PDF válido.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-3xl font-semibold tracking-tight text-slate-900">Novo livro</h1>
      <form onSubmit={(event) => void handleSubmit(event)} className="space-y-5 rounded-lg border border-slate-200 bg-white p-6">
        <Field label="Título">
          <input
            required
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2"
          />
        </Field>
        <Field label="Autor">
          <input
            value={author}
            onChange={(event) => setAuthor(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2"
          />
        </Field>
        <Field label="ISBN">
          <input
            value={isbn}
            onChange={(event) => setIsbn(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2"
          />
        </Field>
        <Field label="Descrição">
          <textarea
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            className="min-h-24 w-full rounded-md border border-slate-300 px-3 py-2"
          />
        </Field>
        <FileDropzone file={file} onFileChange={setFile} />
        {progress > 0 && (
          <div>
            <div className="h-2 overflow-hidden rounded bg-slate-100">
              <div className="h-full bg-teal-700" style={{ width: `${progress}%` }} />
            </div>
            <p className="mt-1 text-xs text-slate-500">{progress}%</p>
          </div>
        )}
        {error && <p className="text-sm text-red-700">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="rounded-md bg-teal-800 px-4 py-2 text-sm font-medium text-white hover:bg-teal-900 disabled:opacity-60"
        >
          {submitting ? "Enviando..." : "Enviar PDF"}
        </button>
      </form>
    </section>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block space-y-1">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}
