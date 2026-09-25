from hausalens.modeling import build_linear_model, normalize_text, predict_with_evidence


def test_normalize_platform_artifacts_and_whitespace():
    assert normalize_text("  @Ali   Na gode https://example.com  ") == "user na gode url"


def test_normalize_preserves_hausa_and_emoji():
    assert normalize_text("SAƘO mai kyau 😊") == "saƙo mai kyau 😊"


def test_small_model_predicts_and_explains():
    model = build_linear_model("hybrid")
    texts = [
        "na gode sosai abin yayi kyau",
        "ina farin ciki da wannan",
        "abin ya bata min rai",
        "wannan ba kyau bane",
        "taron zai fara gobe",
        "an sanar da sabon lokaci",
    ]
    labels = ["positive", "positive", "negative", "negative", "neutral", "neutral"]
    model.fit(texts, labels)
    result = predict_with_evidence(model, "na gode abin yayi kyau")
    assert result["label"] in set(labels)
    assert 0 < result["relative_confidence"] <= 1
    assert result["scores"].keys() == set(labels)

