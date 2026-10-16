# HausaLens

HausaLens is a reproducible three-class sentiment classifier for informal Hausa social-media text. It was built as an individual African NLP capstone with a real human-annotated dataset, six controlled experiments, held-out evaluation, error analysis, a publicly deployed browser application, and an alternative Python Streamlit interface. Both interfaces use the trained model without an external prediction API.

The intended users are researchers, students, and teams exploring aggregate sentiment in Hausa feedback. The model was evaluated on social-media text; use in other domains requires additional evaluation.

## Project links

- **GitHub repository:** [Mahamatbt/summative](https://github.com/Mahamatbt/summative)
- **Live application:** [HausaLens on GitHub Pages](https://mahamatbt.github.io/summative/)
- **PDF report:** [`output/pdf/hausalens_capstone_report.pdf`](output/pdf/hausalens_capstone_report.pdf)
- **Demo video:** pending the student's own 10-15 minute recording. No replacement video has been generated.
- **Recording guide:** [`demo/recording_guide.md`](demo/recording_guide.md)
- **Submission checklist:** [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md)

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

The original raw split files are excluded from version control. The download script retrieves the official files and validates row counts. Evaluation CSVs and qualitative examples include released test text for reproducible error review, with the dataset's attribution and CC BY 4.0 license retained.

A final quality audit found 215 normalized text matches between training and validation, but none between training and test or validation and test. The original results preserve the publisher's splits. A supplementary overlap-free validation comparison is included in `outputs/validation_sensitivity.csv`; the overlap and its effect are disclosed rather than treating the original validation set as fully independent.

## Repository structure

```text
app.py                         Streamlit application
src/hausalens/modeling.py      normalization, model factories, explanations
scripts/download_data.py       official-data downloader with row checks
scripts/train.py               experiments, selection, final evaluation
scripts/analyze_errors.py      descriptive error slices
scripts/audit_data.py          missing values, duplicates, and split overlap
scripts/validate_selection.py  overlap-free validation sensitivity analysis
scripts/export_web_model.py    export the actual learned weights for the browser
scripts/verify_web_model.py    Python/JavaScript numerical parity checks
scripts/verify_deployment.py   live interface checks and screenshot evidence
scripts/build_report.py        PDF report generator
scripts/build_demo.py          narrated demonstration video generator
tests/                         preprocessing and inference tests
outputs/                       metrics, figures, predictions, trained model
output/pdf/                    final report
report/                        report source notes
web/                           public application and browser inference runtime
demo/                          student's recording guide and screenshot evidence
```

## Reproduce the project

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev,report]"
python scripts/download_data.py
python scripts/audit_data.py
python scripts/train.py
python scripts/analyze_errors.py
python scripts/validate_selection.py
pytest -q
streamlit run app.py
```

Training is CPU-friendly and the serialized model is about 1.3 MB. The exact run reported here used Python 3.13.0 and scikit-learn 1.8.0 on Apple silicon.

### Public application and deployment

The public application is hosted at **https://mahamatbt.github.io/summative/**. It runs inference in the visitor's browser using the exported vocabulary, inverse-document-frequency values, SVM coefficients, and intercepts from `outputs/models/hausalens.joblib`. This is a numerical port of the trained classifier, rather than a separate rule-based approximation.

The exporter produces a roughly 3.8 MB uncompressed JSON artifact during deployment. It is downloaded once when the app opens. User text stays in the browser. The original Streamlit app remains available for Python-based local use.

The `Deploy HausaLens` GitHub Actions workflow exports the committed model, checks Python/JavaScript parity, and deploys `web/` to GitHub Pages. A push to `main` redeploys the app automatically. The model-parity check covers all 5,303 test texts plus nine additional edge cases, with zero prediction mismatches and maximum SVM-margin differences below `1e-10`. It checks the implementation without retraining or tuning against test labels.

To reproduce the browser build locally, install Node.js 22 or newer, then run:

```bash
python scripts/export_web_model.py
python scripts/verify_web_model.py
python -m http.server 8000 --directory web
```

Open `http://localhost:8000`. Optional Chrome/Playwright interface checks can be run with `python scripts/verify_deployment.py --local`. The screenshot checker currently uses the standard macOS Chrome installation path.

### Report and final video link

Generate the report with `python scripts/build_report.py`. It uses Arial Unicode on macOS or DejaVu Sans on Linux. After recording and uploading your own video, rebuild it with:

```bash
python scripts/build_report.py --video-url "YOUR_ACCESSIBLE_VIDEO_URL"
```

Replace the pending video entry in this README with that same verified link, then commit and push the updated README and PDF. The report currently labels the personal video as pending.

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

The hybrid differences are small and were not tested for statistical significance. The experiment called "without emoji" uses a high-Unicode-code-point removal heuristic; it is an approximate ablation, not a complete Unicode emoji detector. The model uses TF-IDF features and a linear SVM, not pretrained embeddings or a Transformer.

## Responsible use and limitations

- The model was trained on public social-media text, not reviews, call-center messages, or formal Hausa; cross-domain performance was not measured.
- Neutral statements, negation, rhetorical questions, sarcasm, mixed sentiment, code-switching, dialectal variation, and evolving slang remain difficult.
- The interface reports a softmax transformation of SVM margins as **relative confidence**, not a calibrated probability.
- Predictions must not be used to profile people or make high-impact decisions.
- No native-speaker audit of the model’s final errors was available for this capstone; qualitative interpretations are therefore conservative.
- The publisher's train/validation text overlap can make the original validation scores optimistic. The held-out test has no normalized text overlap with either development partition.

See [`DATA_CARD.md`](DATA_CARD.md) and [`MODEL_CARD.md`](MODEL_CARD.md) for details.

## Attribution

NaijaSenti is credited to Muhammad et al. (2022):

> Shamsuddeen Hassan Muhammad et al. “NaijaSenti: A Nigerian Twitter Sentiment Corpus for Multilingual Sentiment Analysis.” LREC 2022, pp. 590–602.

The dataset is CC BY 4.0. Project source code is MIT licensed. Full academic references appear in the PDF report.

AI assistance was used for coding, documentation, deployment, and verification. Existing resources are distinguished from the project implementation in the report. The student remains responsible for understanding and defending the submitted work and for recording the final demonstration.

