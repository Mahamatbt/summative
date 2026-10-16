#!/usr/bin/env python3
"""Exercise the real public interface and save screenshot evidence (no video)."""

from __future__ import annotations

import argparse
import functools
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CASES = {"positive": "Positive", "neutral": "Neutral", "negative": "Negative", "failure": "Negative"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://mahamatbt.github.io/summative/")
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()
    server = None
    if args.local:
        handler = functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT / "web"))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        args.url = f"http://127.0.0.1:{server.server_port}/"
    output = ROOT / "demo/assets"
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, executable_path=CHROME)
            page = browser.new_page(viewport={"width": 1280, "height": 1100}, device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            response = page.goto(args.url, wait_until="networkidle", timeout=60000)
            assert response and response.ok, "Application HTTP request failed"
            analyze = page.get_by_role("button", name="Analyze sentiment")
            analyze.wait_for(state="visible")
            for case, expected in CASES.items():
                page.locator(f'[data-example="{case}"]').click()
                analyze.click()
                page.locator("#prediction").filter(has_text=expected).wait_for()
                actual = page.locator("#prediction").inner_text()
                assert actual == expected, (case, actual)
                assert page.locator("#evidence code").count() > 0
                if case == "failure":
                    assert page.locator("#reference-note").is_visible()
                page.screenshot(path=str(output / f"live_{case}.png"), full_page=True)
                checks.append({"case": case, "prediction": actual, "passed": True})
            page.locator("#message").fill("   ")
            analyze.click()
            assert page.locator("#result").is_hidden()
            assert "Enter some Hausa text" in page.locator("#status").inner_text()
            checks.append({"case": "blank-input validation", "passed": True})
            page.set_viewport_size({"width": 390, "height": 844})
            page.locator('[data-example="positive"]').click()
            analyze.click()
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Mobile layout overflows"
            page.screenshot(path=str(output / "live_mobile.png"), full_page=True)
            checks.append({"case": "mobile layout", "passed": True})
            assert not errors, errors
            browser.close()
    finally:
        if server:
            server.shutdown()
    summary = {"url": args.url, "checks": checks, "browser_errors": errors, "video_created": False}
    destination = ROOT / "outputs" / ("local_ui_verification.json" if args.local else "deployment_verification.json")
    destination.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
