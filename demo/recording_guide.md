# Your personal 10-15 minute HausaLens demonstration

Aim for about 13 minutes. Read the narration in your own voice and pause while demonstrating. The times include screen changes and interaction. Rehearse to check the final duration. No video has been generated for you.

Open these before recording: the public app at https://mahamatbt.github.io/summative/, your repository at https://github.com/Mahamatbt/summative, DATA_CARD.md, src/hausalens/modeling.py, scripts/train.py, outputs/figures/experiment_comparison.png, outputs/figures/per_class_f1.png, outputs/figures/confusion_matrix.png, outputs/validation_sensitivity.csv, and MODEL_CARD.md.

## 0:00-0:45: introduce the project

**Show:** The GitHub README and project name, then the public app with its URL visible.

**Say:**

> Hello, my name is [say your name]. My individual NLP capstone is HausaLens, a sentiment classifier for Hausa social-media text. It predicts positive, negative, or neutral sentiment. The intended users are researchers, students, and teams exploring aggregate opinions in Hausa feedback. I focused on a measurable task and built the data preparation, training, experiments, evaluation, error analysis, and web interface. I will explain the choices and results, and show examples where the system succeeds and fails.

## 0:45-2:00: explain the data

**Show:** DATA_CARD.md, then a few rows of data/raw/train.tsv. Point to the text and label columns.

**Say:**

> I used the Hausa subset of NaijaSenti, a real, human-annotated social-media dataset. Synthetic AI text was not used for training. The release contains 22,152 examples: 14,172 training, 2,677 validation, and 5,303 test examples. The three labels are close to balanced. Training teaches the model; validation compares configurations; the separate test split evaluates the selected system.
>
> The final quality audit found 215 normalized messages shared by training and validation. Therefore, the original validation scores can be optimistic. There were no normalized text matches between training and test, or validation and test. I document this and include a separate validation comparison that excludes those 215 messages. The data come from one platform and collection period, so they do not represent every Hausa variety or domain.

## 2:00-3:00: preparation and reproducibility

**Show:** normalize_text in src/hausalens/modeling.py, then read_split in scripts/train.py.

**Say:**

> Preprocessing replaces links and usernames with stable tokens, lowercases text, and collapses extra spaces. Hausa characters, punctuation, hashtags, and emojis are retained because they may carry sentiment. Missing rows and within-split duplicates would be removed; none were found in the release used here.
>
> Each experiment learns its feature vocabulary from its training data. The evaluation messages are transformed using those learned features. I used scripts to make the sequence repeatable: download and audit data, train, evaluate, analyze errors, and serve the saved model. A notebook was not required, and scripts make the training and deployment workflow straightforward to reproduce.

## 3:00-4:30: explain the actual model

**Show:** build_linear_model in modeling.py. Point to char_wb, ngram_range, min_df, max_features, C, and class_weight.

**Say:**

> The model combines character TF-IDF with a linear support-vector machine. It extracts patterns of three to five characters within padded word boundaries. TF-IDF converts those patterns into numbers, weighting their occurrence in the message against how common they are in the training documents. The vector is normalized before classification.
>
> The SVM learns coefficients and an intercept for each class. It computes three scores for a new message and selects the highest. Character patterns can remain similar across spelling variants, which makes them a plausible representation for informal text. This is a possible explanation for their performance, rather than a proven causal account.
>
> The configuration caps character features at 65,000, requires occurrence in at least three training documents, and uses C equal to 1.5 with class-balanced weights. The fitted final model has 43,806 features. This version uses TF-IDF rather than pretrained embeddings or a Transformer. It is compact, fast, and practical to deploy.

## 4:30-5:45: explain experiments and selection

**Show:** experiment_comparison.png, then validation_sensitivity.csv.

**Say:**

> I compared six configurations. The majority baseline always predicts the most frequent label and gives a minimum reference. Its validation macro F1 is 16.72 percent. Word TF-IDF with Naive Bayes reaches 71.63 percent. Word unigrams and bigrams with an SVM reach 74.32 percent. Character features with an SVM reach 76.98 percent, the highest original validation score.
>
> Combining word and character features gives about 76.63 percent. The approximate emoji-removal variant gives about 76.64 percent. These small differences are not evidence of statistical significance, and adding more features did not improve the best result.
>
> In the overlap-free validation check, the character model still ranks first at 75.44 percent on 2,462 examples. That supports the ranking while exposing the optimism in the original scores. The final artifact was fitted on training plus validation after the original selection, and the sensitivity check did not change it.

## 5:45-7:00: explain evaluation

**Show:** outputs/test_metrics.json and per_class_f1.png.

**Say:**

> The final test accuracy is 76.58 percent, and macro F1 is 76.49 percent. Accuracy is the fraction of messages receiving the reference dataset label.
>
> Precision asks how often a predicted class is correct. Recall asks how many of that class's actual examples were found. F1 combines precision and recall using a harmonic mean. Macro F1 computes an F1 for each class and averages the three equally. It is a score that balances class performance, rather than another name for accuracy.
>
> Positive F1 is 84.46 percent, negative is 74.56 percent, and neutral is 70.44 percent. These class results reveal an important weakness that a single aggregate score would hide. Published Transformer results provide related-work context, but different dataset versions and metric averaging prevent a direct claim that this project replicated those benchmarks.

## 7:00-8:00: analyze errors

**Show:** confusion_matrix.png. Point to the true-neutral row and predicted-negative column.

**Say:**

> Rows show reference labels and columns show predicted labels. Correct predictions are on the diagonal. The model makes 1,242 test errors. Its largest confusion is 436 neutral messages classified as negative.
>
> A possible explanation is that neutral questions or factual messages contain words associated with negative situations. The classifier may respond to those patterns without enough context to infer the author's intent. Negation-marker messages also have a higher observed error rate. These are descriptive findings and hypotheses, rather than established causes. A native-speaker audit would help distinguish ambiguous annotation from model errors.

## 8:00-11:00: demonstrate the public application

**Show:** https://mahamatbt.github.io/summative/ in the browser. Keep the URL visible. Choose an example, click Analyze sentiment, and pause on each output.

**Say:**

> This is the publicly deployed application. It downloads the actual trained parameters and performs inference in the browser. The input text is not sent to an AI prediction service. The Python version remains available through Streamlit.

1. Choose **Positive** and click **Analyze sentiment**. Text: `Allah ya saka da alheri, na gode sosai!`

   > This expresses thanks and good wishes. The model predicts positive. The interface displays relative confidence and character patterns that contributed to the score.

2. Choose **Neutral** and click **Analyze sentiment**. Text: `Za a fara taron da karfe goma na safe.`

   > This gives a meeting time. It is predicted as neutral because it presents information without obvious praise or criticism.

3. Choose **Negative** and click **Analyze sentiment**. Text: `Wannan abu ya bata min rai sosai.`

   > This expresses being upset, and the model predicts negative. These examples illustrate the workflow; they do not replace the full test-set evaluation.

4. Choose **Known test-set error** and click **Analyze sentiment**. Text: `nawa kuke saida blander din nan ma zan dinga markade acikinta`

   > This is a real test example. The dataset label is neutral, but the model predicts negative. The note identifies it as a reference-label mismatch. Informal wording and context may matter, but I would need a native-speaker review to explain this specific error confidently.

**Then show the confidence warning and model card. Say:**

> Relative confidence is derived from SVM margins and is not a calibrated probability. A high score does not guarantee a correct interpretation. Influential character patterns reveal parts of the linear calculation; they are not a human-like explanation of intent. The model card keeps measured performance and limitations visible.

## 11:00-12:00: explain deployment and relevant code

**Show:** export_web_model.py, web/model.mjs, the GitHub deploy workflow, and outputs/web_parity.json.

**Say:**

> The public app uses a numerical port of the same trained classifier. The exporter saves its vocabulary, inverse-document-frequency values, coefficients, and intercepts. The browser reproduces feature extraction and the linear calculation using those learned values.
>
> The parity check compared browser-runtime and Python predictions on all 5,303 test examples and nine extra edge cases. There were zero label mismatches, with only tiny floating-point score differences. This is an implementation check, not model tuning on the test data.
>
> GitHub Actions rebuilds and deploys the app on pushes to main. The repository includes preparation, training, evaluation, error analysis, inference, tests, and reproduction instructions. Existing datasets and libraries are cited, and AI assistance is disclosed.

## 12:00-13:00: limitations and conclusion

**Show:** MODEL_CARD.md, then the repository's report and live-system links.

**Say:**

> The model has limitations around neutral sentiment, sarcasm, negation, mixed opinions, spelling conventions, and missing context. It has not been evaluated across other domains or all Hausa varieties. The training-validation overlap is disclosed, and score calibration and a native-speaker error audit remain future work.
>
> A useful next experiment would compare an African-language Transformer under a carefully audited split protocol. More natural evaluation data from another domain would also help.
>
> My main finding is that the character SVM performed best among the six configurations tested, with 76.49 percent test macro F1. More features did not automatically help. The project taught me to connect model choices to validation evidence, analyze class-specific failures, and deploy the trained system while making its limitations visible. Thank you.

## After recording

Upload your video with assessor-accessible permissions. Add its link to README.md, then run `python scripts/build_report.py --video-url "YOUR_ACCESSIBLE_VIDEO_URL"` and push the updated PDF. Verify that the final video is 10-15 minutes and that all shared links work while signed out.
