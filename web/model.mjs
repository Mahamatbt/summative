// A numerical port of the trained scikit-learn char_wb TF-IDF + LinearSVC.
// No rules or example-specific labels are used to predict sentiment.
const PY_SPACE = /[\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+/gu;

export function normalizeText(value) {
  return String(value)
    .replace(/https?:\/\/\S+|www\.\S+/giu, " URL ")
    .replace(/@[\p{L}\p{N}_]+/gu, " USER ")
    .replace(PY_SPACE, " ")
    .replace(/^ +| +$/g, "")
    .toLowerCase();
}

export function createPredictor(data) {
  if (data.format_version !== 1) throw new Error("Unsupported model format");
  const vocabulary = new Map(data.features.map((feature, index) => [feature, index]));

  return function predict(text) {
    const normalized = normalizeText(text);
    if (!normalized) throw new Error("Enter some Hausa text before classifying.");
    const counts = new Map();
    for (const word of normalized.split(" ")) {
      const letters = Array.from(` ${word} `);
      for (let n = data.ngram_range[0]; n <= data.ngram_range[1]; n++) {
        let offset = 0;
        do {
          const feature = letters.slice(offset, offset + n).join("");
          const index = vocabulary.get(feature);
          if (index !== undefined) counts.set(index, (counts.get(index) || 0) + 1);
          offset++;
        } while (offset + n <= letters.length);
        if (letters.length <= n) break;
      }
    }
    let squareSum = 0;
    const vector = [];
    for (const [index, count] of counts) {
      const value = (data.sublinear_tf ? 1 + Math.log(count) : count) * data.idf[index];
      squareSum += value * value;
      vector.push([index, value]);
    }
    const norm = Math.sqrt(squareSum) || 1;
    for (const entry of vector) entry[1] /= norm;
    const margins = data.intercepts.map((intercept, cls) =>
      vector.reduce((score, [index, value]) => score + value * data.coefficients[cls][index], intercept),
    );
    const best = margins.indexOf(Math.max(...margins));
    const exponentials = margins.map((value) => Math.exp(value - margins[best]));
    const denominator = exponentials.reduce((sum, value) => sum + value, 0);
    const relative = exponentials.map((value) => value / denominator);
    const evidence = vector
      .map(([index, value]) => ({ feature: data.features[index], contribution: value * data.coefficients[best][index] }))
      .filter((item) => item.contribution > 0)
      .sort((a, b) => b.contribution - a.contribution)
      .slice(0, 6);
    return {
      label: data.classes[best],
      margins,
      relative_confidence: relative[best],
      scores: Object.fromEntries(data.classes.map((label, index) => [label, relative[index]])),
      normalized_text: normalized,
      recognized_features: vector.length,
      evidence,
    };
  };
}
