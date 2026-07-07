"""Verify Genererat spel cost equals SYSTEMKOSTNAD budget."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
BUDGET = 500


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector(".horse:not(.scratched)", timeout=20000)

        cases = [
            ("empty picks", lambda: None),
            ("partial picks", lambda: (
                page.locator('.horse[data-leg="1"]:text-is("3")').click(),
                page.locator('.horse[data-leg="1"]:text-is("7")').click(),
                page.locator('.horse[data-leg="3"]:text-is("5")').click(),
                page.locator('.horse[data-leg="6"]:text-is("2")').click(),
                page.locator('.horse[data-leg="6"]:text-is("4")').click(),
            )),
        ]

        all_ok = True
        for label, setup in cases:
            page.click("#btn-deselect-all")
            page.fill("#stake-input", str(BUDGET))
            page.fill("#seed-input", "42")
            setup()
            page.click("#btn-generate")
            page.wait_for_function(
                """() => {
                  const cost = document.getElementById('cost-big').textContent || '';
                  return cost.includes('SEK') && !cost.startsWith('—');
                }""",
                timeout=20000,
            )
            cost_text = page.locator("#cost-big").inner_text().strip()
            rows = page.locator("#stat-rows-count").inner_text().strip()
            expected_cost = f"{BUDGET:.2f}".replace(".", ",") + " SEK"
            expected_rows = f"{int(BUDGET / 0.5):,}".replace(",", " ")
            ok = expected_cost.split()[0] in cost_text and rows == expected_rows
            print(f"{label}: cost={cost_text} rows={rows} PASS={ok}")
            all_ok = all_ok and ok

        print("VERIFY PASS:", all_ok)
        browser.close()
        return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())