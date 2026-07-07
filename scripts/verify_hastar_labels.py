"""Verify hästar UX labels on live mockup."""

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
        page.wait_for_selector(".selection-legend", timeout=20000)

        legend = page.locator(".selection-legend").inner_text()
        stat_label = page.locator("#stat-shrink").evaluate(
            "el => el.parentElement.querySelector('span').textContent.trim()"
        )
        old_legend = "Slumpens tillägg" in legend
        old_stat = page.locator("text=Tilläggssteg").count() > 0

        page.locator(".selection-legend").screenshot(
            path=str(OUT_DIR / "test-hastar-legend.png")
        )
        page.locator("#stat-rows").screenshot(path=str(OUT_DIR / "test-hastar-stat.png"))

        print("Legend text:")
        print(legend)
        print("Stat label:", stat_label)
        print("Old legend removed:", not old_legend)
        print("Old stat label removed:", not old_stat)
        print("Screenshot legend:", OUT_DIR / "test-hastar-legend.png")
        print("Screenshot stat:", OUT_DIR / "test-hastar-stat.png")

        ok = (
            "Slumpens hästar" in legend
            and "Slumpens tillägg" not in legend
            and stat_label == "Antal hästar tillagda"
            and not old_stat
        )
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())