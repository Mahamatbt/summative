#!/usr/bin/env python3
"""Export learned TF-IDF/SVM parameters for identical browser-side inference."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    artifact = ROOT / "outputs/models/hausalens.joblib"
    model = joblib.load(artifact)
    features = model.named_steps["features"]
    classifier = model.named_steps["classifier"]
    if features.analyzer != "char_wb" or features.norm != "l2":
        raise ValueError("The browser runtime supports the selected char_wb/L2 model only.")
    card = json.loads((ROOT / "outputs/model_card.json").read_text())
    payload = {
        "format_version": 1,
        "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        "classes": classifier.classes_.tolist(),
        "features": features.get_feature_names_out().tolist(),
        "idf": features.idf_.tolist(),
        "coefficients": classifier.coef_.tolist(),
        "intercepts": classifier.intercept_.tolist(),
        "ngram_range": list(features.ngram_range),
        "sublinear_tf": features.sublinear_tf,
        "card": card,
    }
    output = ROOT / "web/model.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {len(payload['features']):,} learned features ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
