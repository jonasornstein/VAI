"""Verify seed help text in mockup sidebar."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
EXPECTED_PHRASES = [
    "Styr slumpens tillägg",
    "Påverkar inte vilka hästar du klickar",
    "Lämna tom",
    "Generera system",
    "Samma seed",
    "Genererat spel",
    "42",
]


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector("#seed-help", timeout=20000)

        heading = page.locator("h3", has_text="Seed (valfritt)").inner_text()
        help_text = page.locator("#seed-help").inner_text().strip()
        aria = page.locator("#seed-input").get_attribute("aria-describedby")
        placeholder = page.locator("#seed-input").get_attribute("placeholder")

        print("Heading:", heading)
        print("aria-describedby:", aria)
        print("placeholder:", placeholder)
        print("Help text:")
        print(help_text)
        print("---")

        checks = {phrase: phrase in help_text for phrase in EXPECTED_PHRASES}
        for phrase, ok in checks.items():
            print(f'  contains "{phrase}": {ok}')

        ok = aria == "seed-help" and all(checks.values())
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())