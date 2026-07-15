"""Verify app title shows VAI V85 (V85-only spelform; V75 discontinued at ATG)."""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
OUT_DIR = Path(__file__).resolve().parent


def read_title_state(page) -> dict[str, str]:
    return page.evaluate(
        """() => ({
          headline: document.getElementById('app-headline').textContent.trim(),
          pageTitle: document.title,
          logoTitle: document.getElementById('app-logo').getAttribute('title'),
          spelform: document.getElementById('spelform').value,
          spelformOptions: Array.from(document.getElementById('spelform').options).map(o => o.value)
        })"""
    )


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector("#app-headline", timeout=20000)

        state = read_title_state(page)
        page.locator(".game-header").screenshot(path=str(OUT_DIR / "test-title-v85.png"))

        print("=== V85 title state ===")
        print(state)
        print("Screenshot:", OUT_DIR / "test-title-v85.png")

        ok = (
            state["headline"] == "VAI V85"
            and state["pageTitle"] == "VAI V85 — Local UI v1.1.3"
            and state["logoTitle"] == "VAI V85"
            and state["spelform"] == "V85"
            and state["spelformOptions"] == ["V85"]
        )
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())