"""Shared text processing, modelling, and explanation utilities."""

from __future__ import annotations

import re
from typing import Any

import numpy as np
from scipy.special import softmax
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

URL_RE = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
USER_RE = re.compile(r"@\w+", flags=re.UNICODE)
SPACE_RE = re.compile(r"\s+")


def normalize_text(text: str, *, remove_emoji: bool = False) -> str:
    """Apply conservative, reproducible normalization.

    Case, Hausa characters, punctuation, hashtags, and emoji are retained because
    they can carry sentiment. URLs and account names are replaced with stable tokens.
    The optional emoji ablation is used only in one controlled experiment.
    """

    text = str(text).strip()
    text = URL_RE.sub(" URL ", text)
    text = USER_RE.sub(" USER ", text)
    if remove_emoji:
        text = "".join(ch for ch in text if ord(ch) < 10_000)
    return SPACE_RE.sub(" ", text).strip().lower()


def build_word_nb() -> Pipeline:
    from sklearn.naive_bayes import MultinomialNB

    return Pipeline(
        [
            (
                "features",
                TfidfVectorizer(
                    preprocessor=normalize_text,
                    ngram_range=(1, 1),
                    min_df=2,
                    max_features=35_000,
                    sublinear_tf=True,
                ),
            ),
            ("classifier", MultinomialNB(alpha=0.7)),
        ]
    )


def build_linear_model(mode: str = "hybrid", *, remove_emoji: bool = False) -> Pipeline:
    """Create word, character, or hybrid TF-IDF + linear SVM model."""

    preprocessor = (
        (lambda value: normalize_text(value, remove_emoji=True))
        if remove_emoji
        else normalize_text
    )
    word = TfidfVectorizer(
        preprocessor=preprocessor,
        analyzer="word",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.995,
        max_features=55_000,
        sublinear_tf=True,
        strip_accents=None,
    )
    char = TfidfVectorizer(
        preprocessor=preprocessor,
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=3,
        max_features=65_000,
        sublinear_tf=True,
    )
    if mode == "word":
        features: Any = word
    elif mode == "char":
        features = char
    elif mode == "hybrid":
        features = FeatureUnion([("word", word), ("char", char)])
    else:
        raise ValueError(f"Unknown feature mode: {mode}")

    return Pipeline(
        [
            ("features", features),
            (
                "classifier",
                LinearSVC(C=1.5, class_weight="balanced", max_iter=5_000),
            ),
        ]
    )


def decision_confidence(scores: np.ndarray) -> np.ndarray:
    """Convert SVM margins to an intuitive relative score (not calibration)."""

    return softmax(np.asarray(scores), axis=-1)


def predict_with_evidence(model: Pipeline, text: str, top_k: int = 6) -> dict[str, Any]:
    """Predict sentiment and expose the strongest local linear feature effects."""

    if not str(text).strip():
        raise ValueError("Enter some Hausa text before classifying.")

    features = model.named_steps["features"]
    classifier = model.named_steps["classifier"]
    row = features.transform([text])
    scores = classifier.decision_function(row)[0]
    relative = decision_confidence(scores)
    best_idx = int(np.argmax(scores))
    label = str(classifier.classes_[best_idx])

    feature_names = features.get_feature_names_out()
    contributions = row.multiply(classifier.coef_[best_idx]).toarray()[0]
    nonzero = np.flatnonzero(contributions)
    ranked = nonzero[np.argsort(contributions[nonzero])[::-1]] if nonzero.size else []
    evidence = []
    for idx in ranked:
        if contributions[idx] <= 0:
            break
        name = str(feature_names[idx]).replace("word__", "").replace("char__", "")
        evidence.append({"feature": name, "contribution": float(contributions[idx])})
        if len(evidence) >= top_k:
            break

    return {
        "label": label,
        "relative_confidence": float(relative[best_idx]),
        "scores": {str(cls): float(value) for cls, value in zip(classifier.classes_, relative)},
        "evidence": evidence,
        "normalized_text": normalize_text(text),
    }

