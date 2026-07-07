"""Verify deselect controls and orange random frames after generate."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
MARKS = {1: [3, 7], 3: [5], 6: [2, 4]}


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector(".horse:not(.scratched)", timeout=20000)

        print("=== Deselect test ===")
        for leg, horses in MARKS.items():
            for horse in horses:
                page.locator(f'.horse[data-leg="{leg}"]:text-is("{horse}")').click()
        before_leg_clear = page.locator(".horse.pool-selected").count()
        print("Marked horses:", before_leg_clear)
        page.locator('.leg-clear-btn[data-leg="1"]').click()
        after_leg_clear = page.locator(".horse.pool-selected").count()
        print("After clear leg 1:", after_leg_clear)
        page.click("#btn-deselect-all")
        after_all_clear = page.locator(".horse.pool-selected").count()
        print("After clear all:", after_all_clear)

        deselect_ok = before_leg_clear == 5 and after_leg_clear == 3 and after_all_clear == 0
        print("Deselect PASS:", deselect_ok)

        print("=== Generate + orange frames ===")
        for leg, horses in MARKS.items():
            for horse in horses:
                page.locator(f'.horse[data-leg="{leg}"]:text-is("{horse}")').click()
        page.fill("#seed-input", "42")
        page.click("#btn-generate")
        page.wait_for_function(
            """() => {
              const cost = document.getElementById('cost-big').textContent || '';
              return cost.includes('SEK') && !cost.startsWith('—');
            }""",
            timeout=20000,
        )

        operator_count = page.locator(".horse.pool-selected").count()
        random_count = page.locator(".horse.random-selected").count()
        print("Operator-colored:", operator_count)
        print("Orange-framed:", random_count)

        leg1_op = page.locator('.horse.pool-selected[data-leg="1"]').count()
        leg1_rand = page.locator('.horse.random-selected[data-leg="1"]').count()
        print("Leg 1 operator:", leg1_op, "random:", leg1_rand)

        frames_ok = operator_count == 5 and random_count > 0 and leg1_op == 2 and leg1_rand > 0
        print("Orange frames PASS:", frames_ok)

        page.click("#btn-deselect-all")
        cleared = (
            page.locator(".horse.pool-selected").count() == 0
            and page.locator(".horse.random-selected").count() == 0
        )
        print("Clear after generate PASS:", cleared)

        ok = deselect_ok and frames_ok and cleared
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())