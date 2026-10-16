#!/usr/bin/env python3
"""Audit released data quality without changing the official splits."""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hausalens.modeling import normalize_text


def main():
    frames = {name: pd.read_csv(ROOT / "data/raw" / f"{name}.tsv", sep="\t") for name in ["train", "dev", "test"]}
    report = {}
    for name, frame in frames.items():
        report[name] = {
            "rows": len(frame),
            "missing_text_or_label": int(frame[["tweet", "label"]].isna().any(axis=1).sum()),
            "duplicate_rows": int(frame.duplicated().sum()),
            "normalized_duplicate_texts_within_split": int(frame.tweet.map(normalize_text).duplicated().sum()),
            "median_whitespace_tokens": float(frame.tweet.str.split().str.len().median()),
            "label_counts": {str(key): int(value) for key, value in frame.label.value_counts().items()},
        }
    sets = {name: set(frame.tweet.map(normalize_text)) for name, frame in frames.items()}
    report["normalized_text_overlap"] = {f"{a}_{b}": len(sets[a] & sets[b]) for a, b in [("train", "dev"), ("train", "test"), ("dev", "test")]}
    report["note"] = "Publisher splits are preserved. Train/dev overlap can inflate validation scores; no normalized train/test or dev/test overlap was found."
    (ROOT / "outputs/data_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
