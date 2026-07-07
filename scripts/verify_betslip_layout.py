"""Verify new Genererat spel betslip layout after generate."""

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

        page.fill("#stake-input", "500")
        page.fill("#seed-input", "42")
        page.click("#btn-generate")
        page.wait_for_selector(".slip-row", timeout=20000)

        rows = page.locator(".slip-row").count()
        leg_cols = page.locator(".slip-row-leg").count()
        horse_cols = page.locator(".slip-row-horses").count()
        footer = page.locator("#slip-footer").inner_text().strip()
        leg1_num = page.locator(".slip-row-leg").first.inner_text().strip()
        leg1_horses = page.locator(".slip-row-horses").first.inner_text().strip()
        leg1_bg = page.locator(".slip-row-leg").first.evaluate(
            "el => getComputedStyle(el).backgroundColor"
        )
        uses_dots = "·" in page.locator(".slip-table").inner_text()
        old_grid = page.locator(".slip-leg").count()

        print("Slip rows:", rows)
        print("Leg columns:", leg_cols)
        print("Horse columns:", horse_cols)
        print("Leg 1 label:", leg1_num)
        print("Leg 1 horses:", leg1_horses)
        print("Leg column bg:", leg1_bg)
        print("Footer:", footer)
        print("Uses dot separator:", uses_dots)
        print("Old slip-leg elements:", old_grid)

        multi_horse_rows = page.eval_on_selector_all(
            ".slip-row-horses",
            "els => els.map(el => el.textContent.trim()).filter(t => t.includes(' '))",
        )

        ok = (
            rows == 8
            and leg_cols == 8
            and horse_cols == 8
            and leg1_num == "1"
            and len(multi_horse_rows) > 0
            and not uses_dots
            and old_grid == 0
            and "rader x 0,50 kr" in footer
            and "500,00 kr" in footer
        )
        print("Multi-horse rows sample:", multi_horse_rows[:3])
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())