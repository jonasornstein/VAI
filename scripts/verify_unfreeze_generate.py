"""Verify unfreeze leg then Generera system succeeds."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector(".horse:not(.scratched)", timeout=20000)

        dialog_messages: list[str] = []
        page.on("dialog", lambda d: (dialog_messages.append(d.message), d.accept()))

        page.click("#btn-deselect-all")
        page.fill("#stake-input", "500")
        page.fill("#seed-input", "42")

        # Freeze leg 3 with no marks — would block generate
        freeze_btn = page.locator('.leg-freeze-btn[data-leg="3"]')
        freeze_btn.click()
        frozen_before = page.locator('.leg-card[data-leg="3"]').evaluate(
            "el => el.classList.contains('leg-frozen')"
        )
        page.click("#btn-generate")
        page.wait_for_timeout(300)

        blocked = (
            len(dialog_messages) == 1
            and dialog_messages[0] == "Fryst avdelning 3 måste ha minst en markerad häst"
        )
        print("Blocked when frozen empty:", blocked)

        # Unfreeze leg 3
        freeze_btn.click()
        frozen_after = page.locator('.leg-card[data-leg="3"]').evaluate(
            "el => el.classList.contains('leg-frozen')"
        )
        btn_text = freeze_btn.inner_text()
        btn_pressed = freeze_btn.get_attribute("aria-pressed")
        print("After unfreeze: frozen=", frozen_after, "btn=", btn_text, "pressed=", btn_pressed)

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
        slip_legs = page.locator(".slip-row").count()
        leg3_slip = page.locator(".slip-row-horses").nth(2).inner_text()
        slip_footer = page.locator("#slip-footer").inner_text()
        leg3_random = page.locator('.horse.random-selected[data-leg="3"]').count()

        print("Cost:", cost_text)
        print("Rows:", rows)
        print("Slip legs:", slip_legs)
        print("Leg 3 slip:", leg3_slip)
        print("Slip footer:", slip_footer)
        print("Leg 3 random frames:", leg3_random)

        ok = (
            blocked
            and not frozen_after
            and btn_pressed == "false"
            and "500,00" in cost_text
            and rows == "1 000"
            and slip_legs == 8
            and leg3_random > 0
            and "1 000 rader" in slip_footer
            and "500,00 kr" in slip_footer
            and len(dialog_messages) == 1
        )
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())