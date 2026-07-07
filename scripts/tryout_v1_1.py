"""Try out Hari v1.1 — API + UI smoke test."""

from __future__ import annotations

import json
import sys
import urllib.request

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"


def main() -> int:
    checks: list[tuple[str, bool]] = []

    schedule = json.loads(urllib.request.urlopen(f"{URL}api/v1/schedule/v85").read())
    checks.append(("schedule_default", schedule.get("default_date") == "2026-07-11"))
    game_id = schedule["rounds"][0]["game_id"]
    print("Game:", game_id, "·", schedule["rounds"][0]["track"])

    card = json.loads(urllib.request.urlopen(f"{URL}api/v1/race-cards/{game_id}").read())
    checks.append(("leg_distributions", bool(card.get("leg_distributions"))))
    checks.append(("track_arjang", card.get("track") == "Årjäng"))

    pools = {str(i): [] for i in range(1, 9)}
    payload = json.dumps(
        {"race_card_id": game_id, "pools": pools, "budget": 500, "seed": 42}
    ).encode()
    req = urllib.request.Request(
        f"{URL}api/v1/generate/random",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    gen = json.loads(urllib.request.urlopen(req).read())
    checks.append(("api_exact_budget", gen["cost_sek"] == 500.0))
    checks.append(("api_hit_summary", "hit_summary" in gen and "p8" in gen["hit_summary"]))
    print("API cost:", gen["cost_sek"], "SEK · rows:", gen["combinations"])
    print("API hit p8:", f"{gen['hit_summary']['p8'] * 100:.4f}%")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector(".leg-card .horse:not(.scratched)", timeout=25000)

        checks.append(
            ("hari_tab", page.locator('[data-mode="random"]').inner_text().strip() == "Hari")
        )
        checks.append(
            (
                "rationale_header",
                page.locator(".rationale h2").inner_text().strip().upper() == "RATIONALE — HARI",
            )
        )

        spelform_options = page.eval_on_selector(
            "#spelform",
            "sel => Array.from(sel.options).map(o => o.value)",
        )
        checks.append(("spelform_v85_only", spelform_options == ["V85"]))

        page.fill("#stake-input", "500")
        page.fill("#seed-input", "42")
        page.click("#btn-generate")
        page.wait_for_selector(".slip-row", timeout=25000)

        cost = page.locator("#cost-big").inner_text()
        checks.append(("ui_exact_budget", "500,00" in cost and "= budget" in cost))
        checks.append(("slip_8_legs", page.locator(".slip-row").count() == 8))

        hit_visible = page.locator("#hit-bars").is_visible()
        hit_text = page.locator("#hit-bars").inner_text()
        checks.append(("ui_hit_bars", hit_visible and "8 rätt" in hit_text and "%" in hit_text))

        rationale = page.locator("#rationale-text").inner_text()
        checks.append(
            ("ui_rationale", "hästar till budget" in rationale and "Seed 42" in rationale)
        )
        checks.append(
            ("open_atg_btn", page.locator("#btn-open-atg").inner_text().strip().upper() == "ÖPPNA ATG/V85")
        )

        print("UI cost:", cost.replace("\n", " "))
        print("UI hit bars:", hit_text.replace("\n", " | ")[:120])
        browser.close()

    print("\n=== Try-out ===")
    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}: {name}")
    all_ok = all(ok for _, ok in checks)
    print("ALL PASS:", all_ok)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())