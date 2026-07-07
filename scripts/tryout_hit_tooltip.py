"""UI try-out — Träffsannolikhet help tooltip."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"


def main() -> int:
    checks: list[tuple[str, bool]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_function(
            '() => document.getElementById("bana").options.length > 0',
            timeout=30000,
        )

        btn = page.locator("#hit-summary-help-btn")
        checks.append(("help_btn_visible", btn.is_visible()))
        aria = btn.get_attribute("aria-label") or ""
        checks.append(("help_btn_aria", "träffsannolikhet" in aria.lower()))
        title = btn.get_attribute("title") or ""
        checks.append(("help_title_atg", "ATG" in title and "V85-andelar" in title))
        checks.append(("help_title_tiers", "P(8)" in title and "P(≥7)" in title))
        checks.append(("help_title_disclaimer", "Förenklad modell" in title))

        page.wait_for_selector(".leg-card .horse:not(.scratched)", timeout=30000)
        page.fill("#stake-input", "500")
        page.fill("#seed-input", "42")
        with page.expect_response(
            lambda r: "/api/v1/generate/random" in r.url and r.status == 200,
            timeout=45000,
        ):
            page.click("#btn-generate")
        page.wait_for_selector(".slip-row", timeout=15000)
        page.wait_for_function(
            '() => { const b = document.getElementById("hit-bars"); return b && !b.hidden; }',
            timeout=30000,
        )
        checks.append(("hit_bars_visible", page.locator("#hit-bars").is_visible()))
        checks.append(
            (
                "hit_bars_describedby",
                page.locator("#hit-bars").get_attribute("aria-describedby") == "hit-summary-help-text",
            )
        )

        page.screenshot(path="scripts/tryout-hit-tooltip.png")
        browser.close()

    print("=== Träffsannolikhet tooltip try-out ===")
    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}: {name}")
    print("Screenshot: scripts/tryout-hit-tooltip.png")
    all_ok = all(ok for _, ok in checks)
    print("ALL PASS:", all_ok)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())