#!/usr/bin/env python3
"""Validation-only sensitivity analysis excluding training-text overlap.

This does not change the deployed artifact or select a model using test labels.
"""

import sys
from pathlib import Path

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, f1_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hausalens.modeling import build_linear_model, build_word_nb, normalize_text


def main():
    train = pd.read_csv(ROOT / "data/raw/train.tsv", sep="\t").dropna().drop_duplicates()
    dev = pd.read_csv(ROOT / "data/raw/dev.tsv", sep="\t").dropna().drop_duplicates()
    train_texts = set(train.tweet.map(normalize_text))
    clean = dev.loc[~dev.tweet.map(normalize_text).isin(train_texts)]
    candidates = [
        ("Majority baseline", DummyClassifier(strategy="most_frequent")),
        ("Word unigram + NB", build_word_nb()),
        ("Word (1-2) + Linear SVM", build_linear_model("word")),
        ("Character (3-5) + Linear SVM", build_linear_model("char")),
        ("Hybrid without emoji", build_linear_model("hybrid", remove_emoji=True)),
        ("Hybrid word+character SVM", build_linear_model("hybrid")),
    ]
    rows = []
    for name, model in candidates:
        model.fit(train.tweet, train.label)
        predicted = model.predict(clean.tweet)
        rows.append({"model": name, "validation_examples": len(clean), "excluded_overlap": len(dev) - len(clean), "accuracy": accuracy_score(clean.label, predicted), "macro_f1": f1_score(clean.label, predicted, average="macro")})
    results = pd.DataFrame(rows).sort_values("macro_f1", ascending=False)
    results.to_csv(ROOT / "outputs/validation_sensitivity.csv", index=False, float_format="%.6f")
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
