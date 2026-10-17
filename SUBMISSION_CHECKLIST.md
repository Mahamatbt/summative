# Final submission checklist

## Available now

- Public repository: https://github.com/Mahamatbt/summative
- Deployed, interactive classifier: https://mahamatbt.github.io/summative/
- PDF report: [output/pdf/hausalens_capstone_report.pdf](output/pdf/hausalens_capstone_report.pdf)
- Demo video: [Student's HausaLens demonstration on YouTube](https://youtu.be/g8qN6C-GF6k)
- Personal recording guide: [demo/recording_guide.md](demo/recording_guide.md)

## Evidence for each rubric criterion

1. **Problem, language, and dataset (8 points).** README introduction, report Introduction and Dataset sections, DATA_CARD.md, download_data.py, and data_audit.json document Hausa sentiment classification, intended users, source, counts, preparation, license, and limitations. This is text classification, so the unsupported-translation-direction restriction is not applicable.
2. **Model development and methodology (10 points).** modeling.py and train.py implement and fit TF-IDF/Naive Bayes/SVM models. Report Methodology explains inputs, outputs, training, feature extraction, C, class weighting, feature limits, and inference. There are no pretrained embeddings or Transformers in this version; explain the actual approach and relate it to the techniques covered in your course. The student's video must demonstrate this understanding.
3. **Baseline and experiments (8 points).** experiment_results.csv contains six configurations. validation_sensitivity.csv repeats the comparison on overlap-free validation examples. Explain the purpose of each comparison, why the character model won, and why small hybrid differences are inconclusive.
4. **Evaluation and error analysis (7 points).** test_metrics.json, class scores, confusion matrix, error_examples.csv, error slices, and the report provide quantitative and qualitative analysis. The live app includes a real neutral-to-negative error. Explain the metrics and demonstrate both correct predictions and that failure in the video.
5. **Research report (10 points).** The PDF contains abstract, introduction, related work, dataset, methodology, experiments/results, error discussion, deployment, limitations/future work, conclusion, and references, with in-text numbered citations. It documents the training/validation overlap, benchmark-comparison limits, and AI assistance.
6. **Web deployment and demonstration (7 points).** The GitHub Pages app is publicly accessible. deployment_verification.json records successful live positive, neutral, negative, known-error, blank-input, and mobile checks. web_parity.json checks numerical equivalence to Python on 5,303 test examples and nine edge cases. The student's recorded demonstration is linked above for assessment of the complete workflow.
7. **Code quality, reproduction, and GitHub (5 points).** The README explains setup, data, training, evaluation, browser export, deployment, report generation, and attribution. GitHub Actions runs tests and publishes the browser app. The README and report include repository, live-system, and personal demonstration links.
8. **Technical understanding and individual defense (5 points).** Your own recording and answers must establish ownership. Code and documentation cannot satisfy this on your behalf. Use the recording guide to rehearse explanations rather than memorizing labels or scores.

This is an evidence checklist, not a predicted grade. The student's recorded demonstration is now linked. Assessment of its content and the student's understanding remains with the instructor.

## Final submission

1. Submit the PDF report, GitHub repository, live-system link, and [YouTube demonstration](https://youtu.be/g8qN6C-GF6k) as requested by your instructor.
2. Keep the video accessible to anyone with the link and ensure its duration meets the instructor's **10-15 minute** requirement.
3. The report already includes the video URL. To reproduce it, run:

   ```bash
   python scripts/build_report.py
   ```

The video was recorded and uploaded by the student. This update only links that supplied recording; it does not replace it with a generated video.
