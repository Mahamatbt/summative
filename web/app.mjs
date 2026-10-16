import { createPredictor } from "./model.mjs";

const examples = {
  positive: "Allah ya saka da alheri, na gode sosai!",
  neutral: "Za a fara taron da karfe goma na safe.",
  negative: "Wannan abu ya bata min rai sosai.",
  failure: "nawa kuke saida blander din nan ma zan dinga markade acikinta",
};
const message = document.querySelector("#message");
const analyze = document.querySelector("#analyze");
const status = document.querySelector("#status");
const count = document.querySelector("#count");
const updateCount = () => { count.textContent = `${message.value.length} / 1000`; };
message.addEventListener("input", updateCount);
updateCount();
for (const button of document.querySelectorAll("[data-example]")) {
  button.addEventListener("click", () => {
    message.value = examples[button.dataset.example];
    for (const other of document.querySelectorAll("[data-example]")) other.setAttribute("aria-pressed", String(other === button));
    document.querySelector("#result").hidden = true;
    updateCount();
    message.focus();
  });
}

try {
  const response = await fetch(new URL("./model.json", import.meta.url));
  if (!response.ok) throw new Error(`Model download failed (${response.status}).`);
  const model = await response.json();
  const predict = createPredictor(model);
  document.querySelector("#macro-f1").textContent = `${(model.card.test_macro_f1 * 100).toFixed(1)}%`;
  document.querySelector("#accuracy").textContent = `${(model.card.test_accuracy * 100).toFixed(1)}%`;
  analyze.disabled = false;
  analyze.textContent = "Analyze sentiment →";
  status.textContent = "Model ready. Predictions run in this browser.";
  document.querySelector("#classify-form").addEventListener("submit", (event) => {
    event.preventDefault();
    try {
      const result = predict(message.value);
      document.querySelector("#prediction").textContent = result.label.charAt(0).toUpperCase() + result.label.slice(1);
      document.querySelector("#confidence").textContent = `${Math.round(result.relative_confidence * 100)}% relative confidence`;
      const distribution = document.querySelector("#distribution");
      distribution.replaceChildren();
      for (const [label, score] of Object.entries(result.scores)) {
        const row = document.createElement("div");
        const name = document.createElement("span"); name.textContent = label;
        const bar = document.createElement("progress"); bar.max = 1; bar.value = score; bar.setAttribute("aria-label", `${label} relative score`);
        const value = document.createElement("span"); value.textContent = `${Math.round(score * 100)}%`;
        row.append(name, bar, value); distribution.append(row);
      }
      const evidence = document.querySelector("#evidence");
      evidence.replaceChildren();
      for (const item of result.evidence) {
        const chip = document.createElement("code"); chip.textContent = item.feature; evidence.append(chip);
      }
      if (!result.evidence.length) evidence.textContent = "No recognized pattern strongly supported this class.";
      const reference = document.querySelector("#reference-note");
      reference.hidden = message.value !== examples.failure;
      reference.textContent = "Known test-set error: the dataset label is neutral; the trained model predicts negative. This example illustrates a measured failure, not an expected correct result.";
      document.querySelector("#result").hidden = false;
      status.textContent = result.recognized_features ? "Analysis complete. Interpret the prediction in context." : "No familiar features found. This prediction is driven by the model's class intercepts and is unreliable.";
    } catch (error) {
      document.querySelector("#result").hidden = true;
      status.textContent = error.message;
    }
  });
} catch (error) {
  status.textContent = `${error.message} Refresh to retry, or run the Python app from the repository.`;
  analyze.textContent = "Model unavailable";
}
