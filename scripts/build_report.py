#!/usr/bin/env python3
"""Build the polished HausaLens capstone report from measured outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "hausalens_capstone_report.pdf"
GREEN = colors.HexColor("#173D25")
MID_GREEN = colors.HexColor("#2E6A3E")
PALE_GREEN = colors.HexColor("#E7F0E8")
GOLD = colors.HexColor("#F4B942")
CREAM = colors.HexColor("#F7F2E8")
INK = colors.HexColor("#17251B")
MUTED = colors.HexColor("#5D6A60")
RED = colors.HexColor("#A64B35")

GITHUB = "https://github.com/Mahamatbt/summative"
LIVE = "https://mahamatbt.github.io/summative/"


def register_fonts() -> None:
    mac = Path("/System/Library/Fonts/Supplemental")
    if (mac / "Arial Unicode.ttf").exists():
        paths = [mac / "Arial Unicode.ttf", mac / "Arial Bold.ttf", mac / "Arial Italic.ttf"]
    else:
        from matplotlib import get_data_path
        fonts = Path(get_data_path()) / "fonts/ttf"
        paths = [fonts / "DejaVuSans.ttf", fonts / "DejaVuSans-Bold.ttf", fonts / "DejaVuSans-Oblique.ttf"]
    for name, path in zip(["ArialU", "ArialB", "ArialI"], paths):
        pdfmetrics.registerFont(TTFont(name, str(path)))


def styles():
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="ArialU", fontSize=9.2, leading=13.6, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=7),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontName="ArialU", fontSize=7.7, leading=10.8, textColor=MUTED, spaceAfter=5),
        "caption": ParagraphStyle("Caption", parent=base["BodyText"], fontName="ArialI", fontSize=7.6, leading=10.2, textColor=MUTED, alignment=TA_CENTER, spaceBefore=4, spaceAfter=9),
        "h1": ParagraphStyle("H1", parent=base["Heading1"], fontName="ArialB", fontSize=20, leading=23, textColor=GREEN, spaceBefore=2, spaceAfter=10),
        "h2": ParagraphStyle("H2", parent=base["Heading2"], fontName="ArialB", fontSize=12.5, leading=15, textColor=MID_GREEN, spaceBefore=12, spaceAfter=6),
        "h3": ParagraphStyle("H3", parent=base["Heading3"], fontName="ArialB", fontSize=9.5, leading=12, textColor=GREEN, spaceBefore=8, spaceAfter=4),
        "bullet": ParagraphStyle("Bullet", parent=base["BodyText"], fontName="ArialU", fontSize=8.9, leading=12.8, textColor=INK, leftIndent=13, firstLineIndent=-8, bulletIndent=3, spaceAfter=4),
        "quote": ParagraphStyle("Quote", parent=base["BodyText"], fontName="ArialI", fontSize=8.5, leading=12.2, textColor=GREEN, leftIndent=16, rightIndent=16, borderColor=GOLD, borderWidth=2, borderPadding=7, spaceAfter=8),
        "link": ParagraphStyle("Link", parent=base["BodyText"], fontName="ArialU", fontSize=8.1, leading=12, textColor=GREEN, spaceAfter=3),
        "kpi": ParagraphStyle("KPI", parent=base["BodyText"], fontName="ArialB", fontSize=19, leading=20, textColor=GREEN, alignment=TA_CENTER),
        "kpilabel": ParagraphStyle("KPILabel", parent=base["BodyText"], fontName="ArialU", fontSize=7.2, leading=9, textColor=MUTED, alignment=TA_CENTER),
        "cover_title": ParagraphStyle("CoverTitle", parent=base["Title"], fontName="ArialB", fontSize=34, leading=38, textColor=colors.white, alignment=TA_LEFT),
        "cover_sub": ParagraphStyle("CoverSub", parent=base["BodyText"], fontName="ArialU", fontSize=14, leading=20, textColor=colors.HexColor("#EAF3EB"), spaceAfter=12),
        "cover_meta": ParagraphStyle("CoverMeta", parent=base["BodyText"], fontName="ArialU", fontSize=9, leading=13, textColor=colors.white),
    }


def first_page(canvas, doc) -> None:
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(GREEN)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.circle(width - 2.1 * cm, height - 2.0 * cm, 0.55 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#29583A"))
    canvas.circle(width - 1.2 * cm, 1.2 * cm, 3.2 * cm, fill=1, stroke=0)
    canvas.restoreState()


def later_page(canvas, doc) -> None:
    width, height = A4
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D5DDD4"))
    canvas.line(1.8 * cm, height - 1.35 * cm, width - 1.8 * cm, height - 1.35 * cm)
    canvas.setFont("ArialB", 8)
    canvas.setFillColor(GREEN)
    canvas.drawString(1.8 * cm, height - 1.05 * cm, "HAUSALENS · AFRICAN NLP CAPSTONE")
    canvas.setFont("ArialU", 8)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(width - 1.8 * cm, 1.0 * cm, f"{doc.page - 1}")
    canvas.restoreState()


def p(text, style):
    return Paragraph(str(text).replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-"), style)


def bullet(text, s):
    return Paragraph(f"• {text}", s["bullet"])


def section(title, s, number=None):
    shown = f"{number}. {title}" if number is not None else title
    return [PageBreak(), Paragraph(shown, s["h1"]), HRFlowable(width="100%", thickness=1.8, color=GOLD, spaceAfter=10)]


def make_table(data, widths, *, header=True, alignments=None, font_size=7.8):
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), "ArialU"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 3),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD6CC")),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, CREAM]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "ArialB"),
        ]
    if alignments:
        for col, value in enumerate(alignments):
            commands.append(("ALIGN", (col, 1 if header else 0), (col, -1), value))
    table.setStyle(TableStyle(commands))
    return table


def kpis(items, s):
    cells = []
    for value, label in items:
        cells.append([[p(value, s["kpi"])], [p(label, s["kpilabel"])]] )
    inner = [Table(cell, colWidths=[4.1 * cm]) for cell in cells]
    table = Table([inner], colWidths=[4.25 * cm] * len(inner), hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_GREEN),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#C4D5C7")),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def build(video_url: str | None = None) -> None:
    register_fonts()
    s = styles()
    metrics = json.loads((ROOT / "outputs" / "test_metrics.json").read_text())
    experiments = pd.read_csv(ROOT / "outputs" / "experiment_results.csv")
    slices = pd.read_csv(ROOT / "outputs" / "error_slices.csv")
    by_length = pd.read_csv(ROOT / "outputs" / "error_by_length.csv")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUT), pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
        topMargin=1.75 * cm, bottomMargin=1.55 * cm,
        title="HausaLens: Lightweight Sentiment Classification for Hausa Social-Media Text",
        author="Individual African NLP Capstone",
        subject="Dataset, experiments, error analysis, and deployment of a Hausa sentiment classifier",
    )
    width, height = A4
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[Frame(2.0 * cm, 2.0 * cm, width - 4.0 * cm, height - 4.0 * cm, id="cover-frame")], onPage=first_page, autoNextPageTemplate="body"),
        PageTemplate(id="body", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body-frame")], onPage=later_page),
    ])

    story = []
    story += [Spacer(1, 3.3 * cm), p("INDIVIDUAL NLP CAPSTONE", s["cover_meta"]), Spacer(1, 0.28 * cm)]
    story += [p("HausaLens", s["cover_title"]), p("Lightweight sentiment classification for Hausa social-media text", s["cover_sub"])]
    story += [Spacer(1, 0.35 * cm), HRFlowable(width="36%", thickness=3, color=GOLD, hAlign="LEFT"), Spacer(1, 0.4 * cm)]
    story += [p("A reproducible comparison of six supervised classifiers using the human-annotated NaijaSenti corpus, with held-out evaluation, error analysis, and an interactive deployment.", s["cover_sub"])]
    story += [Spacer(1, 2.0 * cm), p("Project type  ·  Text Classification for an African Language<br/>Language  ·  Hausa<br/>Task  ·  Positive / Neutral / Negative sentiment<br/>Report date  ·  16 October 2026", s["cover_meta"])]
    story += [PageBreak()]

    story += [p("Project links", s["h1"]), HRFlowable(width="100%", thickness=1.8, color=GOLD, spaceAfter=10)]
    links = [("GitHub repository", GITHUB), ("Live system", LIVE)]
    if video_url:
        links.append(("Demo video", video_url))
    for label, url in links:
        story.append(p(f"<b>{label}:</b> <link href='{url}' color='#2E6A3E'>{url}</link>", s["link"]))
    if not video_url:
        story.append(p("<b>Demo video:</b> Pending the student's own 10-15 minute recording. This report does not claim that the video has been submitted. Add its accessible URL before final submission.", s["link"]))
    story += [Spacer(1, 0.3 * cm), p("The public system is hosted on GitHub Pages. The repository also includes the trained Python model and local Streamlit instructions. The student's personal video and individual defense remain to be completed.", s["small"])]
    story += [p("Abstract", s["h2"])]
    story += [p(
        "This project investigates three-class sentiment classification for informal Hausa social-media text. The study uses 22,152 naturally occurring, human-annotated tweets from the open NaijaSenti release: 14,172 training, 2,677 validation, and 5,303 test items. Six configurations compare a majority baseline and word TF-IDF with Multinomial Naive Bayes against word-, character-, and hybrid TF-IDF representations with linear support-vector machines. Character 3-5 grams achieved the best original validation macro-F1 (0.7698), followed by 0.7658 test accuracy and 0.7649 test macro-F1 after refitting on train plus validation. A quality audit found 215 train/validation text overlaps; an overlap-free validation sensitivity check still ranks the character model first at 0.7544. No normalized training/test text overlap was found. Positive sentiment was easiest (F1 0.8446), while neutral was hardest (F1 0.7044). The model is publicly deployed through a browser interface using exported learned parameters, with numerical parity verified against Python. A local Streamlit alternative is retained. The findings support a compact Hausa sentiment baseline while exposing clear limitations in contextual interpretation.", s["body"])]
    story += [Spacer(1, 0.25 * cm), kpis([
        ("22,152", "HUMAN-ANNOTATED ITEMS"),
        ("0.7649", "TEST MACRO-F1"),
        ("1.3 MB", "MODEL ARTIFACT"),
        ("0", "EXTERNAL API CALLS"),
    ], s)]
    story += [Spacer(1, 0.45 * cm), p("Contents", s["h2"])]
    contents = [
        "1. Introduction", "2. Related Work", "3. Dataset and Data Preparation", "4. Methodology",
        "5. Experiments and Results", "6. Error Analysis and Discussion", "7. Deployment",
        "8. Limitations and Future Work", "9. Conclusion", "10. References", "Appendix A. Reproducibility and Individual Contribution",
    ]
    story += [bullet(item, s) for item in contents]

    story += section("Introduction", s, 1)
    story += [p(
        "Sentiment classification assigns an opinion-bearing text to categories such as positive, neutral, or negative. It is useful for summarizing public feedback, monitoring service quality, and studying online discussion, but most datasets and production tools prioritize high-resource languages. NaijaSenti was introduced to address this imbalance for Hausa, Igbo, Nigerian Pidgin, and Yorùbá, using manually annotated Twitter data and documenting extensive multilingual and code-mixed usage [1]. AfriSenti later broadened shared-task evaluation to 14 African languages [2].", s["body"])]
    story += [p(
        "Hausa is a consequential case because users produce substantial informal text online, yet spelling variation, abbreviated writing, borrowed English expressions, religious phrases, emojis, and missing conversational context complicate sentiment analysis. The problem is not merely whether a classifier can return a label; it is whether the complete workflow is reproducible, whether model selection is isolated from test evaluation, and whether failures are examined rather than hidden behind a single score.", s["body"])]
    story += [p(
        "The intended users are researchers, students, and teams exploring aggregate sentiment in Hausa feedback. The application supports low-stakes research and learning. Generalization to customer service, news, or other domains is a motivation for future evaluation, rather than an established result. This is the text-classification option; the assignment's restriction on selecting an unsupported translation direction applies to its separate machine-translation option.", s["body"])]
    story += [p("Objective and research questions", s["h2"])]
    for item in [
        "RQ1 — How much does a learned classifier improve over a majority-class baseline on the fixed NaijaSenti Hausa validation split?",
        "RQ2 — Do character n-grams, which can represent spelling fragments and morphological variation, outperform word n-grams for this dataset?",
        "RQ3 — Does combining word and character features or removing emoji improve macro-F1?",
        "RQ4 — Which labels and surface-form conditions account for the largest share of held-out errors?",
    ]:
        story.append(bullet(item, s))
    story += [p(
        "The project’s own contribution is the end-to-end experimental pipeline, conservative preprocessing, six controlled comparisons, held-out evaluation, error-slice analysis, compact serialized model, local explanation method, web application, and reproducibility documentation. The underlying tweets, annotations, and published transformer benchmarks are existing resources and are cited separately.", s["quote"])]

    story += section("Related Work", s, 2)
    story += [p(
        "Muhammad et al. introduced NaijaSenti as a large, open sentiment resource for four Nigerian languages. Their collection procedure combined language-specific stop words, emojis, and translated sentiment lexicons to retrieve candidates, followed by human annotation. They reported substantial code-mixing and evaluated multilingual pretrained language models. On Hausa, AfriBERTa-large achieved 81.0 weighted F1 in their reported benchmark, outperforming mBERT and XLM-R-base in that table [1]. This establishes a useful upper reference, but it is not a directly replicated score here because the released files used in this project contain different split counts from the early LREC table.", s["body"])]
    story += [p(
        "The AfriSenti-SemEval shared task formalized monolingual, multilingual, and zero-shot sentiment evaluation across 14 African languages and attracted dozens of submissions. The organizers reported weighted F1 for the shared-task systems [2]. This project instead selects on macro-F1 and reports weighted F1 separately; those measures must not be conflated. Ogueji et al. investigated AfriBERTa, a compact multilingual model for African-language tasks [3]. These studies motivate a future Transformer comparison but are existing research, not models fine-tuned in this project.", s["body"])]
    story += [p(
        "Classical representations remain relevant when reproducibility, speed, and compact deployment matter. Keinan and Hacohen-Kerner tested word and character TF-IDF n-grams alongside classical and deep models in AfriSenti, demonstrating that n-gram baselines belong in a serious experimental comparison rather than being dismissed [4]. Linear support-vector machines construct maximum-margin decision boundaries in high-dimensional feature spaces [5], making them well matched to sparse TF-IDF text vectors. HausaLens therefore treats a compact linear model as a deliberate, testable design choice, not as a claim of state-of-the-art performance.", s["body"])]

    story += section("Dataset and Data Preparation", s, 3)
    story += [p("3.1 Source, license, and fit", s["h2"])]
    story += [p(
        "The data are the Hausa split files from the official HausaNLP/NaijaSenti GitHub repository [6]. They are naturally occurring tweets annotated by people; no large-language-model-generated examples were used. The repository releases the resource under CC BY 4.0. Its three labels map exactly to the target application: negative, neutral, and positive sentiment in informal Hausa social-media text.", s["body"])]
    split_data = [
        ["Split", "Rows", "Negative", "Neutral", "Positive", "Median tokens"],
        ["Train", "14,172", "4,573", "4,912", "4,687", "11"],
        ["Validation", "2,677", "894", "896", "887", "11"],
        ["Test", "5,303", "1,759", "1,789", "1,755", "9"],
        ["Total", "22,152", "7,226", "7,597", "7,329", "10"],
    ]
    story += [make_table(split_data, [2.5*cm, 2.1*cm, 2.1*cm, 2.1*cm, 2.1*cm, 2.5*cm], alignments=["LEFT","RIGHT","RIGHT","RIGHT","RIGHT","RIGHT"]), p("Table 1. Official repository release used in this study. Counts were recomputed locally from the downloaded TSV files.", s["caption"])]
    story += [p(
        "The early LREC paper lists a larger Hausa benchmark split (18,989 / 2,714 / 5,427) [1], whereas the current official files used here contain 14,172 / 2,677 / 5,303 and match later AfriSenti system descriptions. This report records the exact files and counts rather than silently blending versions. The download script checks row counts, and model outputs record the runtime environment.", s["body"])]
    story += [p("3.2 Cleaning and leakage control", s["h2"])]
    for item in [
        "Preserve the publisher’s train, validation, and test boundaries; never use test labels for selection.",
        "Drop missing text or labels and exact duplicate rows within a split. No rows were removed in the downloaded release.",
        "Replace URLs and account handles with stable URL and USER tokens; lowercase and collapse whitespace.",
        "Retain Hausa characters, punctuation, hashtags, and emoji because they may carry sentiment.",
        "Fit TF-IDF vocabularies only on the current training partition inside each experiment pipeline.",
    ]:
        story.append(bullet(item, s))
    story += [p(
        "The corpus is close to class balanced, so accuracy is reported but macro-F1 is the primary model-selection metric. Macro averaging gives each class equal weight and therefore exposes weak neutral-class performance that accuracy alone can conceal.", s["body"])]
    story += [p("3.3 Quality audit and split overlap", s["h2"])]
    story += [p(
        "The final reproducible audit found no missing text/label rows, no exact duplicate rows within a split, and no normalized duplicate texts within a split. However, training and validation share 215 normalized texts, about 8.0% of validation. Preserving publisher boundaries therefore did not make the original validation comparison fully independent. Training/test and validation/test have zero normalized text matches. This check covers exact normalized overlap, not semantic near-duplicates or shared conversational context. The original experiment is retained and the validation overlap is investigated separately in Section 5.", s["body"])]

    story += section("Methodology", s, 4)
    story += [p("4.1 Models", s["h2"])]
    method_rows = [
        ["Configuration", "Representation", "Purpose"],
        ["Majority baseline", "No text features", "Minimum non-learning reference"],
        ["Word + NB", "Word unigrams, TF-IDF", "Simple probabilistic lexical baseline"],
        ["Word + SVM", "Word 1–2 grams, TF-IDF", "Discriminative word-sequence model"],
        ["Character + SVM", "Character 3–5 grams, TF-IDF", "Subword spelling and morphology"],
        ["Hybrid − emoji", "Word + character TF-IDF", "Emoji ablation"],
        ["Hybrid", "Word + character TF-IDF", "Test whether feature union helps"],
    ]
    story += [make_table(method_rows, [4.2*cm, 5.2*cm, 6.2*cm], font_size=7.5), p("Table 2. Controlled configurations trained on the same training split.", s["caption"])]
    story += [p(
        "TF-IDF scales an n-gram by its frequency in the current document and by the inverse frequency of documents containing it. Word models use unigrams or 1–2 grams. Character models use the scikit-learn char_wb analyzer, which creates 3–5 character sequences within padded word boundaries [7]. Terms appearing fewer than two documents for word features or three documents for character features are omitted. Sublinear term frequency is enabled.", s["body"])]
    story += [p(
        "The linear SVM uses C = 1.5, class-balanced weights, and at most 5,000 iterations. A one-versus-rest decision function is learned for the three labels. The interface applies softmax to the three margins only to create an intuitive relative-confidence display; this value is explicitly not described as a calibrated probability. Local feature evidence is computed by multiplying the input’s non-zero TF-IDF values by the coefficient vector for the predicted class and ranking positive contributions.", s["body"])]
    story += [p(
        "For a feature count c, sublinear term frequency is 1 + log(c). Smoothed inverse document frequency is log((1 + N)/(1 + df)) + 1. The resulting vector is L2-normalized. Each class score is its learned intercept plus the dot product of the feature vector and class coefficients. Prediction selects the highest score. Input is a Hausa text string; output is one of three labels, margin-derived relative scores, and feature contributions. Character features are capped at 65,000; the fitted final vocabulary contains 43,806. Naive Bayes uses alpha = 0.7. These are fixed configurations, not an exhaustive hyperparameter search. No pretrained embedding or Transformer is used.", s["body"])]
    story += [p(
        "The so-called emoji-removal experiment removes characters with code points of 10,000 or above. This is an approximate high-code-point ablation, not a complete Unicode emoji detector; some emoji sequences may remain and non-emoji characters may also be removed. Its small performance difference cannot establish the causal value of emoji.", s["body"])]
    story += [p("4.2 Evaluation protocol", s["h2"])]
    story += [p(
        "Each candidate is fitted on 14,172 training items and evaluated on the fixed 2,677-item validation set. The configuration with the highest validation macro-F1 is selected. Only then is the winner refit on training plus validation (16,849 items) and evaluated once on the untouched 5,303-item test set. Reported metrics are accuracy, macro precision, macro recall, macro-F1, weighted-F1, per-class precision/recall/F1, and a confusion matrix. No hyperparameter search or model choice uses the test labels.", s["body"])]

    story += section("Experiments and Results", s, 5)
    result_rows = [["Model", "Accuracy", "Macro-P", "Macro-R", "Macro-F1", "Train s"]]
    for _, row in experiments.sort_values("macro_f1").iterrows():
        result_rows.append([
            row["model"], f"{row['accuracy']:.4f}", f"{row['macro_precision']:.4f}",
            f"{row['macro_recall']:.4f}", f"{row['macro_f1']:.4f}", f"{row['train_seconds']:.2f}",
        ])
    story += [make_table(result_rows, [5.6*cm, 2.0*cm, 2.0*cm, 2.0*cm, 2.1*cm, 1.7*cm], alignments=["LEFT","RIGHT","RIGHT","RIGHT","RIGHT","RIGHT"], font_size=7.1), p("Table 3. Validation results. Timing is descriptive for one local run, not a hardware-normalized benchmark.", s["caption"])]
    story += [Image(str(ROOT / "outputs" / "figures" / "experiment_comparison.png"), width=14.2*cm, height=8.68*cm), p("Figure 1. Validation macro-F1 for all six configurations.", s["caption"])]
    story += [p(
        "All learned models substantially exceed the majority macro-F1 of 0.1672. Word-unigram Naive Bayes reaches 0.7163; replacing it with word 1–2 grams and a linear SVM adds 2.69 points. Character n-grams add another 2.66 points and win at 0.7698. The hybrid model does not improve on character features alone, and its no-emoji ablation differs by only 0.0002 macro-F1 from the full hybrid. More features were therefore not automatically better. This answers RQ1–RQ3 and justifies selecting the character model.", s["body"])]
    sensitivity = pd.read_csv(ROOT / "outputs/validation_sensitivity.csv")
    story += [p("Validation sensitivity: remove training-text overlap", s["h2"])]
    sensitivity_rows = [["Configuration", "Validation items", "Macro-F1"]]
    for _, row in sensitivity.iterrows():
        sensitivity_rows.append([row["model"], str(int(row["validation_examples"])), f"{row['macro_f1']:.4f}"])
    story += [make_table(sensitivity_rows, [9.2*cm, 3.3*cm, 3.3*cm], font_size=7.4)]
    story += [p(
        "Supplementary comparison: exclude the 215 validation texts that normalize to training texts, leaving 2,462 items, then fit the same six configurations on the original training data. Character SVM still ranks first (0.7544), ahead of the approximate no-emoji hybrid (0.7515), full hybrid (0.7513), word SVM (0.7262), Naive Bayes (0.7021), and majority baseline (0.1729). The lower scores show that the original validation result was optimistic. This is a validation-only sensitivity analysis; it does not change the already selected deployed artifact or tune against test labels. Small differences are not claimed to be statistically significant.", s["body"])]
    story += [p("5.1 Held-out test performance", s["h2"])]
    cr = metrics["classification_report"]
    class_rows = [["Class", "Precision", "Recall", "F1", "Support"]]
    for label in ["negative", "neutral", "positive"]:
        class_rows.append([label.title(), f"{cr[label]['precision']:.4f}", f"{cr[label]['recall']:.4f}", f"{cr[label]['f1-score']:.4f}", f"{int(cr[label]['support']):,}"])
    class_rows += [["Macro avg", f"{metrics['macro_precision']:.4f}", f"{metrics['macro_recall']:.4f}", f"{metrics['macro_f1']:.4f}", "5,303"]]
    story += [make_table(class_rows, [4.1*cm, 2.6*cm, 2.6*cm, 2.6*cm, 2.6*cm], alignments=["LEFT","RIGHT","RIGHT","RIGHT","RIGHT"]), p("Table 4. Final performance on the untouched test split after refitting the selected configuration.", s["caption"])]
    story += [kpis([("0.7658", "TEST ACCURACY"), ("0.7649", "TEST MACRO-F1"), ("0.8446", "POSITIVE F1"), ("0.7044", "NEUTRAL F1")], s)]
    story += [Spacer(1, 0.3*cm), Image(str(ROOT / "outputs" / "figures" / "per_class_f1.png"), width=14.6*cm, height=7.84*cm), p("Figure 2. Held-out F1 by class. Macro-F1 makes the neutral-class weakness visible.", s["caption"])]
    story += [Spacer(1, 0.35*cm), p(
        "Positive sentiment is recognized most reliably. Neutral recall is 0.6574, meaning roughly one third of true neutral items are assigned another class. The 0.0049 gap between original validation and final test macro-F1 is not proof of stable generalization: the validation overlap and the different training sizes complicate that interpretation. Precision measures correctness among a class's predictions; recall measures coverage of its reference items. F1 = 2PR/(P + R), with zero-division conventions as in scikit-learn. Macro-F1 averages the three class F1 scores equally; weighted F1 weights them by reference support. Published Hausa Transformer figures use different data versions and sometimes different averaging, so they are context rather than a replicated head-to-head benchmark [1, 8].", s["body"])]

    story += section("Error Analysis and Discussion", s, 6)
    story += [Image(str(ROOT / "outputs" / "figures" / "confusion_matrix.png"), width=13.8*cm, height=10.73*cm), p("Figure 3. Held-out confusion matrix (n = 5,303).", s["caption"])]
    story += [p(
        "The model makes 1,242 errors. Of these, 613 occur on neutral items. The largest single confusion is neutral → negative (436 items), followed by negative → neutral (254). This asymmetry suggests that the learned boundary more readily treats neutral statements containing negative-looking fragments or topics as negative than the reverse. Because annotation disagreement is intrinsic to sentiment, some border cases may not have a single context-free interpretation.", s["body"])]
    story += [p("6.1 Descriptive slices", s["h2"])]
    slice_rows = [["Surface cue", "Present n", "Present error", "Absent error", "Difference"]]
    labels = {
        "short_5_tokens_or_less": "≤5 tokens",
        "contains_negation_marker": "Negation marker",
        "contains_question_cue": "Question cue",
        "contains_non_ascii": "Non-ASCII character",
    }
    for key, label in labels.items():
        present = slices[(slices["slice"] == key) & (slices["present"] == True)].iloc[0]
        absent = slices[(slices["slice"] == key) & (slices["present"] == False)].iloc[0]
        diff = present["error_rate"] - absent["error_rate"]
        slice_rows.append([label, f"{int(present['items']):,}", f"{present['error_rate']:.1%}", f"{absent['error_rate']:.1%}", f"{diff:+.1%}"])
    story += [make_table(slice_rows, [4.8*cm, 2.5*cm, 2.8*cm, 2.8*cm, 2.5*cm], alignments=["LEFT","RIGHT","RIGHT","RIGHT","RIGHT"]), p("Table 5. Surface-form error slices. These are descriptive indicators, not causal or validated linguistic categories.", s["caption"])]
    story += [Image(str(ROOT / "outputs" / "figures" / "error_by_length.png"), width=14.3*cm, height=9.15*cm), p("Figure 4. Error rate by whitespace-token length.", s["caption"])]
    story += [p(
        "Negation-marked messages have a 26.9% error rate versus 22.6% otherwise, and question-like cues have 27.6% versus 23.1%. Contrary to a simple ‘shorter is harder’ hypothesis, messages with five or fewer whitespace tokens are slightly easier than the rest. The highest length-bin error occurs at 11–20 tokens (26.4%); messages above 40 tokens are easiest (13.1%), possibly because they provide more redundant sentiment evidence. Non-ASCII characters, a broad proxy that includes Hausa letters and emoji, are associated with a lower error rate in this sample. None of these observational differences proves causation.", s["body"])]
    story += [p("6.2 Qualitative examples", s["h2"])]
    qual = [
        ["Outcome", "Gold → Predicted", "Held-out text", "Interpretation"],
        ["Success", "negative → negative", "wannan ai karyace", "Direct negative lexical cue; concise context."],
        ["Success", "positive → positive", "allah yah taimaka", "Frequent positive prayer/wish pattern."],
        ["Success", "neutral → neutral", "jirgin sama mai amfani da hasken rana", "Factual nominal phrase with little polarity."],
        ["Failure", "negative → neutral", "ni dai ban yafe ba", "Negation is present but the phrase is short and context-dependent."],
        ["Failure", "positive → negative", "amma ai gaskiya ta faɗa", "Adversative phrasing can resemble disagreement despite positive gold label."],
        ["Failure", "neutral → negative", "tanbayata itace meyasa yan jarida basa kamuwa da cutar corona virus", "Question contains disease and negation cues; topic words may dominate neutrality."],
    ]
    qual_wrapped = [[p(str(cell), s["small"]) for cell in row] for row in qual]
    story += [make_table(qual_wrapped, [1.8*cm, 2.9*cm, 6.1*cm, 5.1*cm], font_size=7.1), p("Table 6. Examples are reproduced from the held-out test set with original spelling. English glosses are omitted because no native-speaker validation was available.", s["caption"])]
    story += [p(
        "The examples point to four recurring challenges: neutral-versus-negative boundaries, explicit negation, rhetorical or conversational questions, and a lack of surrounding thread context. Character n-grams are effective at recognizing variable spellings, but they do not model compositional scope, sarcasm, who holds the opinion, or whether a phrase is quoted. A native-speaker-led error taxonomy would be the most important next analytical step.", s["body"])]

    story += section("Deployment", s, 7)
    story += [p(
        "The public system is deployed on GitHub Pages at the live-system link near the start of this report [11]. The build exports the actual learned vocabulary, IDF values, SVM coefficients, and intercepts from the Python joblib artifact into JSON. A JavaScript runtime reproduces normalization, character n-gram counting, sublinear TF-IDF, L2 normalization, linear class scores, and relative-confidence calculation. Text is processed in the visitor's browser. The original Python Streamlit application remains available locally [10]. Both interfaces show influential character patterns rather than claiming semantic understanding.", s["body"])]
    deployment_rows = [
        ["Layer", "Implementation", "Reproducibility role"],
        ["Data", "Official TSV files + downloader", "Row-count validation; raw data not duplicated in repo"],
        ["Training", "scikit-learn pipelines", "Prevents vocabulary leakage across splits"],
        ["Artifact", "Joblib (~1.3 MB); JSON (~3.8 MB)", "Same learned parameters in Python and JavaScript"],
        ["Interface", "GitHub Pages; local Streamlit", "Text, four examples, prediction, evidence, model card"],
        ["Testing", "pytest + numerical parity + browser", "Model equivalence, real interactions, mobile layout"],
    ]
    story += [make_table(deployment_rows, [3.0*cm, 5.2*cm, 7.6*cm], font_size=7.5), p("Table 7. Deployment architecture.", s["caption"])]
    story += [p(
        "Implementation parity was checked on all 5,303 test texts plus nine edge cases: zero label mismatches, zero normalization mismatches, and maximum absolute SVM-margin difference below 1e-10. This is a numerical implementation check without model tuning or new performance claims. The deployment workflow repeats parity before publication. Automated Chrome checks on the public URL passed positive, neutral, negative, known-error, blank-input, and mobile-layout paths with no JavaScript errors. Screenshot evidence is versioned. No demo video was generated; the student will record it independently.", s["body"])]
    story += [p(
        "The interface displays responsible-use notes and labels the margin-derived confidence as uncalibrated. User text is not sent to a prediction service. The roughly 3.8 MB JSON download is larger than the compressed Python artifact, but inference requires no Python server or commercial API. Source pushes to main trigger the GitHub Actions Pages workflow. Local reproduction and fallback instructions are in the README.", s["body"])]

    story += section("Limitations and Future Work", s, 8)
    limitations = [
        "Domain: evaluation covers the released Twitter test split only. Product reviews, radio transcripts, news comments, and customer-service messages may differ substantially.",
        "Language coverage: Hausa varieties, code-switching practices, orthographic conventions, and emerging slang are not uniformly represented. No language-identification gate is applied.",
        "Labels: a single positive/neutral/negative label cannot express mixed affect, sarcasm, stance toward multiple targets, or annotator disagreement.",
        "Method: linear character features do not represent long-range context or compositional negation. Relative SVM confidence is not probability calibration.",
        "Evaluation: the project did not conduct cross-domain, temporal, dialectal, fairness, robustness, or native-speaker acceptability studies.",
        "Validation independence: 215 normalized texts overlap training and validation. A supplementary overlap-free comparison confirms the character model's ranking, but does not erase the original design limitation.",
        "Privacy and governance: public tweets can still contain sensitive content. Raw split files are excluded, but test prediction/error CSVs and quoted examples contain released test text and retain dataset attribution obligations.",
    ]
    story += [bullet(x, s) for x in limitations]
    story += [p("Prioritized future work", s["h2"])]
    future = [
        "Run a native-speaker review of a stratified error sample, separating annotation ambiguity from model failure.",
        "Fine-tune AfriBERTa or AfroXLM-R under the identical split protocol and report compute, emissions proxy, artifact size, latency, and F1 together.",
        "Calibrate confidence on a reserved calibration set and add abstention for low-confidence or out-of-domain input.",
        "Collect consent-aware, naturally occurring evaluation data from at least one non-Twitter domain and a later time period.",
        "Test robustness to spelling variants, diacritics, code-switching, negation, emoji changes, and adversarial punctuation without changing labels.",
    ]
    story += [bullet(x, s) for x in future]

    story += section("Conclusion", s, 9)
    story += [p(
        "HausaLens demonstrates a complete, reproducible African-language NLP workflow rather than a web wrapper around an existing chatbot. Using 22,152 human-annotated NaijaSenti Hausa tweets, the project established a majority baseline, compared five learned configurations, selected exclusively on validation macro-F1, evaluated once on the held-out test set, and deployed the fitted artifact. Character 3–5 gram TF-IDF with a class-balanced linear SVM was the strongest local configuration, achieving 0.7649 test macro-F1 and a small 1.3 MB footprint.", s["body"])]
    story += [p(
        "The central empirical lesson is that subword form matters: character features outperform word features on this informal dataset, while adding word features provides no gain. The central analytical lesson is that aggregate accuracy conceals a substantial neutral-class weakness and elevated errors around negation and questions. The central engineering lesson is that a modest model can still support transparent, CPU-friendly deployment. The system is useful as an educational baseline and research prototype, but stronger contextual models, probability calibration, cross-domain data, and native-speaker-led evaluation are required before broader use.", s["body"])]

    story += section("References", s, 10)
    references = [
        "[1] Muhammad, S. H., Adelani, D. I., Ruder, S., et al. (2022). NaijaSenti: A Nigerian Twitter Sentiment Corpus for Multilingual Sentiment Analysis. Proceedings of LREC 2022, 590–602. https://aclanthology.org/2022.lrec-1.63/",
        "[2] Muhammad, S. H., Abdulmumin, I., Yimam, S. M., et al. (2023). SemEval-2023 Task 12: Sentiment Analysis for African Languages (AfriSenti-SemEval). Proceedings of SemEval-2023, 2319–2337. https://doi.org/10.18653/v1/2023.semeval-1.315",
        "[3] Ogueji, K., Zhu, Y., & Lin, J. (2021). Small Data? No Problem! Exploring the Viability of Pretrained Multilingual Language Models for Low-resourced Languages. MRL 2021, 116–126. https://doi.org/10.18653/v1/2021.mrl-1.11",
        "[4] Keinan, R., & Hacohen-Kerner, Y. (2023). JCT at SemEval-2023 Tasks 12 A and 12B: Sentiment Analysis for Tweets Written in Low-resource African Languages. SemEval-2023, 365–378. https://doi.org/10.18653/v1/2023.semeval-1.49",
        "[5] Cortes, C., & Vapnik, V. (1995). Support-vector networks. Machine Learning, 20, 273–297. https://doi.org/10.1007/BF00994018",
        "[6] HausaNLP. (2022). NaijaSenti dataset repository, v1.0. https://github.com/hausanlp/NaijaSenti (accessed 25 September 2026).",
        "[7] scikit-learn developers. (2026). TfidfVectorizer documentation. https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html (accessed 25 September 2026).",
        "[8] Salahudeen, S. A., Lawan, F. I., Wali, A. M., et al. (2023). HausaNLP at SemEval-2023 Task 12: Leveraging African Low Resource TweetData for Sentiment Analysis. SemEval-2023, 58–66. https://aclanthology.org/2023.semeval-1.6/",
        "[9] Pedregosa, F., Varoquaux, G., Gramfort, A., et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825–2830. https://jmlr.org/papers/v12/pedregosa11a.html",
        "[10] Streamlit. (2026). Streamlit documentation. https://docs.streamlit.io/ (accessed 25 September 2026).",
        "[11] GitHub. (2026). Using custom workflows with GitHub Pages. https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages (accessed 16 October 2026).",
        "[12] ReportLab. (2026). ReportLab documentation. https://docs.reportlab.com/ (accessed 16 October 2026).",
    ]
    for ref in references:
        story.append(p(ref, s["small"]))

    story += section("Appendix A — Reproducibility and Individual Contribution", s)
    story += [p("A.1 Exact workflow", s["h2"])]
    workflow = [
        ["Step", "Command", "Output"],
        ["1", "python scripts/download_data.py", "Validated official train/dev/test TSV files"],
        ["2", "python scripts/train.py", "Six validation runs, final test metrics, model, predictions, figures"],
        ["3", "python scripts/analyze_errors.py", "Error slices and length analysis"],
        ["3a", "python scripts/audit_data.py", "Missing rows, duplicates, normalized split overlap"],
        ["3b", "python scripts/validate_selection.py", "Overlap-free validation sensitivity comparison"],
        ["4", "pytest -q", "Automated normalization and inference tests"],
        ["5", "streamlit run app.py", "Interactive local web interface"],
        ["6", "python scripts/build_report.py", "This report from measured outputs"],
        ["7", "python scripts/export_web_model.py", "Learned parameters for public browser inference"],
        ["8", "python scripts/verify_web_model.py", "Python/JavaScript numerical-equivalence evidence"],
    ]
    story += [make_table(workflow, [1.2*cm, 6.2*cm, 8.4*cm], font_size=7.5), p("Table A1. Reproduction sequence.", s["caption"])]
    story += [p("A.2 Runtime and artifacts", s["h2"])]
    runtime = metrics["runtime"]
    story += [p(
        f"The reported experiment ran with Python {runtime['python']} and scikit-learn {runtime['scikit_learn']} on {runtime['platform']}. Deterministic split files were supplied by the dataset publisher; no random resampling was used. The trained model, raw prediction file, error-only file, confusion matrix, experiment table, metrics JSON, and figures are versioned project outputs. The raw tweet TSV files are excluded and can be reacquired with attribution.", s["body"])]
    story += [p("A.3 What was implemented in this project", s["h2"])]
    for item in [
        "Implemented: data validation and preprocessing pipeline; six model configurations; metric computation; selection protocol; held-out evaluation; error slicing; visualizations; local explanation utility; Streamlit interface; tests; documentation; PDF builder; demo assets.",
        "Reused with attribution: NaijaSenti annotations and split files; scikit-learn estimators and vectorizers; Streamlit framework; ReportLab and plotting libraries; published benchmark findings.",
        "Not used: synthetic training data, commercial sentiment APIs, hosted chatbot inference, or manual alteration of test predictions.",
        "AI assistance: AI tools assisted coding, documentation, deployment, and verification. The student is responsible for understanding and checking the work, recording the 10-15 minute demonstration, and answering the individual technical defense.",
        "Submission status: source code and public application are available at the links in this report. The personal demonstration video is pending and must be linked before final submission. The script's --video-url option rebuilds the report with the verified video URL.",
    ]:
        story.append(bullet(item, s))
    story.append(p("Verification evidence: outputs/data_audit.json, outputs/validation_sensitivity.csv, outputs/web_parity.json, and outputs/deployment_verification.json. The complete submission checklist and personal recording guide are linked from the README.", s["small"]))

    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-url", help="Accessible URL of the student's own final demonstration")
    args = parser.parse_args()
    if args.video_url and not args.video_url.startswith("https://"):
        parser.error("--video-url must be a public HTTPS URL")
    build(args.video_url)
