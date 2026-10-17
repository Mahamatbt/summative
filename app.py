"""Streamlit interface for HausaLens."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from hausalens.modeling import predict_with_evidence  # noqa: E402

st.set_page_config(page_title="HausaLens", page_icon="◉", layout="wide")

st.markdown(
    """
<style>
  .stApp { background: #f7f2e8; }
  .block-container { max-width: 1080px; padding-top: 2.4rem; }
  h1, h2, h3 { color: #16351f; letter-spacing: -0.02em; }
  .eyebrow { color:#8a4f11; font-weight:700; letter-spacing:.12em; text-transform:uppercase; font-size:.78rem; }
  .hero { padding: 2rem 2.2rem; border-radius: 24px; background:linear-gradient(135deg,#143b25,#245c37); color:#fff; margin-bottom:1.5rem; box-shadow:0 16px 40px #173a2422; }
  .hero h1 { color:#fff; font-size:3.1rem; margin:.15rem 0 .5rem; }
  .hero p { max-width:720px; color:#e7f2e8; font-size:1.08rem; }
  .chip { display:inline-block; background:#f4b942; color:#26351f; border-radius:999px; padding:.35rem .7rem; margin:.2rem .25rem .2rem 0; font-weight:700; font-size:.8rem; }
  .result { padding:1.4rem; border:1px solid #d4d8cc; border-radius:18px; background:#fffaf2; }
  .metric-note { color:#5e6b61; font-size:.85rem; }
  footer {visibility:hidden;}
</style>
<div class="hero">
  <div class="eyebrow" style="color:#f4b942">Low-resource NLP · Nigeria</div>
  <h1>HausaLens</h1>
  <p>Explore sentiment in Hausa social-media text with a model trained on 16,849 human-annotated NaijaSenti tweets. See the prediction, relative model confidence, and the text patterns that influenced it.</p>
  <span class="chip">Hausa</span><span class="chip">3 classes</span><span class="chip">No external API</span>
</div>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load_assets():
    model = joblib.load(ROOT / "outputs" / "models" / "hausalens.joblib")
    card = json.loads((ROOT / "outputs" / "model_card.json").read_text(encoding="utf-8"))
    return model, card


model, card = load_assets()
demo_choice = str(st.query_params.get("demo", "")).title()
if demo_choice not in {"Positive", "Neutral", "Negative"}:
    demo_choice = "Positive"

left, right = st.columns([1.35, 0.65], gap="large")
with left:
    st.subheader("Classify a Hausa message")
    examples = {
        "Positive": "Allah ya saka da alheri, na gode sosai!",
        "Neutral": "Za a fara taron da karfe goma na safe.",
        "Negative": "Wannan abu ya bata min rai sosai.",
    }
    selected = st.segmented_control("Try an example", list(examples), default=demo_choice)
    message = st.text_area(
        "Hausa text",
        value=examples[selected] if selected else "",
        height=150,
        placeholder="Rubuta saƙonka a nan…",
        max_chars=1000,
    )
    classify = st.button("Analyze sentiment", type="primary", use_container_width=True) or bool(st.query_params.get("demo"))

    if classify:
        try:
            result = predict_with_evidence(model, message)
        except ValueError as exc:
            st.warning(str(exc))
        else:
            icons = {"positive": "↗", "neutral": "→", "negative": "↘"}
            with st.container(border=True):
                st.metric("Prediction", f"{icons[result['label']]} {result['label'].title()}")
                st.progress(result["relative_confidence"], text=f"Relative confidence {result['relative_confidence']:.0%}")
                st.caption("Relative confidence is derived from SVM margins and is not a calibrated probability.")
                st.write("**Influential text patterns**")
                if result["evidence"]:
                    chips = " ".join(f"`{item['feature']}`" for item in result["evidence"])
                    st.markdown(chips)
                else:
                    st.write("No recognized feature strongly supported this class.")

with right:
    st.subheader("Model card")
    st.metric("Held-out macro-F1", f"{card['test_macro_f1']:.1%}")
    st.metric("Held-out accuracy", f"{card['test_accuracy']:.1%}")
    st.write("**Model**  ", card.get("model_description", card["selected_model"]))
    st.write("**Labels**  ", " · ".join(card["labels"]))
    st.write("**Dataset**  ", card["dataset"])
    st.caption("Research prototype. Social-media language changes over time; sarcasm, mixed sentiment, dialect variation, and unseen domains remain difficult.")

with st.expander("How HausaLens works"):
    st.write(
        "The selected classifier represents text with character 3–5 grams in TF-IDF space, then learns "
        "a class-balanced linear support-vector machine. Model selection compared this approach with a "
        "majority baseline, word features, Naive Bayes, and hybrid word-character features on the fixed "
        "validation split. Character features help capture spelling variation and informal writing. The "
        "model runs locally inside this application."
    )

with st.expander("Responsible use and data"):
    st.write(
        "HausaLens is not suitable for decisions about individuals. Its training data are public tweets "
        "released in the NaijaSenti research dataset under CC BY 4.0. User input is processed for inference "
        "and is not intentionally stored by this app."
    )

st.markdown("[Watch the student's project demonstration on YouTube](https://youtu.be/g8qN6C-GF6k)")
