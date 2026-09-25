#!/usr/bin/env python3
"""Summarize interpretable error slices from held-out predictions."""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

NEGATION = re.compile(r"\b(?:ba|bai|ban|bamu|bata|baza|kada|ba[kw]a)\b", re.IGNORECASE)
QUESTION = re.compile(r"[?？]|\b(?:me|meyasa|yaushe|wane|ina)\b", re.IGNORECASE)
EMOJI = re.compile(r"[^\x00-\x7F]")


def main() -> None:
    source = Path("outputs/test_predictions.csv")
    output = Path("outputs")
    frame = pd.read_csv(source)
    frame["tokens"] = frame["tweet"].str.split().str.len()
    frame["short_5_tokens_or_less"] = frame["tokens"] <= 5
    frame["contains_negation_marker"] = frame["tweet"].str.contains(NEGATION)
    frame["contains_question_cue"] = frame["tweet"].str.contains(QUESTION)
    frame["contains_non_ascii"] = frame["tweet"].str.contains(EMOJI)
    frame["error"] = ~frame["correct"]

    slices = []
    for column in [
        "short_5_tokens_or_less",
        "contains_negation_marker",
        "contains_question_cue",
        "contains_non_ascii",
    ]:
        for value, group in frame.groupby(column):
            slices.append(
                {
                    "slice": column,
                    "present": bool(value),
                    "items": len(group),
                    "errors": int(group["error"].sum()),
                    "error_rate": float(group["error"].mean()),
                }
            )
    slice_frame = pd.DataFrame(slices)
    slice_frame.to_csv(output / "error_slices.csv", index=False, float_format="%.6f")

    by_class = (
        frame.groupby("label", sort=False)["error"]
        .agg([("items", "size"), ("errors", "sum"), ("error_rate", "mean")])
        .reset_index()
    )
    by_class.to_csv(output / "error_by_class.csv", index=False, float_format="%.6f")

    length_bins = pd.cut(
        frame["tokens"], bins=[0, 5, 10, 20, 40, float("inf")], labels=["1-5", "6-10", "11-20", "21-40", "41+"]
    )
    by_length = frame.assign(length_bin=length_bins).groupby("length_bin", observed=True)["error"].agg(["size", "sum", "mean"])
    by_length.columns = ["items", "errors", "error_rate"]
    by_length.to_csv(output / "error_by_length.csv", float_format="%.6f")

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    bars = ax.bar(by_length.index.astype(str), by_length["error_rate"], color="#2E6A3E")
    ax.bar_label(bars, labels=[f"{v:.1%}" for v in by_length["error_rate"]], padding=4)
    ax.set(xlabel="Tweet length (whitespace tokens)", ylabel="Error rate", ylim=(0, max(by_length["error_rate"]) + 0.1))
    ax.set_title("Held-out errors by message length")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(output / "figures" / "error_by_length.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "overall_error_rate": float(frame["error"].mean()),
        "total_errors": int(frame["error"].sum()),
        "test_items": len(frame),
        "highest_error_class": str(by_class.sort_values("error_rate", ascending=False).iloc[0]["label"]),
        "notes": "Slices are surface-form indicators, not causal explanations or validated linguistic categories.",
    }
    (output / "error_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(slice_frame.to_string(index=False))
    print("\n", by_class.to_string(index=False))
    print("\n", by_length.to_string())


if __name__ == "__main__":
    main()

