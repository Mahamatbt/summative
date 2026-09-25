#!/usr/bin/env python3
"""Download the official NaijaSenti Hausa split files."""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/hausanlp/NaijaSenti/main/data/annotated_tweets/hau"
EXPECTED_ROWS = {"train": 14_172, "dev": 2_677, "test": 5_303}


def main() -> None:
    output = Path("data/raw")
    output.mkdir(parents=True, exist_ok=True)
    for split, expected in EXPECTED_ROWS.items():
        destination = output / f"{split}.tsv"
        urllib.request.urlretrieve(f"{BASE}/{split}.tsv", destination)
        rows = sum(1 for _ in destination.open(encoding="utf-8")) - 1
        if rows != expected:
            raise RuntimeError(f"{split}: expected {expected} rows, found {rows}")
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()[:12]
        print(f"{split:>5}: {rows:>6,} rows  sha256={digest}")


if __name__ == "__main__":
    main()

