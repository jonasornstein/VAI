"""Verify per-leg and all-leg deselect controls."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector(".horse:not(.scratched)", timeout=20000)

        page.locator('.horse[data-leg="1"]:text-is("3")').click()
        page.locator('.horse[data-leg="1"]:text-is("7")').click()
        page.locator('.horse[data-leg="3"]:text-is("5")').click()
        assert page.locator(".horse.pool-selected").count() == 3

        page.locator('.leg-clear-btn[data-leg="1"]').click()
        assert page.locator(".horse.pool-selected").count() == 1

        page.click("#btn-deselect-all")
        assert page.locator(".horse.pool-selected").count() == 0
        assert page.locator(".horse.random-selected").count() == 0

        print("Deselect leg/all: PASS")
        browser.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())