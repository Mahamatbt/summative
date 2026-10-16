# Model card: HausaLens v1.0

## Model description

- **Task:** Hausa tweet sentiment classification
- **Labels:** negative, neutral, positive
- **Representation:** character 3–5 gram TF-IDF within word boundaries
- **Classifier:** class-balanced linear support-vector machine
- **Training data:** 16,849 NaijaSenti Hausa train + validation examples after model selection
- **Artifact:** `outputs/models/hausalens.joblib`
- **External inference services:** none
- **Public application:** https://mahamatbt.github.io/summative/
- **Deployment:** browser inference using exported learned vocabulary, IDF values, class coefficients, and intercepts; Python Streamlit remains available locally.

## Selection and evaluation

Six configurations were trained on the official train split. The highest validation macro-F1 determined the winner. The selected configuration was then refit on train + validation and evaluated once on the 5,303-item held-out test set.

| Metric | Test score |
|---|---:|
| Accuracy | 0.7658 |
| Macro precision | 0.7672 |
| Macro recall | 0.7665 |
| Macro-F1 | 0.7649 |
| Weighted-F1 | 0.7645 |

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Negative | 0.7081 | 0.7874 | 0.7456 | 1,759 |
| Neutral | 0.7587 | 0.6574 | 0.7044 | 1,789 |
| Positive | 0.8347 | 0.8547 | 0.8446 | 1,755 |

## Intended use

The artifact is intended for education, reproducible NLP experimentation, and low-stakes exploration of in-domain Hausa social-media text. It may support research prototyping when its limitations are kept visible.

## Out-of-scope use

Do not use the model for surveillance, moderation without human review, profiling, employment, credit, healthcare, policing, political targeting, or any decision that affects a person’s rights or opportunities. Do not interpret the relative confidence score as a calibrated probability.

## Known limitations

The released training and validation partitions share 215 normalized texts. Original model selection preserves those partitions and may yield optimistic validation scores. A separate validation-only sensitivity comparison excludes those texts; the final test set has no normalized text matches with either partition. Browser/Python implementation parity is checked on all 5,303 test examples plus nine edge cases without changing model selection or training.

Neutral text is the largest error source. Performance can degrade with other domains, new slang, long conversational context, sarcasm, code-switching patterns unlike the training data, or spelling conventions absent from the corpus. The test set was not independently re-annotated, and no native-speaker error audit was conducted for this capstone.

