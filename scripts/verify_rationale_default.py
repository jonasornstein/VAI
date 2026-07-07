"""Verify default rationale text on live mockup."""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
DEFAULT = "Slumpmässigt urval ur operatörens kandidatpool per avdelning."
OUT_DIR = Path(__file__).resolve().parent


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector("#rationale-text", timeout=20000)

        on_load = page.locator("#rationale-text").inner_text().strip()
        page.locator(".rationale").screenshot(path=str(OUT_DIR / "test-rationale-default.png"))

        page.select_option("#datum", index=0)
        page.wait_for_timeout(500)
        after_datum = page.locator("#rationale-text").inner_text().strip()

        print("On load:", on_load)
        print("After datum change:", after_datum)
        print("Screenshot:", OUT_DIR / "test-rationale-default.png")

        ok = (
            on_load == DEFAULT
            and after_datum == DEFAULT
            and "python -m atg serve" not in on_load
            and "Expert och Kvantitativ" not in on_load
        )
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())