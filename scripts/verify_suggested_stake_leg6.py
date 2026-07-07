"""Verify suggested stake when all horses in leg 6 cannot hit exact 20000 SEK budget."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
BUDGET = 20000


def test_api(card_id: str, leg6_horses: list[int]) -> bool:
    pools = {str(i): [] for i in range(1, 9)}
    pools["6"] = leg6_horses
    payload = {"race_card_id": card_id, "pools": pools, "budget": BUDGET, "seed": 42}
    req = urllib.request.Request(
        f"{URL}api/v1/generate/random",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode())
            print("API unexpected success:", body["cost_sek"])
            return False
    except urllib.error.HTTPError as exc:
        err = json.loads(exc.read().decode())["error"]
        print("API error code:", err["code"])
        print("API suggested_stake_sek:", err.get("suggested_stake_sek"))
        print("API suggested_combinations:", err.get("suggested_combinations"))
        suggested = err.get("suggested_stake_sek")
        if err["code"] != "BUDGET_NOT_MET" or suggested is None:
            return False
        payload["budget"] = suggested
        req2 = urllib.request.Request(
            f"{URL}api/v1/generate/random",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req2) as resp2:
            ok = json.loads(resp2.read().decode())
        print("API retry cost_sek:", ok["cost_sek"])
        return ok["cost_sek"] == suggested and set(leg6_horses) <= set(ok["selections"]["6"])


def test_ui() -> bool:
    dialogs: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.accept()))
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector('.leg-card[data-leg="6"] .horse:not(.scratched)', timeout=20000)

        horses = page.locator('.leg-card[data-leg="6"] .horse:not(.scratched)')
        horse_count = horses.count()
        print("UI leg 6 horses:", horse_count)
        for index in range(horse_count):
            horses.nth(index).click()

        marked = page.eval_on_selector_all(
            '.leg-card[data-leg="6"] .horse.pool-selected',
            "els => els.map(el => el.textContent.trim())",
        )
        print("UI marked leg 6:", marked)

        page.fill("#stake-input", str(BUDGET))
        page.fill("#seed-input", "42")
        page.click("#btn-generate")
        page.wait_for_selector(".slip-row", timeout=20000)

        stake_after = page.input_value("#stake-input")
        slip_rows = page.locator(".slip-row").count()
        cost_text = page.locator("#cost-big").inner_text().strip()
        leg6_slip = page.locator(".slip-row").nth(5).locator(".slip-row-horses").inner_text().strip()

        print("UI dialog count:", len(dialogs))
        if dialogs:
            print("UI dialog:", dialogs[0].replace("\n", " | "))
        print("UI stake after:", stake_after)
        print("UI slip rows:", slip_rows)
        print("UI cost:", cost_text)
        print("UI leg 6 slip:", leg6_slip)

        browser.close()

    return (
        len(dialogs) == 1
        and "20000" in dialogs[0]
        and "Närmaste möjliga kostnad" in dialogs[0]
        and slip_rows == 8
        and float(stake_after.replace(",", ".")) != BUDGET
        and set(marked) <= set(leg6_slip.split())
    )


def main() -> int:
    listing = json.loads(urllib.request.urlopen(f"{URL}api/v1/race-cards").read().decode())
    card_id = listing["race_cards"][0]["id"]
    card = json.loads(urllib.request.urlopen(f"{URL}api/v1/race-cards/{card_id}").read().decode())
    leg6_horses = sorted(
        horse["number"] if isinstance(horse, dict) else horse
        for horse in next(leg for leg in card["legs"] if leg["leg"] == 6)["horses"]
    )
    print("Card:", card_id)
    print("Leg 6 horses:", leg6_horses)

    api_ok = test_api(card_id, leg6_horses)
    ui_ok = test_ui()
    print("API PASS:", api_ok)
    print("UI PASS:", ui_ok)
    print("VERIFY PASS:", api_ok and ui_ok)
    return 0 if api_ok and ui_ok else 1


if __name__ == "__main__":
    sys.exit(main())