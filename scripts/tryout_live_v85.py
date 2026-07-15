"""Test Hari v1.1 against today's live ATG V85 schedule."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import date

from vai.atg_race_card import fetch_atg_race_card_bundle
from vai.io.pools import empty_operator_pools
from vai.schedule import fetch_atg_schedule, rounds_for_date
from vai.strategies.random import generate_random_v1
from vai.models.proposal import RandomResult

URL = "http://127.0.0.1:8765/"
TODAY = date.today().isoformat()


def main() -> int:
    schedule = fetch_atg_schedule()
    today_rounds = rounds_for_date(schedule, TODAY)

    print(f"Today ({TODAY})")
    print(f"  V85 rounds today: {len(today_rounds)}")
    if today_rounds:
        for r in today_rounds:
            print(f"    {r.game_id} · {r.track}")
    else:
        print("  (no V85 on ATG today — V85 is typically Saturday)")

    print(f"\nLive ATG schedule")
    print(f"  default_date: {schedule.default_date}")
    for r in schedule.rounds:
        if not r.settled:
            print(f"  upcoming: {r.game_id} · {r.track} · {r.date} · bettable={r.bettable}")

    game_id = next(r.game_id for r in schedule.rounds if not r.settled)
    card, dists, _odds = fetch_atg_race_card_bundle(game_id)
    print(f"\nRace card: {card.track} {card.date}")
    for leg in card.legs:
        print(f"  leg {leg.leg}: {len(leg.horses)} horses", end="")
        if leg.scratches:
            print(f" (scratches: {list(leg.scratches)})", end="")
        print()

    outcome = generate_random_v1(card, empty_operator_pools(), 500.0, seed=42)
    if not isinstance(outcome, RandomResult):
        print("Generate failed:", outcome)
        return 1
    print(f"\nGenerate (seed 42, 500 SEK)")
    print(f"  cost: {outcome.cost_sek} SEK · rows: {outcome.combinations}")
    print(f"  breakdown: {outcome.cost_breakdown}")

    # API via local server
    try:
        api_schedule = json.loads(urllib.request.urlopen(f"{URL}api/v1/schedule/v85").read())
        api_card = json.loads(urllib.request.urlopen(f"{URL}api/v1/race-cards/{game_id}").read())
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
        api_gen = json.loads(urllib.request.urlopen(req).read())
    except urllib.error.URLError as exc:
        print("\nLocal server offline:", exc)
        return 1

    print(f"\nLocal UI API")
    print(f"  schedule default: {api_schedule['default_date']}")
    print(f"  card track: {api_card['track']} · distributions: {bool(api_card.get('leg_distributions'))}")
    print(f"  api cost: {api_gen['cost_sek']} SEK · hit_summary: {'yes' if 'hit_summary' in api_gen else 'no'}")
    if "hit_summary" in api_gen:
        hs = api_gen["hit_summary"]
        print(f"    p8={hs['p8']*100:.4f}% · p5plus={hs['p5plus']*100:.2f}%")

    ok = (
        outcome.cost_sek == 500.0
        and api_gen["cost_sek"] == 500.0
        and outcome.selections == {int(k): v for k, v in api_gen["selections"].items()}
        and api_card["track"] == card.track
    )
    print(f"\nLIVE V85 TEST: {'PASS' if ok else 'FAIL'}")
    print(f"Using live card: {game_id}")
    if not today_rounds:
        print(f"Note: Open http://127.0.0.1:8765/ — DATUM shows {schedule.default_date} (next V85), not today.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())