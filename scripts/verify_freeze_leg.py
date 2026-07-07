"""Verify freeze leg with seed 42 and budget 500."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
BUDGET = 500
SEED = "42"
# Leg 2 spik + leg 4 gardering; both frozen — random fills other legs only
MARKS = {2: [5], 4: [3, 7]}
FROZEN = [2, 4]


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector(".horse:not(.scratched)", timeout=20000)

        page.click("#btn-deselect-all")
        page.fill("#stake-input", str(BUDGET))
        page.fill("#seed-input", SEED)

        for leg, horses in MARKS.items():
            for horse in horses:
                page.locator(f'.horse[data-leg="{leg}"]:text-is("{horse}")').click()
            page.locator(f'.leg-freeze-btn[data-leg="{leg}"]').click()

        for leg in FROZEN:
            frozen = page.locator(f'.leg-card[data-leg="{leg}"]').evaluate(
                "el => el.classList.contains('leg-frozen')"
            )
            btn_pressed = page.locator(f'.leg-freeze-btn[data-leg="{leg}"]').get_attribute(
                "aria-pressed"
            )
            print(f"Leg {leg} frozen UI: class={frozen} aria-pressed={btn_pressed}")

        page.click("#btn-generate")
        page.wait_for_function(
            """() => {
              const cost = document.getElementById('cost-big').textContent || '';
              return cost.includes('SEK') && !cost.startsWith('—');
            }""",
            timeout=20000,
        )

        cost_text = page.locator("#cost-big").inner_text().strip()
        rows = page.locator("#stat-rows-count").inner_text().strip()

        def slip_horses(leg: int) -> set[int]:
            text = page.locator(".slip-row-horses").nth(leg - 1).inner_text()
            return {int(part) for part in text.split() if part}

        leg2 = slip_horses(2)
        leg4 = slip_horses(4)
        leg2_rand = page.locator('.horse.random-selected[data-leg="2"]').count()
        leg4_rand = page.locator('.horse.random-selected[data-leg="4"]').count()
        leg2_op = page.locator('.horse.pool-selected[data-leg="2"]').count()
        leg4_op = page.locator('.horse.pool-selected[data-leg="4"]').count()

        print("Cost:", cost_text)
        print("Rows:", rows)
        print("Leg 2 slip:", sorted(leg2), "random frames:", leg2_rand, "operator:", leg2_op)
        print("Leg 4 slip:", sorted(leg4), "random frames:", leg4_rand, "operator:", leg4_op)

        ok = (
            "500,00" in cost_text
            and rows == "1 000"
            and leg2 == {5}
            and leg4 == {3, 7}
            and leg2_rand == 0
            and leg4_rand == 0
            and leg2_op == 1
            and leg4_op == 2
        )
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())