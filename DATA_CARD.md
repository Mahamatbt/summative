# Data card: NaijaSenti Hausa

## Source and intended use

HausaLens uses the Hausa split files published in the official [HausaNLP/NaijaSenti repository](https://github.com/hausanlp/NaijaSenti). NaijaSenti contains naturally occurring tweets collected and annotated for sentiment research. It is not synthetic data. The repository identifies the resource as CC BY 4.0 and requests citation of Muhammad et al. (2022).

## Labels and splits

The task has three mutually exclusive labels: `negative`, `neutral`, and `positive`. This project preserves the provided train, development, and test split boundaries. It does not tune on test labels.

| Split | Rows | Negative | Neutral | Positive |
|---|---:|---:|---:|---:|
| Train | 14,172 | 4,573 | 4,912 | 4,687 |
| Development | 2,677 | 894 | 896 | 887 |
| Test | 5,303 | 1,759 | 1,789 | 1,755 |

The release used here differs from the earlier counts in the LREC 2022 paper. The exact official repository files and row counts above are therefore the reproducibility authority for this project.

## Preparation

Rows with missing text or labels would be removed, and exact duplicate rows are removed within each split. No rows were lost in this release. User handles and URLs are mapped to stable tokens. Text is lowercased and whitespace is collapsed. Hausa characters, punctuation, hashtags, and emoji are otherwise preserved. The winning model uses character n-grams, so it does not require tokenization or stop-word removal.

## Risks and limitations

Tweets can contain personal, political, religious, sarcastic, offensive, or context-dependent language. Although account handles are normalized in the model pipeline, the raw dataset should be handled carefully. The corpus represents a particular platform and time period, and is not a representative sample of all Hausa speakers or varieties. Labels compress mixed and contextual affect into three classes. Dataset annotations and downstream predictions can both be wrong.

