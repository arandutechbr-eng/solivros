export type SplitStimulus = {
  instruction: string | null;
  label: string | null;
  title: string | null;
  passage: string;
};

const INSTRUCTION_RE =
  /^(utilize\s+o\s+texto[\s\S]*?quest(?:ões|oes|õrs)[\s\S]{0,48}?\d+(?:\s*(?:e|a|,|e\s+a)\s*\d+)*)\.?\s*/i;
const LABEL_RE = /^(texto\s+(?:[ivx]+|\d+)\b)\s*/i;
const TITLE_RE =
  /^([^\n.]{8,120}?)(?=\s+(?:No|Na|Nas|Nos|O|A|Os|As|Um|Uma|Mas|Diante|Quando|Em|Esse|Esta|Este|Ao|Após|Depois)\s)/;

function collapseSpaces(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}

export function splitStimulus(stimulus: string): SplitStimulus {
  let rest = stimulus.replace(/^[\u200b\u200c\u200d\ufeff]+/, "").trim();
  let instruction: string | null = null;
  let label: string | null = null;
  let title: string | null = null;

  const instructionMatch = rest.match(INSTRUCTION_RE);
  if (instructionMatch) {
    instruction = collapseSpaces(instructionMatch[0]).replace(/\s*\.?$/, ".");
    rest = rest.slice(instructionMatch[0].length).trim();
  }

  const labelMatch = rest.match(LABEL_RE);
  if (labelMatch) {
    const raw = collapseSpaces(labelMatch[1]);
    label = raw.replace(/^texto/i, "Texto");
    rest = rest.slice(labelMatch[0].length).trim();
  }

  const titleMatch = rest.match(TITLE_RE);
  if (titleMatch) {
    title = collapseSpaces(titleMatch[1]);
    rest = rest.slice(titleMatch[0].length).trim();
  }

  return { instruction, label, title, passage: rest };
}
