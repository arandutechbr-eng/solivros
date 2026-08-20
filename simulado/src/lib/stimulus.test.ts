import { expect, test } from "vitest";
import { splitStimulus } from "./stimulus";

test("separa a instrução Utilize o texto do trecho", () => {
  const split = splitStimulus(
    "Utilize o texto a seguir para responder as questões 468 e 469. Na internet, mentiras têm pernas longas Diz o velho ditado",
  );
  expect(split.instruction).toBe("Utilize o texto a seguir para responder as questões 468 e 469.");
  expect(split.label).toBeNull();
  expect(split.passage.startsWith("Na internet")).toBe(true);
});

test("separa o rótulo Texto II", () => {
  const split = splitStimulus(
    "Utilize o texto a seguir para responder as questões de 462 a 462. Texto II O Brasil na memória A viagem tem uma estruturalidade típica.",
  );
  expect(split.instruction).toMatch(/Utilize o texto/i);
  expect(split.label).toBe("Texto II");
  expect(split.passage.startsWith("A viagem") || split.title?.startsWith("O Brasil")).toBe(true);
});

test("separa instrução e título das questões 239 e 240", () => {
  const split = splitStimulus(
    "Utilize o texto a seguir para responder as questões 239 e 240. Lições após um ano de ensino remoto na pandemia No momento em que se tornam ainda mais complexas as discussões",
  );
  expect(split.instruction).toBe("Utilize o texto a seguir para responder as questões 239 e 240.");
  expect(split.title).toBe("Lições após um ano de ensino remoto na pandemia");
  expect(split.passage.startsWith("No momento")).toBe(true);
});
