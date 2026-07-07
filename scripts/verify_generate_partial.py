"""Verify Generera system with a few horses marked on some legs."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"

# leg -> horse numbers to mark before generate
MARKS = {
    1: [3, 7],
    3: [5],
    6: [2, 4],
}


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_function(
            '() => document.querySelectorAll(".leg-card .horse:not(.scratched)").length > 0',
            timeout=20000,
        )

        for leg, horses in MARKS.items():
            for horse in horses:
                page.locator(
                    f'.leg-card .horse[data-leg="{leg}"]:text-is("{horse}")'
                ).click()

        marked = page.eval_on_selector_all(
            ".horse.pool-selected",
            "els => els.map(el => ({leg: el.getAttribute('data-leg'), horse: el.textContent}))",
        )
        print("Marked before generate:", marked)

        page.fill("#seed-input", "42")
        page.click("#btn-generate")
        page.wait_for_function(
            """() => {
              const cost = document.getElementById('cost-big').textContent || '';
              return cost.includes('SEK') && !cost.startsWith('—');
            }""",
            timeout=20000,
        )

        slip = page.eval_on_selector_all(
            ".slip-row-horses",
            "els => els.map(el => el.textContent.trim())",
        )
        cost_text = page.locator("#cost-big").inner_text().strip()
        rows = page.locator("#stat-rows-count").inner_text()
        breakdown = page.locator("#stat-breakdown").inner_text()
        grow_steps = page.locator("#stat-shrink").inner_text()
        rationale = page.locator("#rationale-text").inner_text()

        print("Cost:", cost_text)
        print("Rows:", rows)
        print("Breakdown:", breakdown)
        print("Tilläggssteg:", grow_steps)
        print("Slip:", slip)
        print("Rationale:", rationale)

        def slip_horses(leg_index: int) -> set[int]:
            text = slip[leg_index]
            return {int(part) for part in text.split() if part}

        checks = []
        for leg, horses in MARKS.items():
            present = set(horses) <= slip_horses(leg - 1)
            checks.append((leg, horses, present))
            print(f"Leg {leg} locked picks {horses} present: {present}")

        ok = (
            len(marked) == sum(len(v) for v in MARKS.values())
            and len(slip) == 8
            and all(present for _, _, present in checks)
            and "500,00" in cost_text
        )
        operator_count = page.locator(".horse.pool-selected").count()
        random_count = page.locator(".horse.random-selected").count()
        print("Operator-colored horses:", operator_count)
        print("Random-framed horses:", random_count)

        ok = ok and operator_count == 5 and random_count > 0
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())