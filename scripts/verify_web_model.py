#!/usr/bin/env python3
"""Compare browser and Python inference without retraining or tuning the model."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hausalens.modeling import normalize_text  # noqa: E402


def main() -> None:
    frame = pd.read_csv(ROOT / "data/raw/test.tsv", sep="\t").dropna(subset=["tweet", "label"]).drop_duplicates()
    edge_cases = [
        "Allah ya saka da alheri, na gode sosai!",
        "Za a fara taron da karfe goma na safe.",
        "Wannan abu ya bata min rai sosai.",
        "nawa kuke saida blander din nan ma zan dinga markade acikinta",
        "  @Ali   SAƘO mai kyau 😊 https://example.com  ",
        "a i ƙ 😊 ba ba ba ba",
        "@Mālam_123 @ƙ123 www.example.org?x=1",
        "na\u0085gode\u001csosai\u3000!",
        "https://example.com😊 aaaa",
    ]
    texts = frame["tweet"].tolist() + edge_cases
    artifact = ROOT / "outputs/models/hausalens.joblib"
    model = joblib.load(artifact)
    expected = model.predict(texts)
    expected_margins = model.decision_function(texts)
    completed = subprocess.run(
        ["node", str(ROOT / "scripts/predict_web.mjs")],
        input=json.dumps(texts, ensure_ascii=False), capture_output=True, text=True, check=True,
    )
    actual = json.loads(completed.stdout)
    mismatches = sum(item["label"] != label for item, label in zip(actual, expected))
    normalization_mismatches = sum(item["normalized_text"] != normalize_text(text) for item, text in zip(actual, texts))
    actual_margins = np.array([item["margins"] for item in actual])
    delta = float(np.max(np.abs(expected_margins - actual_margins)))
    assert len(actual) == len(texts)
    assert mismatches == 0, f"{mismatches} prediction mismatches"
    assert normalization_mismatches == 0, f"{normalization_mismatches} normalization mismatches"
    assert delta < 1e-10, f"Margin drift: {delta}"
    summary = {
        "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        "test_examples": len(frame), "additional_edge_cases": len(edge_cases),
        "prediction_mismatches": mismatches, "normalization_mismatches": normalization_mismatches,
        "maximum_absolute_margin_difference": delta,
        "purpose": "Implementation parity only; no model selection, training, or tuning on test data.",
    }
    (ROOT / "outputs/web_parity.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
