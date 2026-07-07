"""Open mockup and test slip print flow."""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
OUT_DIR = Path(__file__).resolve().parent
BUDGET = 432
SEED = "42"


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        context.add_init_script(
            "window.print = function() { window.__printStubbed = true; };"
        )
        page = context.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector(".horse:not(.scratched)", timeout=20000)

        page.fill("#stake-input", str(BUDGET))
        page.fill("#seed-input", SEED)
        page.click("#btn-generate")
        page.wait_for_selector(".slip-row", timeout=20000)

        page.click("#btn-print-slip")
        print_called = page.evaluate("window.__printStubbed === true")
        print_mode = page.evaluate(
            "document.body.classList.contains('print-slip-only')"
        )
        page.locator(".slip-preview").screenshot(path=str(OUT_DIR / "test-slip-before-export.png"))

        print("=== Print test ===")
        print("print() called:", print_called)
        print("body.print-slip-only:", print_mode)
        print("Screenshot:", OUT_DIR / "test-slip-before-export.png")

        ok = print_called and print_mode
        print()
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())