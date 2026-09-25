#!/usr/bin/env python3
"""Capture verified HausaLens states from a running local Streamlit server."""

from pathlib import Path

from playwright.sync_api import sync_playwright

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CASES = {
    "positive": "Positive",
    "neutral": "Neutral",
    "negative": "Negative",
}


def main() -> None:
    output = Path("demo/assets")
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=CHROME)
        page = browser.new_page(viewport={"width": 1280, "height": 1100}, device_scale_factor=1)
        for case, label in CASES.items():
            page.goto(f"http://127.0.0.1:8501/?demo={case}", wait_until="domcontentloaded")
            page.get_by_text(label, exact=True).last.wait_for(state="visible", timeout=30_000)
            page.get_by_text("Influential text patterns", exact=True).wait_for(state="visible", timeout=30_000)
            page.screenshot(path=str(output / f"app_{case}.png"), full_page=True)
            print(f"captured {case}: {page.title()}")
        browser.close()


if __name__ == "__main__":
    main()

