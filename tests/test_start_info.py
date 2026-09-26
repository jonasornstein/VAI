"""Tests for Fundamental start-info (last-5 codes, km, payload)."""

from __future__ import annotations

from vai.models.race_card import Leg, RaceInfo
from vai.start_info import compact_last5, extract_starts_from_game, form_token, leg_header, starts_from_yaml_card
from vai.track_distance import km_between


def test_leg_header_includes_prize() -> None:
    header = leg_header(
        Leg(
            leg=1,
            race_label="V85-1",
            horses=(1,),
            start_time="15:02",
            race_info=RaceInfo(
                race_name="Aby",
                distance_m=2140,
                start_method="auto",
                prize="Pris: 500.000-250.000 kr",
            ),
        )
    )
    assert header["race_info"]["prize"] == "Pris: 500.000-250.000 kr"
    assert header["race_info"]["distance_m"] == 2140
    assert leg_header(Leg(leg=2, race_label="V85-2", horses=(1,)))["race_info"] is None


def test_form_token_diskad() -> None:
    assert form_token({"disqualified": True, "place": "1"}) == "d"
    assert form_token({"disqualified": True, "galloped": True}) == "d"


def test_form_token_placing_and_osk() -> None:
    assert form_token({"place": "4"}) == "4"
    assert form_token({"place": "0", "galloped": True}) == "o"
    assert form_token({"place": None}) == "o"
    assert form_token({}) == "o"


def test_compact_last5_newest_first() -> None:
    records = [
        {"place": "4"},
        {"place": "4"},
        {"place": "1"},
        {"place": "1"},
        {"disqualified": True, "galloped": True},
        {"place": "2"},
    ]
    assert compact_last5(records) == "4-4-1-1-d"


def test_km_same_track_zero() -> None:
    assert km_between("Färjestad", "Färjestad") == 0


def test_km_solvalla_farjestad_estimate() -> None:
    km = km_between("Solvalla", "Färjestad")
    assert km is not None
    assert 300 <= km <= 420


def test_km_unknown_track_none() -> None:
    assert km_between("Bjerke", "Färjestad") is None
    assert km_between(None, "Färjestad") is None


def test_extract_starts_includes_scratches_and_pools() -> None:
    payload = {
        "races": [
            {
                "number": 5,
                "track": {"name": "Färjestad"},
                "starts": [
                    {
                        "number": 1,
                        "postPosition": 1,
                        "scratched": False,
                        "horse": {
                            "id": 1,
                            "name": "Licorice Sisu",
                            "homeTrack": {"name": "Solvalla"},
                        },
                        "driver": {
                            "firstName": "Örjan",
                            "lastName": "Kihlström",
                            "homeTrack": {"name": "Solvalla"},
                        },
                        "pools": {
                            "vinnare": {"odds": 967},
                            "V85": {"betDistribution": 1470},
                        },
                    },
                    {
                        "number": 10,
                        "postPosition": 10,
                        "scratched": True,
                        "horse": {"id": 10, "name": "Wise Emotions", "homeTrack": {"name": "Färjestad"}},
                        "driver": {
                            "firstName": "Ole Johan",
                            "lastName": "Östre",
                            "homeTrack": {"name": "Färjestad"},
                        },
                        "pools": {"vinnare": {"odds": 9900}, "V85": {"betDistribution": 10}},
                    },
                ],
            }
        ]
        + [{"number": n, "starts": [{"number": 1, "horse": {"name": "X"}}]} for n in range(6, 13)]
    }
    rows = extract_starts_from_game(payload, race_track="Färjestad", include_form=False)
    assert len(rows[1]) == 2
    first = rows[1][0]
    assert first["name"] == "Licorice Sisu"
    assert first["kusk"] == "Örjan Kihlström"
    assert first["odds"] == 9.67
    assert first["v85_pct"] == 0.147
    assert first["km_horse"] == km_between("Solvalla", "Färjestad")
    scratched = rows[1][1]
    assert scratched["scratched"] is True
    assert scratched["odds"] is None
    assert scratched["v85_pct"] is None
    assert scratched["km_horse"] == 0


def test_starts_from_yaml_card(sample_race_card) -> None:
    by_leg = starts_from_yaml_card(sample_race_card)
    assert set(by_leg.keys()) == set(range(1, 9))
    row = by_leg[1][0]
    assert "number" in row
    assert row["kusk"] is None
    assert row["last5"] is None
