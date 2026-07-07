"""Verify Generera system works with no horses marked."""

from __future__ import annotations

import json
import sys
import urllib.request

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"


def _get_schedule_game_id() -> str:
    with urllib.request.urlopen(f"{URL}api/v1/schedule/v85", timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["rounds"][0]["game_id"]


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_function(
            """() => {
              const el = document.getElementById('datum');
              return el && el.options && el.options.length > 0 && el.value;
            }""",
            timeout=20000,
        )
        page.wait_for_function(
            '() => document.querySelectorAll(".leg-card .horse:not(.scratched)").length > 0',
            timeout=20000,
        )

        selected_horses = page.locator(".horse.pool-selected").count()
        print("Marked horses before generate:", selected_horses)

        page.click("#btn-generate")
        page.wait_for_function(
            """() => {
              const cost = document.getElementById('cost-big').textContent || '';
              return cost.includes('SEK') && !cost.startsWith('—');
            }""",
            timeout=20000,
        )

        cost_text = page.locator("#cost-big").inner_text()
        rows = page.locator("#stat-rows-count").inner_text()
        breakdown = page.locator("#stat-breakdown").inner_text()
        grow_steps = page.locator("#stat-shrink").inner_text()
        slip_legs = page.locator(".slip-row").count()
        slip_footer = page.locator("#slip-footer").inner_text()
        rationale = page.locator("#rationale-text").inner_text()
        btn_disabled = page.locator("#btn-generate").is_disabled()

        print("Cost display:", cost_text.strip())
        print("Rows:", rows)
        print("Breakdown:", breakdown)
        print("Tilläggssteg:", grow_steps)
        print("Slip legs:", slip_legs)
        print("Slip footer:", slip_footer)
        print("Rationale:", rationale)
        print("Generate button disabled:", btn_disabled)

        cost_value = page.eval_on_selector("#cost-big", "el => el.textContent")
        ok = (
            selected_horses == 0
            and slip_legs == 8
            and "500,00" in cost_value
            and "1 000 rader" in slip_footer
            and not btn_disabled
        )
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())