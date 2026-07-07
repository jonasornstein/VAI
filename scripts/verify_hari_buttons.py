"""Verify Hari mode tab and matching action button sizes."""

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
        page.wait_for_selector("#btn-generate", timeout=20000)

        hari_tab = page.locator('[data-mode="random"]').inner_text().strip()
        hari_active = page.locator('[data-mode="random"]').evaluate(
            "el => el.classList.contains('active')"
        )
        generate_text = page.locator("#btn-generate").inner_text().strip()
        atg_text = page.locator("#btn-open-atg").inner_text().strip()
        gen_box = page.locator("#btn-generate").bounding_box()
        atg_box = page.locator("#btn-open-atg").bounding_box()

        page.locator(".mode-tabs").screenshot(path=str(OUT_DIR / "test-hari-tab.png"))
        page.locator("#btn-generate").screenshot(path=str(OUT_DIR / "test-btn-generate.png"))
        page.locator("#btn-open-atg").screenshot(path=str(OUT_DIR / "test-btn-atg.png"))

        print("Hari tab text:", hari_tab)
        print("Hari tab active:", hari_active)
        print("Generate button:", generate_text)
        print("ATG button:", atg_text)
        print("Generate size:", gen_box)
        print("ATG size:", atg_box)

        same_size = (
            gen_box
            and atg_box
            and gen_box["width"] == atg_box["width"]
            and gen_box["height"] == atg_box["height"]
        )

        ok = (
            hari_tab == "Hari"
            and hari_active
            and generate_text == "GENERERA SYSTEM"
            and atg_text == "ÖPPNA ATG/V85"
            and same_size
        )
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())