from datetime import date

import pytest

from vai.atg_fetch import AtgFetchError
from vai.atg_race_card import is_atg_game_id, parse_atg_game
from vai.schedule import (
    build_schedule,
    parse_date_from_game_id,
    parse_v85_products,
    resolve_next_v85_date,
    rounds_for_date,
)

SAMPLE_PRODUCTS = {
    "upcoming": [
        {
            "id": "V85_2026-07-11_31_5",
            "startTime": "2026-07-11T16:10:00",
            "bettable": True,
            "tracks": [{"id": 31, "name": "Årjäng"}],
        }
    ],
    "results": [
        {
            "id": "V85_2026-07-05_82_5",
            "startTime": "2026-07-05T15:31:33",
            "tracks": [{"id": 82, "name": "Jarlsberg"}],
        }
    ],
}

TODAY_UPCOMING_PRODUCTS = {
    "upcoming": [
        {
            "id": "V85_2026-07-07_18_5",
            "startTime": "2026-07-07T16:10:00",
            "bettable": True,
            "tracks": [{"id": 18, "name": "Halmstad"}],
        },
        {
            "id": "V85_2026-07-11_31_5",
            "startTime": "2026-07-11T16:10:00",
            "bettable": True,
            "tracks": [{"id": 31, "name": "Årjäng"}],
        },
    ],
    "results": [],
}


def test_parse_date_from_game_id() -> None:
    assert parse_date_from_game_id("V85_2026-07-11_31_5") == "2026-07-11"
    assert parse_date_from_game_id("invalid") is None


def test_resolve_next_v85_date_uses_next_future_when_no_v85_today() -> None:
    rounds = parse_v85_products(SAMPLE_PRODUCTS)
    assert resolve_next_v85_date(rounds, today=date(2026, 7, 7)) == "2026-07-11"


def test_resolve_next_v85_date_uses_today_when_unsettled() -> None:
    rounds = parse_v85_products(TODAY_UPCOMING_PRODUCTS)
    assert resolve_next_v85_date(rounds, today=date(2026, 7, 7)) == "2026-07-07"


def test_build_schedule_default_and_dates() -> None:
    schedule = build_schedule(SAMPLE_PRODUCTS, today=date(2026, 7, 7))
    assert schedule.default_date == "2026-07-11"
    assert schedule.dates == ("2026-07-11",)
    assert len(schedule.rounds) == 1
    assert schedule.rounds[0].track == "Årjäng"


def test_rounds_for_date() -> None:
    schedule = build_schedule(TODAY_UPCOMING_PRODUCTS, today=date(2026, 7, 7))
    july_7 = rounds_for_date(schedule, "2026-07-07")
    assert len(july_7) == 1
    assert july_7[0].track == "Halmstad"


def test_resolve_next_v85_date_raises_when_empty() -> None:
    with pytest.raises(AtgFetchError):
        resolve_next_v85_date([], today=date(2026, 7, 7))


def test_is_atg_game_id() -> None:
    assert is_atg_game_id("V85_2026-07-11_31_5")
    assert not is_atg_game_id("2026-07-05-halmstad")


def test_parse_atg_game_builds_eight_legs() -> None:
    payload = {
        "status": "bettable",
        "races": [
            {
                "number": 5 + i,
                "status": "upcoming",
                "scheduledStartTime": f"2026-07-11T{16 + i}:10:00",
                "track": {"name": "Årjäng"},
                "starts": [
                    {"number": 1, "scratched": False},
                    {"number": 2, "scratched": True},
                ],
            }
            for i in range(8)
        ],
    }
    card = parse_atg_game("V85_2026-07-11_31_5", payload)
    assert card.date == "2026-07-11"
    assert card.track == "Årjäng"
    assert card.source == "atg"
    assert len(card.legs) == 8
    assert card.legs[0].horses == (1,)
    assert card.legs[0].scratches == (2,)
    assert card.legs[0].race_info is not None