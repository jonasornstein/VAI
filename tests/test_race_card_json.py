"""Tests for race card API serialization."""

from __future__ import annotations

from atg.io.race_card_json import race_card_to_dict
from atg.models.race_card import Leg, RaceCard, RaceInfo


def test_race_card_to_dict_includes_race_info() -> None:
    legs = []
    for i in range(1, 9):
        legs.append(
            Leg(
                leg=i,
                race_label=f"V85-{i}",
                horses=(1, 3),
                start_time="16:10" if i == 1 else None,
                race_info=RaceInfo(
                    race_name="STL Stodivisionen",
                    distance_m=2140,
                    start_method="volt",
                    class_summary="3-åriga ston",
                )
                if i == 1
                else None,
            )
        )
    card = RaceCard(
        game="v85",
        date="2026-07-11",
        track="Årjäng",
        legs=tuple(legs),
        source="atg",
        fetched_at="2026-07-11T10:00:00Z",
        settled=False,
    )
    payload = race_card_to_dict(card)
    leg1 = payload["legs"][0]
    assert leg1["race_info"]["distance_m"] == 2140
    assert leg1["race_info"]["start_method"] == "volt"
    assert leg1["race_info"]["race_name"] == "STL Stodivisionen"
    assert "race_info" not in payload["legs"][1]


def test_race_card_to_dict_includes_horse_names() -> None:
    card = RaceCard(
        game="v85",
        date="2026-07-11",
        track="Årjäng",
        legs=(
            Leg(
                leg=1,
                race_label="V85-1",
                horses=(1, 7),
                horse_names=((1, "Easy Pick"), (7, "Hankypanky Leonie")),
            ),
        )
        + tuple(Leg(leg=i, race_label=f"V85-{i}", horses=(1,)) for i in range(2, 9)),
        source="atg",
        fetched_at="2026-07-11T10:00:00Z",
        settled=False,
    )
    payload = race_card_to_dict(card)
    assert payload["legs"][0]["horse_names"] == {"1": "Easy Pick", "7": "Hankypanky Leonie"}
    assert "horse_names" not in payload["legs"][1]