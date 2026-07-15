"""Verify VAI branding on live mockup."""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
OUT_DIR = Path(__file__).resolve().parent


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector("#app-headline", timeout=20000)

        headline = page.locator("#app-headline").inner_text().strip()
        page_title = page.title()
        logo_title = page.locator("#app-logo").get_attribute("title")
        logo_text = page.locator("#app-logo text").text_content().strip()
        footer = page.locator(".footer-note").inner_text().strip()
        pdf_removed = page.locator("#btn-export-pdf").count() == 0
        print_btn = page.locator("#btn-print-slip").inner_text().strip()

        page.locator(".game-header").screenshot(path=str(OUT_DIR / "test-vai-branding-header.png"))

        print("Headline:", headline)
        print("Page title:", page_title)
        print("Logo tooltip:", logo_title)
        print("Logo badge text:", logo_text)
        print("Footer note:", footer)
        print("PDF button removed:", pdf_removed)
        print("Print button:", print_btn)
        print("Screenshot:", OUT_DIR / "test-vai-branding-header.png")

        ok = (
            headline == "VAI V85"
            and page_title == "VAI V85 — Local UI v1.1.3"
            and logo_title == "VAI V85"
            and logo_text == "VAI"
            and "TRAVHÄST + VAI" in footer.upper()
            and pdf_removed
            and print_btn == "Skriv ut spelkvitto"
            and "V85 Proposal" not in page.content()
        )
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())