"""Verify Expert STATS toggle: k/N + % on horses and consensus strip."""

from __future__ import annotations

import json
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

from vai.activity_log import ActivityLogger
from vai.server import VaiRequestHandler, find_repo_root

OUT_DIR = Path(__file__).resolve().parent


def _start_server() -> tuple[ThreadingHTTPServer, str]:
    root = find_repo_root()
    VaiRequestHandler.repo_root = root
    VaiRequestHandler.mockup_dir = root / "outbox" / "mockups"
    VaiRequestHandler.race_cards_dir = root / "inbox" / "race-cards"
    VaiRequestHandler.expert_tips_dir = root / "inbox" / "expert-tips"
    VaiRequestHandler.activity_logger = ActivityLogger(None)
    server = ThreadingHTTPServer(("127.0.0.1", 0), VaiRequestHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{port}"


def main() -> int:
    checks: list[tuple[str, bool]] = []
    server, base = _start_server()
    try:
        with urlopen(f"{base}/api/v1/expert-stats?date=2026-07-25&track=Bolln%C3%A4s") as response:
            payload = json.loads(response.read().decode("utf-8"))
        checks.append(("api_tip_count_5", payload.get("tip_count") == 5))
        leg2 = {row["horse"]: row for row in payload["legs"]["2"]}
        checks.append(("api_leg2_h2_5", leg2[2]["count"] == 5 and leg2[2]["pct"] == 100.0))

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1400, "height": 900})
            page.goto(base + "/", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector(".mode-tabs", timeout=20000)

            stats_btn = page.locator("#btn-expert-stats")
            checks.append(("stats_hidden_in_hari", not stats_btn.is_visible()))

            page.locator('[data-mode="expert"]').click()
            page.wait_for_selector("#expert-tips-panel", timeout=15000)
            page.wait_for_selector("#legs-grid .horse", timeout=25000)
            checks.append(("stats_visible_in_expert", stats_btn.is_visible()))
            checks.append(("stats_label", stats_btn.inner_text().strip() == "STATS"))
            after_clear = page.evaluate(
                """() => {
                  var clear = document.getElementById('btn-deselect-all');
                  var stats = document.getElementById('btn-expert-stats');
                  return !!(clear && stats && clear.nextElementSibling === stats);
                }"""
            )
            checks.append(("stats_right_of_rensa_alla", after_clear))

            stats = payload
            page.evaluate("(stats) => window.__vaiApplyExpertStats(stats)", stats)
            page.wait_for_timeout(300)

            strip = page.locator("#expert-stats-strip")
            checks.append(("strip_visible", strip.is_visible()))
            strip_text = strip.inner_text()
            checks.append(("strip_count_header", "5 tips" in strip_text))
            checks.append(("strip_pct", "100%" in strip_text))
            checks.append(("strip_frac", "5/5" in strip_text))

            horse_meta = page.locator("#legs-grid .horse .meta .count").first
            checks.append(("horse_count_line", horse_meta.count() > 0 and "/" in horse_meta.inner_text()))
            pct_line = page.locator("#legs-grid .horse .meta .pct").first
            checks.append(("horse_pct_line", pct_line.count() > 0 and "%" in pct_line.inner_text()))
            checks.append(("grid_stats_mode", page.locator("#legs-grid.stats-mode").count() == 1))

            page.locator("#expert-stats-strip").screenshot(path=str(OUT_DIR / "test-expert-stats-strip.png"))
            page.locator("#legs-grid").screenshot(path=str(OUT_DIR / "test-expert-stats-grid.png"))

            page.locator("#btn-expert-stats").click()
            page.wait_for_timeout(200)
            checks.append(("toggle_off_strip", not page.locator("#expert-stats-strip").is_visible()))
            checks.append(("toggle_off_pool", page.locator("#legs-grid .horse .meta .pool").count() > 0))

            page.locator('[data-mode="random"]').click()
            page.wait_for_timeout(200)
            checks.append(("hari_hides_stats_btn", not page.locator("#btn-expert-stats").is_visible()))

            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        VaiRequestHandler.activity_logger = None

    print("Expert STATS verification")
    ok = True
    for name, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        if not passed:
            ok = False
    print("VERIFY PASS:" if ok else "VERIFY FAIL:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
