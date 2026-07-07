"""Verify live betslip matches inbox/betslip.png structure."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
# Match reference PNG footer: 864 rader x 0,50 kr = 432,00 kr
BUDGET = 432
SEED = "42"


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 420, "height": 900})
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector(".horse:not(.scratched)", timeout=20000)

        page.fill("#stake-input", str(BUDGET))
        page.fill("#seed-input", SEED)
        page.click("#btn-generate")
        page.wait_for_selector(".slip-row", timeout=20000)

        title_visible = page.locator("#slip-title").is_visible()
        title_display = page.locator("#slip-title").evaluate(
            "el => getComputedStyle(el).display"
        )
        footer = page.locator("#slip-footer").inner_text().strip()
        rows = page.locator(".slip-row").count()
        uses_dots = "·" in page.locator(".slip-table").inner_text()
        leg_bg = page.locator(".slip-row-leg").first.evaluate(
            "el => getComputedStyle(el).backgroundColor"
        )
        horse_bg = page.locator(".slip-row-horses").first.evaluate(
            "el => getComputedStyle(el).backgroundColor"
        )
        footer_bg = page.locator("#slip-footer").evaluate(
            "el => getComputedStyle(el).backgroundColor"
        )

        page.locator(".slip-preview").screenshot(path="scripts/compare-betslip-live.png")

        print("Title visible:", title_visible, "display:", title_display)
        print("Rows:", rows)
        print("Footer:", footer)
        print("Leg bg:", leg_bg)
        print("Horse bg:", horse_bg)
        print("Footer bg:", footer_bg)
        print("Dot separator:", uses_dots)

        ok = (
            not title_visible
            and title_display == "none"
            and rows == 8
            and footer == "864 rader x 0,50 kr = 432,00 kr"
            and not uses_dots
            and leg_bg == "rgb(0, 107, 179)"
            and horse_bg == "rgb(255, 255, 255)"
            and footer_bg == "rgb(242, 239, 232)"
        )
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())