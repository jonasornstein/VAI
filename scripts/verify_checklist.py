"""Verify Innan spel checklist wires to generated system."""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
OUT_DIR = Path(__file__).resolve().parent


def checklist_state(page) -> dict[str, str]:
    return page.evaluate(
        """() => {
          function state(id) {
            const el = document.getElementById(id);
            if (!el) return 'missing';
            if (el.classList.contains('done')) return 'done';
            if (el.classList.contains('warn')) return 'warn';
            return 'pending';
          }
          return {
            legs: state('check-legs'),
            cost: state('check-cost'),
            scratches: state('check-scratches'),
            reserves: state('check-reserves'),
            scratchHint: document.getElementById('check-scratches')?.title || '',
            reservesHint: document.getElementById('check-reserves')?.title || '',
            labels: Array.from(document.querySelectorAll('#operator-checklist li')).map(
              (el) => el.textContent.trim()
            )
          };
        }"""
    )


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector(".horse:not(.scratched)", timeout=20000)

        before = checklist_state(page)
        page.locator("#operator-checklist").screenshot(
            path=str(OUT_DIR / "test-checklist-before.png")
        )

        page.fill("#stake-input", "432")
        page.fill("#seed-input", "42")
        page.click("#btn-generate")
        page.wait_for_selector(".slip-row", timeout=20000)
        after = checklist_state(page)
        page.locator("#operator-checklist").screenshot(
            path=str(OUT_DIR / "test-checklist-after.png")
        )

        print("=== Before generate ===")
        print(before)
        print("Screenshot:", OUT_DIR / "test-checklist-before.png")
        print()
        print("=== After generate (budget 432, seed 42) ===")
        print(after)
        print("Screenshot:", OUT_DIR / "test-checklist-after.png")

        ok = (
            before["legs"] == "pending"
            and before["cost"] == "pending"
            and before["scratches"] == "pending"
            and before["reserves"] == "pending"
            and after["legs"] == "done"
            and after["cost"] == "done"
            and after["scratches"] == "done"
            and after["reserves"] == "done"
            and len(after["labels"]) == 4
        )
        print()
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())