"""Verify rationale text uses hästar instead of tillägg after generate."""

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
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_selector(".horse:not(.scratched)", timeout=30000)

        before = page.locator("#rationale-text").inner_text().strip()
        page.fill("#stake-input", "432")
        page.fill("#seed-input", "42")

        with page.expect_response(
            lambda r: "/api/v1/generate/random" in r.url and r.request.method == "POST",
            timeout=30000,
        ):
            page.click("#btn-generate")

        page.wait_for_selector(".slip-row", timeout=30000)
        after = page.locator("#rationale-text").inner_text().strip()
        page.locator(".rationale").screenshot(path=str(OUT_DIR / "test-rationale-text.png"))

        print("Before generate:")
        print(before)
        print()
        print("After generate:")
        print(after)
        print("Screenshot:", OUT_DIR / "test-rationale-text.png")

        ok = (
            before == "Slumpmässigt urval ur operatörens kandidatpool per avdelning."
            and after.startswith(before)
            and "hästar till budget" in after
            and "tillägg till budget" not in after
            and "Markerade hästar låses" in after
            and "Seed 42" in after
        )
        print()
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())