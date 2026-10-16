// Batch numerical inference for Python/JavaScript parity checks. Input is stdin.
import { readFileSync } from "node:fs";
import { createPredictor } from "../web/model.mjs";

const model = JSON.parse(readFileSync(new URL("../web/model.json", import.meta.url), "utf8"));
const predict = createPredictor(model);
const texts = JSON.parse(readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(texts.map((text) => {
  const result = predict(text);
  return { label: result.label, margins: result.margins, normalized_text: result.normalized_text };
})));
