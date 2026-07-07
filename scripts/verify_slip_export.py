"""Verify slip print and ATG export controls."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector(".horse:not(.scratched)", timeout=20000)

        headline = page.locator("#app-headline").inner_text().strip()
        logo_text = page.locator(".game-header__logo text").text_content().strip()
        pdf_gone = page.locator("#btn-export-pdf").count() == 0
        print_disabled = page.locator("#btn-print-slip").is_disabled()

        page.fill("#stake-input", "432")
        page.fill("#seed-input", "42")
        page.click("#btn-generate")
        page.wait_for_selector(".slip-row", timeout=20000)

        print_enabled = not page.locator("#btn-print-slip").is_disabled()
        footer = page.locator("#slip-footer").inner_text().strip()

        with page.expect_popup() as popup_info:
            page.click("#btn-open-atg")
        popup = popup_info.value
        popup.wait_for_load_state("domcontentloaded", timeout=15000)
        atg_url = popup.url
        popup.close()

        print("Headline:", headline)
        print("Logo text:", logo_text)
        print("PDF button removed:", pdf_gone)
        print("Print disabled before generate:", print_disabled)
        print("Print enabled after generate:", print_enabled)
        print("Slip footer:", footer)
        print("ATG URL:", atg_url)

        ok = (
            headline == "VAI V85"
            and logo_text == "VAI"
            and pdf_gone
            and print_disabled
            and print_enabled
            and footer == "864 rader x 0,50 kr = 432,00 kr"
            and atg_url.startswith("https://www.atg.se/v85")
        )
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())