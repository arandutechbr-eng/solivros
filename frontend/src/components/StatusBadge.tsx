import type { BookStatus } from "../types/book";

const LABELS: Record<BookStatus, string> = {
  UPLOADED: "Enviado",
  PROCESSING: "Processando",
  EXTRACTED: "Extraído",
  STRUCTURED: "Estruturado",
  REVIEW: "Em revisão",
  APPROVED: "Aprovado",
  PUBLISHED: "Publicado",
  ERROR: "Erro",
};

const STYLES: Record<BookStatus, string> = {
  UPLOADED: "bg-slate-100 text-slate-700",
  PROCESSING: "bg-amber-100 text-amber-800",
  EXTRACTED: "bg-sky-100 text-sky-800",
  STRUCTURED: "bg-indigo-100 text-indigo-800",
  REVIEW: "bg-orange-100 text-orange-800",
  APPROVED: "bg-emerald-100 text-emerald-800",
  PUBLISHED: "bg-teal-100 text-teal-800",
  ERROR: "bg-red-100 text-red-800",
};

export function StatusBadge({ status }: { status: BookStatus }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${STYLES[status]}`}>
      {LABELS[status]}
    </span>
  );
}
