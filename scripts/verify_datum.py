"""Headless check: mockup DATUM shows expected V85 date."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
EXPECTED_DATUM = "2026-07-11"


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_function(
            """() => {
              const el = document.getElementById('datum');
              return el && el.options && el.options.length > 0 && el.value;
            }""",
            timeout=20000,
        )

        selected = page.locator("#datum").input_value()
        options = page.eval_on_selector(
            "#datum",
            "el => Array.from(el.options).map(o => o.value)",
        )
        bana_text = page.eval_on_selector(
            "#bana",
            "el => el.options[el.selectedIndex] ? el.options[el.selectedIndex].textContent : ''",
        )
        api_status = page.locator("#api-status").inner_text()
        source = page.locator("#source-badge").inner_text()

        page.wait_for_function(
            '() => document.querySelectorAll(".leg-card").length === 8',
            timeout=20000,
        )
        legs = page.locator(".leg-card").count()

        print(f"DATUM selected: {selected}")
        print(f"DATUM options: {options}")
        print(f"BANA text: {bana_text}")
        print(f"API status: {api_status}")
        print(f"Source badge: {source}")
        print(f"Leg cards rendered: {legs}")

        ok = selected == EXPECTED_DATUM
        print(f"VERIFY PASS: {ok}")
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())