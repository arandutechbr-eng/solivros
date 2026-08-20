import { splitStimulus } from "../lib/stimulus";

export function StimulusBlock({
  stimulus,
  questionAnchor = "questao",
  showJump = true,
}: {
  stimulus: string;
  questionAnchor?: string;
  showJump?: boolean;
}) {
  const { instruction, label, title, passage } = splitStimulus(stimulus);

  return (
    <article className="rounded-2xl border border-amber-400/30 bg-slate-900 p-5">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs font-medium uppercase tracking-wide text-amber-300">Texto de apoio</p>
        {showJump && (
          <a href={`#${questionAnchor}`} className="text-xs font-medium text-amber-300 hover:underline">
            Ir para a questão →
          </a>
        )}
      </div>
      {instruction && (
        <p className="rounded-xl bg-amber-400 px-4 py-3 text-sm font-semibold leading-6 text-slate-950">
          {instruction}
        </p>
      )}
      {label && <p className="mt-4 text-sm font-semibold uppercase tracking-wide text-white">{label}</p>}
      {title && <p className="mt-4 text-base font-semibold leading-6 text-white">{title}</p>}
      {passage && (
        <p
          className={`whitespace-pre-wrap text-sm leading-7 text-slate-300 ${
            instruction || label || title ? "mt-3" : ""
          }`}
        >
          {passage}
        </p>
      )}
    </article>
  );
}
