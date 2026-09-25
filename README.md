# HausaLens

HausaLens is a reproducible three-class sentiment classifier for informal Hausa social-media text. It was built as an individual African NLP capstone with a real human-annotated dataset, six controlled experiments, held-out evaluation, error analysis, and a Streamlit interface that runs the trained model locally without an external prediction API.

## Project links

- **Live application:** pending public deployment; run locally with the commands below
- **PDF report:** [`output/pdf/hausalens_capstone_report.pdf`](output/pdf/hausalens_capstone_report.pdf)
- **Demo video:** [`demo/hausalens_demo.mp4`](demo/hausalens_demo.mp4) after generation

## Result at a glance

The selected model is a character 3–5 gram TF-IDF representation with a class-balanced linear SVM. Model choice used the fixed validation set; the official test set was evaluated once after refitting on train + validation.

| Metric | Held-out test result |
|---|---:|
| Accuracy | 0.7658 |
| Macro precision | 0.7672 |
| Macro recall | 0.7665 |
| Macro-F1 | **0.7649** |
| Weighted-F1 | 0.7645 |

The positive class is easiest (F1 0.8446); neutral is hardest (F1 0.7044). This is a research prototype, not a tool for making decisions about people.

## Why this is a machine-learning project

HausaLens does not call a hosted classifier or chatbot. `scripts/train.py` fits every model on the official NaijaSenti Hausa training split, selects among six configurations on validation macro-F1, refits the winner, evaluates once on the held-out test split, and serializes the resulting pipeline for inference. The web app loads that artifact and exposes local linear-feature evidence for each prediction.

## Dataset

The project uses the Hausa subset of [NaijaSenti](https://github.com/hausanlp/NaijaSenti), a naturally occurring, human-annotated Twitter sentiment corpus released under CC BY 4.0. The downloaded release contains 22,152 examples:

| Split | Rows | Negative | Neutral | Positive |
|---|---:|---:|---:|---:|
| Train | 14,172 | 4,573 | 4,912 | 4,687 |
| Validation | 2,677 | 894 | 896 | 887 |
| Test | 5,303 | 1,759 | 1,789 | 1,755 |

Raw tweets are intentionally excluded from this repository. The download script retrieves the official split files and validates row counts.

## Repository structure

```text
app.py                         Streamlit application
src/hausalens/modeling.py      normalization, model factories, explanations
scripts/download_data.py       official-data downloader with row checks
scripts/train.py               experiments, selection, final evaluation
scripts/analyze_errors.py      descriptive error slices
scripts/build_report.py        PDF report generator
scripts/build_demo.py          narrated demonstration video generator
tests/                         preprocessing and inference tests
outputs/                       metrics, figures, predictions, trained model
output/pdf/                    final report
report/                        report source notes
demo/                          video and script
```

## Reproduce the project

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/download_data.py
python scripts/train.py
python scripts/analyze_errors.py
pytest -q
streamlit run app.py
```

Training is CPU-friendly and the serialized model is about 1.3 MB. The exact run reported here used Python 3.13.0 and scikit-learn 1.8.0 on Apple silicon.

## Experiments

| Configuration | Validation macro-F1 |
|---|---:|
| Majority baseline | 0.1672 |
| Word unigram TF-IDF + Multinomial NB | 0.7163 |
| Word 1–2 gram TF-IDF + linear SVM | 0.7432 |
| **Character 3–5 gram TF-IDF + linear SVM** | **0.7698** |
| Hybrid word + character, emoji removed | 0.7664 |
| Hybrid word + character | 0.7663 |

The character-only model slightly outperformed both hybrid variants. Adding more feature families was not automatically better, and removing emoji did not produce a meaningful gain.

## Responsible use and limitations

- The model was trained on public social-media text, not reviews, call-center messages, or formal Hausa; cross-domain performance was not measured.
- Neutral statements, negation, rhetorical questions, sarcasm, mixed sentiment, code-switching, dialectal variation, and evolving slang remain difficult.
- The interface reports a softmax transformation of SVM margins as **relative confidence**, not a calibrated probability.
- Predictions must not be used to profile people or make high-impact decisions.
- No native-speaker audit of the model’s final errors was available for this capstone; qualitative interpretations are therefore conservative.

See [`DATA_CARD.md`](DATA_CARD.md) and [`MODEL_CARD.md`](MODEL_CARD.md) for details.

## Attribution

NaijaSenti is credited to Muhammad et al. (2022):

> Shamsuddeen Hassan Muhammad et al. “NaijaSenti: A Nigerian Twitter Sentiment Corpus for Multilingual Sentiment Analysis.” LREC 2022, pp. 590–602.

The dataset is CC BY 4.0. Project source code is MIT licensed. Full academic references appear in the PDF report.

