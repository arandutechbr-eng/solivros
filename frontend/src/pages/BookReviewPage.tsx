import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ParagraphEditor } from "../components/ParagraphEditor";
import {
  createChapter,
  createParagraph,
  deleteChapter,
  deleteParagraph,
  getBook,
  listChapters,
  listParagraphs,
  updateChapter,
  updateParagraph,
} from "../services/books";
import type { Book, Chapter, Paragraph, ParagraphType } from "../types/book";

const LOW_CONFIDENCE = 0.8;

export function BookReviewPage() {
  const { id } = useParams();
  const bookId = Number(id);
  const [book, setBook] = useState<Book | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [paragraphs, setParagraphs] = useState<Paragraph[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [title, setTitle] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const selected = useMemo(
    () => chapters.find((chapter) => chapter.id === selectedId) ?? null,
    [chapters, selectedId],
  );

  async function loadChapters(preferredId?: number) {
    const data = await listChapters(bookId);
    setChapters(data);
    const nextId = preferredId ?? selectedId ?? data[0]?.id ?? null;
    setSelectedId(nextId);
    return data;
  }

  async function loadParagraphs(chapterId: number) {
    const data = await listParagraphs(chapterId);
    setParagraphs(data);
  }

  useEffect(() => {
    void getBook(bookId).then(setBook);
    void loadChapters();
  }, [bookId]);

  useEffect(() => {
    if (!selected) {
      setParagraphs([]);
      setTitle("");
      return;
    }
    setTitle(selected.title);
    void loadParagraphs(selected.id);
  }, [selected?.id]);

  async function handleSave() {
    if (!selected) return;
    setSaving(true);
    setMessage(null);
    try {
      await updateChapter(selected.id, { title });
      await Promise.all(paragraphs.map((paragraph) => updateParagraph(paragraph.id, {
        content: paragraph.content,
        type: paragraph.type,
        order: paragraph.order,
      })));
      await loadChapters(selected.id);
      setMessage("Alterações salvas.");
    } catch {
      setMessage("Não foi possível salvar.");
    } finally {
      setSaving(false);
    }
  }

  async function handleAddChapter() {
    const chapter = await createChapter(bookId, `Capítulo ${chapters.length + 1}`);
    await loadChapters(chapter.id);
  }

  async function handleDeleteChapter(chapter: Chapter) {
    if (!window.confirm(`Excluir "${chapter.title}"?`)) return;
    await deleteChapter(chapter.id);
    await loadChapters();
  }

  async function moveChapter(chapter: Chapter, direction: -1 | 1) {
    const index = chapters.findIndex((item) => item.id === chapter.id);
    const target = chapters[index + direction];
    if (!target) return;
    await Promise.all([
      updateChapter(chapter.id, { order: target.order }),
      updateChapter(target.id, { order: chapter.order }),
    ]);
    await loadChapters(chapter.id);
  }

  async function handleAddParagraph() {
    if (!selected) return;
    await createParagraph(selected.id, { content: "", type: "paragraph" });
    await loadParagraphs(selected.id);
  }

  async function handleDeleteParagraph(paragraph: Paragraph) {
    await deleteParagraph(paragraph.id);
    if (selected) await loadParagraphs(selected.id);
  }

  async function moveParagraph(paragraph: Paragraph, direction: -1 | 1) {
    const index = paragraphs.findIndex((item) => item.id === paragraph.id);
    const target = paragraphs[index + direction];
    if (!target) return;
    await Promise.all([
      updateParagraph(paragraph.id, { order: target.order }),
      updateParagraph(target.id, { order: paragraph.order }),
    ]);
    if (selected) await loadParagraphs(selected.id);
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">Revisão</p>
          <h1 className="text-2xl font-semibold text-slate-900">{book?.title ?? "Livro"}</h1>
        </div>
        <div className="flex gap-3">
          <Link to={`/books/${bookId}`} className="text-sm text-slate-600 hover:underline">
            Voltar
          </Link>
          <button
            type="button"
            disabled={saving || !selected}
            onClick={() => void handleSave()}
            className="rounded-md bg-teal-800 px-4 py-2 text-sm font-medium text-white hover:bg-teal-900 disabled:opacity-60"
          >
            {saving ? "Salvando..." : "Salvar alterações"}
          </button>
        </div>
      </div>
      {message && <p className="text-sm text-slate-600">{message}</p>}

      <div className="grid min-h-[70vh] grid-cols-1 overflow-hidden rounded-lg border border-slate-200 bg-white lg:grid-cols-[280px_1fr]">
        <aside className="border-b border-slate-200 p-4 lg:border-b-0 lg:border-r">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Capítulos</h2>
            <button type="button" onClick={() => void handleAddChapter()} className="text-sm text-teal-800">
              + Novo
            </button>
          </div>
          <ul className="space-y-1">
            {chapters.map((chapter, index) => (
              <li key={chapter.id}>
                <button
                  type="button"
                  onClick={() => setSelectedId(chapter.id)}
                  className={`w-full rounded-md px-3 py-2 text-left text-sm ${
                    chapter.id === selectedId ? "bg-teal-50 font-medium text-teal-900" : "hover:bg-slate-50"
                  }`}
                >
                  {chapter.title}
                </button>
                <div className="mb-2 flex gap-2 px-3 text-xs text-slate-500">
                  <button type="button" onClick={() => void moveChapter(chapter, -1)} disabled={index === 0}>
                    ↑
                  </button>
                  <button
                    type="button"
                    onClick={() => void moveChapter(chapter, 1)}
                    disabled={index === chapters.length - 1}
                  >
                    ↓
                  </button>
                  <button type="button" onClick={() => void handleDeleteChapter(chapter)}>
                    Excluir
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </aside>

        <div className="space-y-5 p-6">
          {!selected && <p className="text-slate-500">Crie um capítulo para começar a revisão.</p>}
          {selected && (
            <>
              <label className="block space-y-1">
                <span className="text-sm font-medium text-slate-600">Título</span>
                <input
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  className="w-full rounded-md border border-slate-300 px-3 py-2 text-lg"
                />
              </label>

              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Conteúdo</h2>
                <button type="button" onClick={() => void handleAddParagraph()} className="text-sm text-teal-800">
                  + Parágrafo
                </button>
              </div>

              <div className="space-y-4">
                {paragraphs.map((paragraph, index) => (
                  <article
                    key={paragraph.id}
                    className={`rounded-md border ${
                      paragraph.confidence < LOW_CONFIDENCE ? "border-amber-400 bg-amber-50" : "border-slate-200"
                    }`}
                  >
                    {paragraph.confidence < LOW_CONFIDENCE && (
                      <p className="border-b border-amber-200 px-3 py-2 text-xs font-medium text-amber-800">
                        ⚠ Baixa confiança de OCR
                      </p>
                    )}
                    <ParagraphEditor
                      content={paragraph.content}
                      onChange={(content) =>
                        setParagraphs((current) =>
                          current.map((item) => (item.id === paragraph.id ? { ...item, content } : item)),
                        )
                      }
                    />
                    <div className="flex items-center justify-between gap-3 border-t border-slate-100 px-3 py-2 text-xs text-slate-500">
                      <select
                        value={paragraph.type}
                        onChange={(event) =>
                          setParagraphs((current) =>
                            current.map((item) =>
                              item.id === paragraph.id
                                ? { ...item, type: event.target.value as ParagraphType }
                                : item,
                            ),
                          )
                        }
                        className="rounded border border-slate-300 px-2 py-1"
                      >
                        <option value="paragraph">Parágrafo</option>
                        <option value="heading">Título</option>
                        <option value="subheading">Subtítulo</option>
                        <option value="quote">Citação</option>
                        <option value="footnote">Nota</option>
                        <option value="caption">Legenda</option>
                      </select>
                      <div className="flex gap-2">
                        <button type="button" onClick={() => void moveParagraph(paragraph, -1)} disabled={index === 0}>
                          ↑
                        </button>
                        <button
                          type="button"
                          onClick={() => void moveParagraph(paragraph, 1)}
                          disabled={index === paragraphs.length - 1}
                        >
                          ↓
                        </button>
                        <button type="button" onClick={() => void handleDeleteParagraph(paragraph)}>
                          Excluir
                        </button>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
