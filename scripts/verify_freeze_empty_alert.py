"""Verify alert when frozen leg has no marked horses."""

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

        def on_dialog(dialog) -> None:
            dialog_messages.append(dialog.message)
            dialog.accept()

        page.on("dialog", on_dialog)

        page.click("#btn-deselect-all")
        page.fill("#stake-input", "500")
        page.fill("#seed-input", "42")
        page.locator('.leg-freeze-btn[data-leg="3"]').click()
        page.click("#btn-generate")

        page.wait_for_timeout(500)

        cost_text = page.locator("#cost-big").inner_text().strip()
        slip_legs = page.locator(".slip-row").count()
        expected = "Fryst avdelning 3 måste ha minst en markerad häst"

        print("Dialog shown:", dialog_messages)
        print("Expected alert:", expected)
        print("Cost display:", cost_text)
        print("Slip legs:", slip_legs)

        ok = (
            len(dialog_messages) == 1
            and dialog_messages[0] == expected
            and cost_text.startswith("—")
            and slip_legs == 0
        )
        print("VERIFY PASS:", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())