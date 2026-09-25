#!/usr/bin/env python3
"""Build a narrated 7–10 minute HausaLens capstone demonstration video."""

from __future__ import annotations

import json
import shutil
import subprocess
import textwrap
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
ASSETS = DEMO / "assets"
TMP = DEMO / "build"
WIDTH, HEIGHT = 1280, 720
GREEN = "#173D25"
MID_GREEN = "#2E6A3E"
PALE_GREEN = "#E7F0E8"
GOLD = "#F4B942"
CREAM = "#F7F2E8"
INK = "#17251B"
MUTED = "#5D6A60"
RED = "#A64B35"
FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


@dataclass
class Slide:
    title: str
    kicker: str
    bullets: list[str]
    narration: str
    visual: str | None = None
    layout: str = "split"


SLIDES = [
    Slide(
        "HausaLens",
        "INDIVIDUAL AFRICAN NLP CAPSTONE",
        ["Hausa social-media sentiment", "22,152 human-annotated examples", "Six experiments · held-out evaluation · deployed interface"],
        "Hello, and welcome to my capstone demonstration. This project is called HausaLens. It is a text-classification system for sentiment in informal Hausa social-media messages. The application predicts whether a message is positive, neutral, or negative. My objective was not only to put a label behind a web form. I built a complete machine-learning workflow: obtaining and validating real data, defining a simple baseline, comparing multiple learned models, selecting a model without looking at the test labels, evaluating it quantitatively, analyzing errors, and deploying the exact fitted artifact through an interactive interface. In this video I will explain the problem, data, methodology, experiments, results, limitations, and application. All headline numbers shown here come from reproducible output files in the repository.",
        layout="title",
    ),
    Slide(
        "Why Hausa sentiment?",
        "PROBLEM & MOTIVATION",
        [
            "Useful for feedback and public-opinion research",
            "Informal spelling, code-switching, emoji, and missing context",
            "Low-resource setting rewards efficient, transparent baselines",
        ],
        "Sentiment analysis can summarize opinions in feedback, public discussion, and service interactions. Yet most mature tools and datasets favor high-resource languages. Hausa is widely used online, but informal messages vary in spelling, mix languages, include prayers and idioms, and often depend on a conversation that the model cannot see. These properties make the task technically interesting and socially relevant. I chose a lightweight, inspectable approach because a capstone should establish what can be achieved under realistic resource constraints. I also kept the scope precise: this is sentiment classification for social-media-style Hausa, not a general Hausa-understanding system. The model is a research prototype and must not be used to profile individuals or make high-impact decisions.",
    ),
    Slide(
        "A real, human-annotated dataset",
        "DATASET · NAIJASENTI HAUSA",
        [
            "Train 14,172 · validation 2,677 · test 5,303",
            "Negative 7,226 · neutral 7,597 · positive 7,329",
            "Official split boundaries preserved; no synthetic training data",
            "CC BY 4.0, with publisher attribution",
        ],
        "The training resource is the Hausa portion of NaijaSenti, published by Muhammad and colleagues. These are naturally occurring tweets labeled by human annotators; synthetic text is not the primary dataset, or even part of training. The current official repository release contains twenty-two thousand one hundred fifty-two examples. Fourteen thousand one hundred seventy-two are used for training, two thousand six hundred seventy-seven for validation, and five thousand three hundred three for the final test. The three labels are close to balanced. I preserve the publisher’s split boundaries so the evaluation is comparable and leakage-resistant. The project documents an important version detail: an early paper reports larger Hausa split counts, while the official files used here match the later AfriSenti release. My downloader checks the actual row counts, and the report states this discrepancy explicitly.",
        layout="dataset",
    ),
    Slide(
        "Conservative preparation",
        "DATA PIPELINE",
        [
            "Normalize URLs and account handles",
            "Lowercase and collapse whitespace",
            "Preserve Hausa characters, punctuation, hashtags, and emoji",
            "Fit every vocabulary inside the training pipeline",
        ],
        "Preprocessing is deliberately conservative. URLs and account names are mapped to stable tokens, text is lowercased, and repeated whitespace is collapsed. Hausa characters, punctuation, hashtags, and emoji are preserved because they may carry sentiment. I do not remove stop words or apply stemming. Every TF-IDF vocabulary is fitted inside its experiment pipeline on training data only. This prevents information from the validation or test set from influencing the feature space. Rows with missing values or exact duplicates would be removed, but the official files used in this run did not lose any rows. The training script records metrics, predictions, confusion matrices, figures, the selected model, and the exact software runtime so that each claim in the report can be traced back to an artifact.",
        layout="pipeline",
    ),
    Slide(
        "Six controlled experiments",
        "BASELINES & MODEL SELECTION",
        [
            "Majority class → macro-F1 0.167",
            "Word unigram + Naive Bayes → 0.716",
            "Word 1–2 gram SVM → 0.743",
            "Character 3–5 gram SVM → 0.770",
            "Hybrid models → about 0.766",
        ],
        "I compared six configurations on exactly the same validation split. The majority classifier establishes a minimum baseline and reaches only zero point one six seven macro F one. Word-unigram TF-IDF with Multinomial Naive Bayes reaches zero point seven one six. A discriminative linear support-vector machine using word unigrams and bigrams improves to zero point seven four three. The best model uses character three-to-five grams and reaches zero point seven seven zero. I also test a union of word and character features, with and without emoji. Both hybrid versions score about zero point seven six six, so adding feature families does not automatically help. The character model is selected because it has the highest validation macro F one. Character fragments are a practical fit for spelling variation and informal morphology, and the linear SVM stays compact and CPU-friendly.",
        visual="outputs/figures/experiment_comparison.png",
    ),
    Slide(
        "Held-out result",
        "FINAL TEST · N = 5,303",
        [
            "Accuracy 0.7658 · macro-F1 0.7649",
            "Positive F1 0.8446",
            "Negative F1 0.7456",
            "Neutral F1 0.7044",
        ],
        "After model selection, I refit the character model on training plus validation, for sixteen thousand eight hundred forty-nine examples. Then I evaluate once on the untouched test set. Accuracy is zero point seven six five eight and macro F one is zero point seven six four nine. The validation-to-test decrease is less than half a percentage point, which suggests stable selection. Per-class results are more informative than the aggregate. Positive sentiment is easiest, with F one of zero point eight four four six. Negative reaches zero point seven four five six. Neutral is the weakest at zero point seven zero four four. Published Afrocentric transformer systems achieve higher Hausa scores, roughly around zero point eight one weighted F one, so I present HausaLens as a compact baseline with deployment advantages, not a state-of-the-art claim.",
        visual="outputs/figures/per_class_f1.png",
    ),
    Slide(
        "Where the model fails",
        "ERROR ANALYSIS",
        [
            "1,242 total errors; 613 come from neutral items",
            "Neutral → negative is the largest confusion",
            "Negation markers and question cues show higher error rates",
            "Observational slices are not causal explanations",
        ],
        "The confusion matrix reveals the largest weakness. The model makes one thousand two hundred forty-two errors, and six hundred thirteen of them are on neutral examples. Four hundred thirty-six neutral messages are predicted as negative. Descriptive slices add detail: messages containing a simple negation marker have a twenty-six point nine percent error rate, compared with twenty-two point six percent otherwise. Question-like cues also show higher errors. Interestingly, very short messages are not the hardest; the eleven-to-twenty-token group has the highest length-bin error, while messages longer than forty tokens are easier, perhaps because they contain redundant evidence. These slices are surface-form indicators, not causal linguistic claims. A native-speaker-led review would be necessary to separate annotation ambiguity, cultural context, and genuine model failure.",
        visual="outputs/figures/confusion_matrix.png",
    ),
    Slide(
        "Interactive inference: positive",
        "WEB APPLICATION",
        [
            "Exact fitted model, loaded locally",
            "Prediction + margin-based relative confidence",
            "Input-specific influential character patterns",
            "Visible model card and limitations",
        ],
        "Now I will demonstrate the application. This screen is captured from the running Streamlit interface, not a mockup. The example says, Allah ya saka da alheri, na gode sosai, a positive expression of thanks and good wishes. HausaLens returns Positive. It also shows a relative confidence and the character patterns that contributed most strongly to the positive decision. The confidence is derived from support-vector margins and the interface clearly says that it is not a calibrated probability. On the right, the model card keeps held-out macro F one, accuracy, dataset, model family, and limitations visible. No commercial classifier or chatbot is called. The same serialized scikit-learn pipeline evaluated in the experiment runs inside the application.",
        visual="demo/assets/app_positive.png",
        layout="app",
    ),
    Slide(
        "Interactive inference: contrasting cases",
        "WEB APPLICATION",
        [
            "Neutral example → Neutral",
            "Negative example → Negative",
            "All three paths manually tested",
            "Explanations expose fragments, not human reasoning",
        ],
        "The next two captures show contrasting cases. A factual scheduling sentence is labeled Neutral. A sentence expressing that something caused distress is labeled Negative. I manually tested all three example paths in the application and verified that each rendered its expected label, confidence bar, and feature evidence. The different confidence values also show why the score must not be overinterpreted. Local feature evidence is useful for debugging a linear model, because it tells us which observed character fragments moved the decision. It is not a semantic explanation of intent, sarcasm, or context. The interface therefore pairs transparency with a responsible-use warning rather than suggesting that a numeric score makes the system infallible.",
        layout="apps",
    ),
    Slide(
        "Reproducible from data to deployment",
        "ENGINEERING & REPOSITORY",
        [
            "download_data.py validates official splits",
            "train.py runs selection and final evaluation",
            "analyze_errors.py creates documented slices",
            "pytest verifies normalization and inference",
            "app.py serves the 1.3 MB model artifact",
        ],
        "The repository is organized around reproducibility. The data downloader retrieves the official files and validates their row counts. The training script executes all six experiments, saves validation metrics, selects the winner, refits it, and produces the held-out predictions and figures. The error-analysis script derives slices from those predictions. Automated tests check platform-artifact normalization, preservation of Hausa characters and emoji, and end-to-end inference. The web app loads a compressed model of roughly one point three megabytes. Raw tweets are not duplicated in the repository; they are downloaded from the attributed source. The README, data card, model card, report builder, and demo script make the full workflow inspectable. This organization also makes it straightforward to replace the linear model with an Afrocentric transformer in a future controlled comparison.",
        layout="repo",
    ),
    Slide(
        "Limitations and future work",
        "RESPONSIBLE CONCLUSION",
        [
            "Twitter-only evaluation and temporal drift",
            "Neutral, negation, sarcasm, and context remain difficult",
            "No native-speaker audit or cross-domain fairness study",
            "Next: AfroXLM-R comparison, calibration, and abstention",
        ],
        "HausaLens has important limitations. Evaluation covers one social-media dataset and time period, so results should not be generalized to reviews, call-center text, formal writing, or every Hausa variety. Three labels cannot represent mixed sentiment or multiple targets. Character n-grams do not understand long-range negation, sarcasm, or conversation context. The confidence display is not calibrated, and this capstone did not include a native-speaker error audit, temporal test, dialectal study, or fairness evaluation. My next steps would be to conduct a stratified native-speaker review, fine-tune AfriBERTa or AfroXLM-R under the same split protocol, measure accuracy alongside latency and artifact size, calibrate scores on a reserved set, and add abstention for low-confidence or out-of-domain input. The main conclusion is that a compact, transparent model can form a credible baseline, but responsible deployment requires explicit boundaries and continued evaluation.",
    ),
    Slide(
        "What I learned",
        "CONCLUSION",
        [
            "Subword form beats word-only features here",
            "More features do not guarantee a better model",
            "Macro-F1 reveals a neutral-class weakness",
            "Deployment should expose evidence and limitations",
        ],
        "To conclude, this project fulfills the capstone as an end-to-end machine-learning investigation. It uses real human-annotated Hausa data, establishes a baseline, runs controlled experiments, selects without test leakage, reports multiple metrics, analyzes concrete failures, and deploys the trained artifact. The empirical lesson is that character-level subword form matters for this informal dataset, while combining additional word features brings no improvement. The analytical lesson is that accuracy alone hides a substantial neutral-class weakness. The engineering lesson is that transparent, local inference can be practical with a small model. Thank you for watching. The repository contains the complete source, trained model, measured outputs, PDF report, and instructions for running HausaLens locally or visiting the deployed application.",
        layout="final",
    ),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD if bold else FONT, size)


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width_px: int, *, size: int, fill: str, bold: bool = False, spacing: int = 8) -> int:
    f = font(size, bold)
    avg = max(1, int(width_px / (size * 0.54)))
    lines = textwrap.wrap(text, width=avg, break_long_words=False)
    y = xy[1]
    for line in lines:
        draw.text((xy[0], y), line, font=f, fill=fill)
        y += size + spacing
    return y


def fit_image(path: Path, box: tuple[int, int, int, int], background=CREAM) -> Image.Image:
    image = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = box
    image.thumbnail((x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (x1 - x0, y1 - y0), background)
    canvas.paste(image, ((canvas.width - image.width) // 2, (canvas.height - image.height) // 2))
    return canvas


def chrome(draw: ImageDraw.ImageDraw, slide: Slide, number: int) -> None:
    draw.text((56, 34), slide.kicker, font=font(17, True), fill=GOLD)
    draw.text((56, 66), slide.title, font=font(42, True), fill=GREEN)
    draw.line((56, 126, 1224, 126), fill="#CBD6CC", width=2)
    draw.text((1190, 680), f"{number:02d}", font=font(16, True), fill=MUTED)


def bullet_list(draw: ImageDraw.ImageDraw, bullets: list[str], x: int, y: int, width_px: int, size: int = 25, gap: int = 15) -> None:
    for text in bullets:
        draw.ellipse((x, y + 9, x + 10, y + 19), fill=GOLD)
        y = draw_wrapped(draw, text, (x + 25, y), width_px - 25, size=size, fill=INK, spacing=7) + gap


def render_slide(slide: Slide, number: int, destination: Path) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), CREAM)
    draw = ImageDraw.Draw(image)
    if slide.layout == "title":
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill=GREEN)
        draw.ellipse((1050, -100, 1380, 230), fill=MID_GREEN)
        draw.ellipse((1080, 570, 1360, 850), fill="#29583A")
        draw.text((70, 70), slide.kicker, font=font(18, True), fill=GOLD)
        draw.text((70, 170), slide.title, font=font(78, True), fill="white")
        draw.text((70, 265), "Lightweight sentiment classification for Hausa", font=font(31), fill="#EAF3EB")
        draw.line((70, 335, 330, 335), fill=GOLD, width=7)
        y = 390
        for text in slide.bullets:
            draw.text((72, y), text, font=font(24), fill="white")
            y += 58
    elif slide.layout == "final":
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill=GREEN)
        draw.text((60, 45), slide.kicker, font=font(18, True), fill=GOLD)
        draw.text((60, 95), slide.title, font=font(54, True), fill="white")
        y = 190
        for text in slide.bullets:
            draw.rounded_rectangle((60, y, 1190, y + 85), radius=16, fill="#245C37")
            draw.ellipse((88, y + 34, 100, y + 46), fill=GOLD)
            draw.text((122, y + 24), text, font=font(27), fill="white")
            y += 105
        draw.text((60, 660), "github.com/Mahamatbt/hausalens", font=font(18), fill="#EAF3EB")
    else:
        chrome(draw, slide, number)
        if slide.layout == "dataset":
            bullet_list(draw, slide.bullets, 60, 175, 540, 24)
            labels = [("14,172", "TRAIN"), ("2,677", "VALIDATION"), ("5,303", "TEST"), ("22,152", "TOTAL")]
            positions = [(675, 200), (970, 200), (675, 420), (970, 420)]
            for (value, label), (x, y) in zip(labels, positions):
                draw.rounded_rectangle((x, y, x + 240, y + 155), radius=18, fill=PALE_GREEN, outline="#C4D5C7", width=2)
                draw.text((x + 28, y + 30), value, font=font(40, True), fill=GREEN)
                draw.text((x + 30, y + 97), label, font=font(16, True), fill=MUTED)
        elif slide.layout == "pipeline":
            stages = [("1", "DOWNLOAD", "Official TSV"), ("2", "NORMALIZE", "Conservative"), ("3", "TRAIN", "Six models"), ("4", "SELECT", "Validation"), ("5", "TEST", "Once"), ("6", "DEPLOY", "Same artifact")]
            y = 225
            for i, (num, heading, sub) in enumerate(stages):
                x = 45 + i * 203
                draw.rounded_rectangle((x, y, x + 165, y + 150), radius=16, fill=PALE_GREEN, outline="#C4D5C7", width=2)
                draw.ellipse((x + 17, y + 16, x + 57, y + 56), fill=GOLD)
                draw.text((x + 31, y + 24), num, font=font(18, True), fill=GREEN)
                draw.text((x + 18, y + 78), heading, font=font(18, True), fill=GREEN)
                draw.text((x + 18, y + 112), sub, font=font(16), fill=MUTED)
                if i < len(stages) - 1:
                    draw.line((x + 168, y + 75, x + 196, y + 75), fill=GOLD, width=5)
            bullet_list(draw, slide.bullets, 70, 475, 1140, 23, 9)
        elif slide.layout == "app":
            visual = fit_image(ROOT / slide.visual, (590, 150, 1220, 670), background="#EEE9DF")
            image.paste(visual, (590, 150))
            bullet_list(draw, slide.bullets, 60, 180, 480, 24, 14)
        elif slide.layout == "apps":
            left = fit_image(ASSETS / "app_neutral.png", (45, 160, 635, 650), background="#EEE9DF")
            right = fit_image(ASSETS / "app_negative.png", (645, 160, 1235, 650), background="#EEE9DF")
            image.paste(left, (45, 160)); image.paste(right, (645, 160))
            draw.rounded_rectangle((72, 575, 370, 630), radius=13, fill=PALE_GREEN)
            draw.text((92, 589), "NEUTRAL PATH VERIFIED", font=font(17, True), fill=GREEN)
            draw.rounded_rectangle((675, 575, 985, 630), radius=13, fill="#F1E6E1")
            draw.text((695, 589), "NEGATIVE PATH VERIFIED", font=font(17, True), fill=RED)
        elif slide.layout == "repo":
            bullet_list(draw, slide.bullets, 60, 175, 620, 24, 13)
            draw.rounded_rectangle((735, 170, 1205, 620), radius=20, fill=GREEN)
            tree = ["hausalens/", "├── app.py", "├── src/hausalens/", "├── scripts/", "│   ├── train.py", "│   └── analyze_errors.py", "├── tests/", "├── outputs/", "├── report/", "└── demo/"]
            y = 205
            for line in tree:
                draw.text((775, y), line, font=font(22, line == "hausalens/"), fill=GOLD if line == "hausalens/" else "white")
                y += 37
        elif slide.visual:
            bullet_list(draw, slide.bullets, 60, 175, 500, 23, 11)
            visual = fit_image(ROOT / slide.visual, (575, 155, 1220, 650))
            image.paste(visual, (575, 155))
        else:
            bullet_list(draw, slide.bullets, 75, 185, 1120, 30, 26)

    image.save(destination, quality=95)


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def seconds(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def stamp(value: float) -> str:
    millis = int(round(value * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main() -> None:
    if TMP.exists():
        shutil.rmtree(TMP)
    (TMP / "slides").mkdir(parents=True)
    (TMP / "audio").mkdir()
    (TMP / "segments").mkdir()
    DEMO.mkdir(exist_ok=True)

    script_lines = ["# HausaLens demonstration narration", ""]
    srt = []
    concat = []
    elapsed = 0.0

    for index, slide in enumerate(SLIDES, 1):
        image_path = TMP / "slides" / f"slide_{index:02d}.png"
        audio_path = TMP / "audio" / f"slide_{index:02d}.aiff"
        segment_path = TMP / "segments" / f"slide_{index:02d}.mp4"
        render_slide(slide, index, image_path)
        run(["say", "-v", "Samantha", "-r", "180", "-o", str(audio_path), slide.narration])
        duration = seconds(audio_path) + 1.1
        run([
            "ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-i", str(image_path), "-i", str(audio_path),
            "-vf", "scale=1280:720,fps=24,format=yuv420p", "-af", "apad=pad_dur=1.1", "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "112k", "-movflags", "+faststart", str(segment_path),
        ])
        concat.append(f"file '{segment_path.resolve()}'")
        script_lines += [f"## {index}. {slide.title}", "", slide.narration, ""]
        srt += [str(index), f"{stamp(elapsed / 1.06)} --> {stamp((elapsed + duration - 0.4) / 1.06)}", slide.narration, ""]
        elapsed += duration

    concat_path = TMP / "concat.txt"
    concat_path.write_text("\n".join(concat) + "\n", encoding="utf-8")
    raw_output = TMP / "hausalens_demo_raw.mp4"
    output = DEMO / "hausalens_demo.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_path), "-c", "copy", str(raw_output)])
    # Final pacing pass keeps the presentation inside the requested 7–10 minute window.
    run([
        "ffmpeg", "-loglevel", "error", "-y", "-i", str(raw_output),
        "-filter_complex", "[0:v]setpts=PTS/1.06[v];[0:a]atempo=1.06[a]",
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
        "-c:a", "aac", "-b:a", "112k", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output),
    ])
    (DEMO / "narration_script.md").write_text("\n".join(script_lines), encoding="utf-8")
    (DEMO / "hausalens_demo.srt").write_text("\n".join(srt), encoding="utf-8")
    print(json.dumps({"video": str(output), "duration_seconds": round(seconds(output), 2), "slides": len(SLIDES)}, indent=2))


if __name__ == "__main__":
    main()
