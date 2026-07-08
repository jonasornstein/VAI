"""Tests for ATG game JSON parsing (F-007, F-029)."""

from __future__ import annotations

from atg.atg_race_card import extract_race_info, parse_atg_game

SAMPLE_RACE = {
    "name": "Hästkraft Årjäng 2026 - STL Stodivisionen",
    "distance": 2140,
    "startMethod": "volte",
    "startTime": "2026-07-11T16:10:00",
    "scheduledStartTime": "2026-07-11T16:10:00",
    "terms": ["3-åriga och äldre svenska ston 100.001 - 725.000 kr."],
    "status": "upcoming",
    "starts": [
        {"number": 1, "scratched": False},
        {"number": 2, "scratched": True},
        {"number": 3, "scratched": False},
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


def test_parse_atg_game_includes_race_info_and_excludes_scratches() -> None:
    card = parse_atg_game("V85_2026-07-11_31_5", _game_payload())
    leg1 = card.leg_by_number(1)
    assert leg1.race_info is not None
    assert leg1.race_info.distance_m == 2140
    assert 2 in leg1.scratches
    assert 2 not in leg1.horses
    assert 1 in leg1.horses
    assert 3 in leg1.horses