"""Verify app title updates when spelform (game type) changes."""

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
          spelform: document.getElementById('spelform').value
        })"""
    )


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector("#app-headline", timeout=20000)

        initial = read_title_state(page)
        page.locator(".game-header").screenshot(
            path=str(OUT_DIR / "test-title-v85.png")
        )

        # V75 is disabled in UI today; enable briefly to verify title wiring.
        page.evaluate(
            """() => {
              const opt = document.querySelector('#spelform option[value="V75"]');
              if (opt) opt.disabled = false;
              const sel = document.getElementById('spelform');
              sel.value = 'V75';
              sel.dispatchEvent(new Event('change', { bubbles: true }));
            }"""
        )
        v75 = read_title_state(page)
        page.locator(".game-header").screenshot(
            path=str(OUT_DIR / "test-title-v75.png")
        )

        page.select_option("#spelform", "V85")
        back = read_title_state(page)

        print("=== Initial (V85) ===")
        print(initial)
        print("Screenshot:", OUT_DIR / "test-title-v85.png")
        print()
        print("=== After change to V75 ===")
        print(v75)
        print("Screenshot:", OUT_DIR / "test-title-v75.png")
        print()
        print("=== After change back to V85 ===")
        print(back)

        ok = (
            initial["headline"] == "VAI V85"
            and initial["pageTitle"] == "VAI V85 — ATG UX v1.1 (Local UI)"
            and initial["logoTitle"] == "VAI V85"
            and initial["spelform"] == "V85"
            and v75["headline"] == "VAI V75"
            and v75["pageTitle"] == "VAI V75 — ATG UX v1.1 (Local UI)"
            and v75["logoTitle"] == "VAI V75"
            and v75["spelform"] == "V75"
            and back["headline"] == "VAI V85"
            and back["pageTitle"] == "VAI V85 — ATG UX v1.1 (Local UI)"
            and back["spelform"] == "V85"
        )
        print()
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())