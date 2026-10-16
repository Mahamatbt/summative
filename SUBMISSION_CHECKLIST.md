# Final submission checklist

## Available now

- Public repository: https://github.com/Mahamatbt/summative
- Deployed, interactive classifier: https://mahamatbt.github.io/summative/
- PDF report: [output/pdf/hausalens_capstone_report.pdf](output/pdf/hausalens_capstone_report.pdf)
- Personal recording guide: [demo/recording_guide.md](demo/recording_guide.md)

## Evidence for each rubric criterion

1. **Problem, language, and dataset (8 points).** README introduction, report Introduction and Dataset sections, DATA_CARD.md, download_data.py, and data_audit.json document Hausa sentiment classification, intended users, source, counts, preparation, license, and limitations. This is text classification, so the unsupported-translation-direction restriction is not applicable.
2. **Model development and methodology (10 points).** modeling.py and train.py implement and fit TF-IDF/Naive Bayes/SVM models. Report Methodology explains inputs, outputs, training, feature extraction, C, class weighting, feature limits, and inference. There are no pretrained embeddings or Transformers in this version; explain the actual approach and relate it to the techniques covered in your course. The student's video must demonstrate this understanding.
3. **Baseline and experiments (8 points).** experiment_results.csv contains six configurations. validation_sensitivity.csv repeats the comparison on overlap-free validation examples. Explain the purpose of each comparison, why the character model won, and why small hybrid differences are inconclusive.
4. **Evaluation and error analysis (7 points).** test_metrics.json, class scores, confusion matrix, error_examples.csv, error slices, and the report provide quantitative and qualitative analysis. The live app includes a real neutral-to-negative error. Explain the metrics and demonstrate both correct predictions and that failure in the video.
5. **Research report (10 points).** The PDF contains abstract, introduction, related work, dataset, methodology, experiments/results, error discussion, deployment, limitations/future work, conclusion, and references, with in-text numbered citations. It documents the training/validation overlap, benchmark-comparison limits, and AI assistance.
6. **Web deployment and demonstration (7 points).** The GitHub Pages app is publicly accessible. deployment_verification.json records successful live positive, neutral, negative, known-error, blank-input, and mobile checks. web_parity.json checks numerical equivalence to Python on 5,303 test examples and nine edge cases. The complete user workflow must still appear in your video.
7. **Code quality, reproduction, and GitHub (5 points).** The README explains setup, data, training, evaluation, browser export, deployment, report generation, and attribution. GitHub Actions runs tests and publishes the browser app. The README and report have repository/live links; their video entry remains explicitly pending.
8. **Technical understanding and individual defense (5 points).** Your own recording and answers must establish ownership. Code and documentation cannot satisfy this on your behalf. Use the recording guide to rehearse explanations rather than memorizing labels or scores.

This is an evidence checklist, not a predicted grade. Video-dependent rubric requirements remain incomplete until you record the demonstration.

## Remaining student actions

1. Record your own **10-15 minute** demonstration. Show the public URL, four examples, relevant code, experiments, evaluation, and limitations.
2. Upload it to a location accessible to the assessor, and test its sharing permissions while signed out.
3. Replace the pending video entry in README.md with its verified link.
4. Add the same URL to the PDF by running:

   ```bash
   python scripts/build_report.py --video-url "YOUR_ACCESSIBLE_VIDEO_URL"
   ```

5. Commit and push the updated README and PDF, and submit the repository, report, live-system URL, and personal video as requested by your instructor.

No new video was recorded or generated as part of this completion work.
