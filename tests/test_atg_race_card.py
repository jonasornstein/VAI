"""Tests for ATG game JSON parsing (F-007, F-029)."""

from __future__ import annotations

from vai.atg_race_card import (
    extract_horse_names,
    extract_leg_distributions,
    extract_leg_odds,
    extract_race_info,
    parse_atg_game,
)

SAMPLE_RACE = {
    "name": "Hästkraft Årjäng 2026 - STL Stodivisionen",
    "distance": 2140,
    "startMethod": "volte",
    "startTime": "2026-07-11T16:10:00",
    "scheduledStartTime": "2026-07-11T16:10:00",
    "terms": ["3-åriga och äldre svenska ston 100.001 - 725.000 kr."],
    "status": "upcoming",
    "starts": [
        {"number": 1, "scratched": False, "horse": {"name": "Easy Pick"}},
        {"number": 2, "scratched": True, "horse": {"name": "Bee My Clementine"}},
        {"number": 3, "scratched": False, "horse": {"name": "Amelia Earhart"}},
    ],
}


def _game_payload() -> dict:
    return {
        "id": "V85_2026-07-11_31_5",
        "status": "bettable",
        "races": [{**SAMPLE_RACE, "number": 5}] * 7 + [{**SAMPLE_RACE, "number": 12}],
    }


def test_extract_race_info_from_atg_race() -> None:
    info = extract_race_info(SAMPLE_RACE)
    assert info is not None
    assert info.race_name == "Hästkraft Årjäng 2026 - STL Stodivisionen"
    assert info.distance_m == 2140
    assert info.start_method == "volt"
    assert info.class_summary == "3-åriga och äldre svenska ston 100.001 - 725.000 kr."
    assert info.status == "upcoming"


def test_extract_horse_names_from_atg_starts() -> None:
    names = extract_horse_names(SAMPLE_RACE["starts"])
    assert names == ((1, "Easy Pick"), (2, "Bee My Clementine"), (3, "Amelia Earhart"))


def test_parse_atg_game_includes_race_info_and_excludes_scratches() -> None:
    card = parse_atg_game("V85_2026-07-11_31_5", _game_payload())
    leg1 = card.leg_by_number(1)
    assert leg1.race_info is not None
    assert leg1.race_info.distance_m == 2140
    assert 2 in leg1.scratches
    assert 2 not in leg1.horses
    assert 1 in leg1.horses
    assert 3 in leg1.horses
    assert dict(leg1.horse_names) == {
        1: "Easy Pick",
        2: "Bee My Clementine",
        3: "Amelia Earhart",
    }


def _start_with_pools(number: int, bet_dist: int, vinnare_odds: int) -> dict:
    return {
        "number": number,
        "scratched": False,
        "horse": {"name": f"Horse {number}"},
        "pools": {
            "V85": {"betDistribution": bet_dist},
            "vinnare": {"odds": vinnare_odds},
        },
    }


def test_extract_leg_distributions_and_odds() -> None:
    payload = {
        "races": [
            {
                "starts": [
                    _start_with_pools(1, 2730, 813),  # 27.3% pool, odds 8.13
                    _start_with_pools(2, 1500, 450),
                ]
            }
        ]
    }
    dists = extract_leg_distributions(payload)
    odds = extract_leg_odds(payload)
    assert dists[1][1] == 0.273
    assert dists[1][2] == 0.15
    assert odds[1][1] == 8.13
    assert odds[1][2] == 4.5