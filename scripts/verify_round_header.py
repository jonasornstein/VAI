"""Verify the VAI V85 header shows course, start time, OMSÄTTNING, and Uppdatera."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8766/"
OUT_DIR = Path("/tmp")
# Thousands separators and the space before "kr" are non-breaking so the amount stays on one line.
META_RE = re.compile(
    r"^.+ · \d{2}:\d{2} · OMSÄTTNING[ \u00a0][\d \u00a0]+(?:,\d{2})?[ \u00a0]kr$"
)


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector("#app-headline", timeout=20000)
        page.wait_for_function(
            """() => {
              var t = document.getElementById('app-round-meta').textContent || '';
              return t.indexOf('OMSÄTTNING') !== -1 && t.indexOf('kr') !== -1;
            }""",
            timeout=30000,
        )

        headline = page.locator("#app-headline").inner_text().strip()
        meta = page.locator("#app-round-meta").inner_text().strip()
        refresh = page.locator("#btn-refresh-round")
        refresh_visible_hari = refresh.is_visible()
        refresh_title = refresh.get_attribute("title") or ""

        horse = page.locator("#legs-grid .horse:not(.scratched)").first
        horse.click()
        selected = page.locator("#legs-grid .horse.pool-selected").first
        leg = selected.get_attribute("data-leg")
        num = selected.get_attribute("data-horse")
        refresh.click()
        page.wait_for_function(
            "() => !document.getElementById('btn-refresh-round').disabled",
            timeout=30000,
        )
        still = page.locator(
            f'#legs-grid .horse.pool-selected[data-leg="{leg}"][data-horse="{num}"]'
        )
        mark_kept = still.count() == 1
        meta_after = page.locator("#app-round-meta").inner_text().strip()

        page.locator('.mode-tabs [data-mode="expert"]').click()
        refresh_visible_expert = refresh.is_visible()
        page.locator('.mode-tabs [data-mode="fundamental"]').click()
        page.wait_for_selector("#btn-fundamental-refresh", timeout=10000)
        refresh_visible_fundamental = refresh.is_visible()
        fundamental_still = page.locator("#btn-fundamental-refresh").is_visible()

        page.screenshot(path=str(OUT_DIR / "vai-round-header-desktop.png"))
        header = page.locator(".game-header")
        header.screenshot(path=str(OUT_DIR / "vai-round-header-desktop-bar.png"))

        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(300)
        meta_box = page.locator("#app-round-meta").bounding_box()
        btn_box = refresh.bounding_box()
        page.screenshot(path=str(OUT_DIR / "vai-round-header-mobile.png"))
        header.screenshot(path=str(OUT_DIR / "vai-round-header-mobile-bar.png"))

        print("Headline:", headline)
        print("Meta:", meta)
        print("Meta after refresh:", meta_after)
        print("Refresh title:", refresh_title)
        print("Visible Hari/Expert/Fundamental:", refresh_visible_hari, refresh_visible_expert, refresh_visible_fundamental)
        print("Mark kept:", mark_kept, "leg", leg, "horse", num)
        print("Fundamental button:", fundamental_still)
        print("Mobile meta box:", meta_box)
        print("Mobile button box:", btn_box)

        fits = (
            meta_box is not None
            and btn_box is not None
            and meta_box["x"] >= -1
            and meta_box["x"] + meta_box["width"] <= 391
            and btn_box["x"] >= -1
            and btn_box["x"] + btn_box["width"] <= 391
        )
        ok = (
            headline == "VAI V85"
            and META_RE.match(meta) is not None
            and META_RE.match(meta_after) is not None
            and refresh_visible_hari
            and refresh_visible_expert
            and refresh_visible_fundamental
            and "odds" in refresh_title
            and mark_kept
            and fundamental_still
            and fits
        )
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
