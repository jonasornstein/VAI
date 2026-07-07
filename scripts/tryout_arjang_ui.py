"""UI try-out — Årjäng V85 2026-07-11."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
DATE = "2026-07-11"
TRACK = "Årjäng"
SEED = "42"
BUDGET = "500"

# Approved outbox proposal legs (seed 42)
EXPECTED_SLIP = {
    1: ["1"],
    2: ["5", "12"],
    3: ["1", "2", "3", "4", "5", "6", "7", "9", "11", "12"],
    4: ["4"],
    5: ["1", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
    6: ["8"],
    7: ["10"],
    8: ["1", "3", "5", "7", "13"],
}


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

        datum_val = page.input_value("#datum")
        checks.append(("datum", datum_val == DATE))

        bana_text = page.locator("#bana option:checked").inner_text().strip()
        checks.append(("bana", bana_text == TRACK))

        page.select_option("#datum", DATE)
        page.wait_for_timeout(500)
        page.select_option("#bana", label=TRACK)
        page.wait_for_selector(".leg-card .horse:not(.scratched)", timeout=25000)

        source = page.locator("#source-badge").inner_text().strip()
        checks.append(("source_atg", source == "ATG"))

        page.fill("#stake-input", BUDGET)
        page.fill("#seed-input", SEED)
        page.click("#btn-generate")
        page.wait_for_selector(".slip-row", timeout=30000)

        cost = page.locator("#cost-big").inner_text()
        checks.append(("cost_500", "500,00" in cost and "= budget" in cost))

        footer = page.locator("#slip-footer").inner_text()
        checks.append(("footer", "1 000 rader" in footer and "500,00" in footer))

        for leg, expected in EXPECTED_SLIP.items():
            horses_text = page.locator(".slip-row").nth(leg - 1).locator(".slip-row-horses").inner_text()
            actual = horses_text.split()
            checks.append((f"leg{leg}_slip", actual == [str(h) for h in expected]))

        hit_ok = page.locator("#hit-bars").is_visible() and "≥5 rätt" in page.locator("#hit-bars").inner_text()
        checks.append(("hit_bars", hit_ok))

        rationale = page.locator("#rationale-text").inner_text()
        checks.append(("rationale_seed", "Seed 42" in rationale))

        page.screenshot(path="scripts/tryout-arjang-ui.png", full_page=True)
        browser.close()

    print(f"UI try-out: Årjäng {DATE}")
    print("Screenshot: scripts/tryout-arjang-ui.png")
    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}: {name}")
    all_ok = all(v for _, v in checks)
    print("ALL PASS:", all_ok)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())