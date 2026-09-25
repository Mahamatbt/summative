#!/usr/bin/env python3
"""Train baselines and proposed HausaLens model on the official splits."""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from hausalens.modeling import build_linear_model, build_word_nb  # noqa: E402

LABELS = ["negative", "neutral", "positive"]


def read_split(data_dir: Path, name: str) -> pd.DataFrame:
    frame = pd.read_csv(data_dir / f"{name}.tsv", sep="\t")
    frame = frame.dropna(subset=["tweet", "label"]).drop_duplicates().reset_index(drop=True)
    unexpected = set(frame["label"]) - set(LABELS)
    if unexpected:
        raise ValueError(f"Unexpected labels in {name}: {unexpected}")
    return frame


def evaluate(name: str, model, train: pd.DataFrame, dev: pd.DataFrame) -> tuple[dict, object]:
    started = time.perf_counter()
    model.fit(train["tweet"], train["label"])
    prediction = model.predict(dev["tweet"])
    elapsed = time.perf_counter() - started
    metrics = {
        "model": name,
        "accuracy": accuracy_score(dev["label"], prediction),
        "macro_precision": precision_score(dev["label"], prediction, average="macro", zero_division=0),
        "macro_recall": recall_score(dev["label"], prediction, average="macro", zero_division=0),
        "macro_f1": f1_score(dev["label"], prediction, average="macro"),
        "weighted_f1": f1_score(dev["label"], prediction, average="weighted"),
        "train_seconds": elapsed,
    }
    print(f"{name:28s} dev macro-F1={metrics['macro_f1']:.4f} ({elapsed:.1f}s)")
    return metrics, model


def save_confusion(y_true, y_pred, output: Path) -> None:
    matrix = confusion_matrix(y_true, y_pred, labels=LABELS)
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    sns.heatmap(matrix, annot=True, fmt=",d", cmap="YlGn", cbar=False, ax=ax)
    ax.set(xlabel="Predicted", ylabel="True", title="HausaLens held-out test confusion matrix")
    ax.set_xticklabels(LABELS)
    ax.set_yticklabels(LABELS, rotation=0)
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_experiment_chart(results: pd.DataFrame, output: Path) -> None:
    ordered = results.sort_values("macro_f1")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    colors = ["#8CA58E"] * len(ordered)
    colors[-1] = "#D98927"
    bars = ax.barh(ordered["model"], ordered["macro_f1"], color=colors)
    ax.set(xlabel="Validation macro-F1", xlim=(0, 1), title="Model comparison on the fixed validation split")
    ax.bar_label(bars, labels=[f"{v:.3f}" for v in ordered["macro_f1"]], padding=5)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_per_class_chart(report: dict, output: Path) -> None:
    values = [report[label]["f1-score"] for label in LABELS]
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    bars = ax.bar(LABELS, values, color=["#A64B35", "#8CA58E", "#D98927"])
    ax.bar_label(bars, labels=[f"{value:.3f}" for value in values], padding=5)
    ax.set(ylabel="Held-out F1", ylim=(0, 1), title="Per-class performance exposes the neutral gap")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "figures").mkdir(exist_ok=True)
    (args.output_dir / "models").mkdir(exist_ok=True)

    train = read_split(args.data_dir, "train")
    dev = read_split(args.data_dir, "dev")
    test = read_split(args.data_dir, "test")

    experiments = [
        ("Majority baseline", DummyClassifier(strategy="most_frequent")),
        ("Word unigram + NB", build_word_nb()),
        ("Word (1-2) + Linear SVM", build_linear_model("word")),
        ("Character (3-5) + Linear SVM", build_linear_model("char")),
        ("Hybrid without emoji", build_linear_model("hybrid", remove_emoji=True)),
        ("Hybrid word+character SVM", build_linear_model("hybrid")),
    ]

    rows = []
    trained = {}
    for name, model in experiments:
        metrics, fitted = evaluate(name, model, train, dev)
        rows.append(metrics)
        trained[name] = fitted

    results = pd.DataFrame(rows).sort_values("macro_f1", ascending=False)
    results.to_csv(args.output_dir / "experiment_results.csv", index=False, float_format="%.6f")
    save_experiment_chart(results, args.output_dir / "figures" / "experiment_comparison.png")

    winner = str(results.iloc[0]["model"])
    final_model = trained[winner]
    combined = pd.concat([train, dev], ignore_index=True)
    final_model.fit(combined["tweet"], combined["label"])
    test_prediction = final_model.predict(test["tweet"])
    report = classification_report(test["label"], test_prediction, labels=LABELS, output_dict=True, zero_division=0)
    test_metrics = {
        "selected_model": winner,
        "selection_rule": "highest validation macro-F1; test evaluated once after refit on train+dev",
        "accuracy": accuracy_score(test["label"], test_prediction),
        "macro_precision": precision_score(test["label"], test_prediction, average="macro", zero_division=0),
        "macro_recall": recall_score(test["label"], test_prediction, average="macro", zero_division=0),
        "macro_f1": f1_score(test["label"], test_prediction, average="macro"),
        "weighted_f1": f1_score(test["label"], test_prediction, average="weighted"),
        "classification_report": report,
        "split_rows_after_deduplication": {
            "train": len(train), "validation": len(dev), "test": len(test), "train_plus_validation": len(combined)
        },
        "runtime": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "platform": platform.platform(),
        },
    }
    (args.output_dir / "test_metrics.json").write_text(json.dumps(test_metrics, indent=2), encoding="utf-8")

    predictions = test.assign(prediction=test_prediction)
    predictions["correct"] = predictions["label"] == predictions["prediction"]
    predictions.to_csv(args.output_dir / "test_predictions.csv", index=False)
    errors = predictions.loc[~predictions["correct"]].copy()
    errors.to_csv(args.output_dir / "error_examples.csv", index=False)
    pd.DataFrame(confusion_matrix(test["label"], test_prediction, labels=LABELS), index=LABELS, columns=LABELS).to_csv(
        args.output_dir / "confusion_matrix.csv"
    )
    save_confusion(test["label"], test_prediction, args.output_dir / "figures" / "confusion_matrix.png")
    save_per_class_chart(report, args.output_dir / "figures" / "per_class_f1.png")
    joblib.dump(final_model, args.output_dir / "models" / "hausalens.joblib", compress=3)

    summary = {
        "dataset": "NaijaSenti Hausa v1.0",
        "license": "CC BY 4.0",
        "labels": LABELS,
        "selected_model": winner,
        "model_description": (
            "Character 3-5 gram TF-IDF with a class-balanced linear support-vector machine"
            if winner.startswith("Character")
            else winner
        ),
        "test_macro_f1": test_metrics["macro_f1"],
        "test_accuracy": test_metrics["accuracy"],
    }
    (args.output_dir / "model_card.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
