import json
from pathlib import Path
from unittest.mock import patch

from vai.atg_fetch import AtgFetchError
from vai.card import build_card, clear_records_cache, is_card_game_id
from vai.server import VaiRequestHandler

from test_server import _get, _get_status, _start_test_server


def _game(game_type: str, legs: int, odds: int = 450) -> dict:
    races = []
    for i in range(legs):
        races.append({
            "id": f"2026-10-17_16_{5 + i}", "number": 5 + i, "name": f"Lopp {i}", "distance": 2140,
            "startMethod": "auto", "startTime": "2026-10-17T15:00:00", "prize": "Pris: 100.000-50.000 kr.",
            "track": {"id": 16, "name": "Gävle", "condition": "light"}, "status": "upcoming",
            "starts": [
                {"number": 1, "postPosition": 1, "distance": 2140,
                 "horse": {"id": 100 + i, "name": f"H{i}", "homeTrack": {"name": "Gävle"},
                           "trainer": {"firstName": "T", "lastName": "R", "homeTrack": {"name": "Solvalla"}},
                           "shoes": {"front": {"hasShoe": True}, "back": {"hasShoe": False}}},
                 "driver": {"id": 7, "firstName": "K", "lastName": "U", "homeTrack": {"name": "Gävle"}},
                 "pools": {"vinnare": {"odds": odds}, game_type: {"betDistribution": 2500, "trend": 0.1}}},
                {"number": 2, "scratched": True, "horse": {"id": 900 + i, "name": "S"}, "driver": {},
                 "pools": {"vinnare": {"odds": 9999}}},
            ],
        })
    return {"type": game_type, "status": "bettable", "races": races,
            "pools": {game_type: {"turnover": 1234500, "systemCount": 10}}}


RESULTS = {"records": [{"place": "1", "start": {"distance": 2140, "driver": {"id": 8}}},
                       {"place": "0", "galloped": True, "start": {}}]}


def test_is_card_game_id() -> None:
    assert is_card_game_id("V85_2026-10-17_16_5")
    assert is_card_game_id("V75_2026-10-17_16_5")
    assert not is_card_game_id("../etc")
    assert not is_card_game_id("bollnas-2026-07-15")


def test_build_card_v85_and_open_odds_kept(tmp_path: Path) -> None:
    clear_records_cache()
    with patch("vai.card.fetch_horse_results", return_value=RESULTS):
        c = build_card("V85_2026-10-17_16_5", odds_dir=tmp_path, fetch_game=lambda g: _game("V85", 8, 450))
        assert c["legCount"] == 8 and c["product"] == "V85" and c["turnover"] == 12345
        s = c["legs"][0]["starters"][0]
        assert s["odds"] == 4.5 and s["oddsOpen"] == 4.5 and s["oddsDelta"] == 0
        assert s["bookingPct"] == 25.0 and s["formLast5"] == "1-x" and s["gallops"] == 1
        assert s["horseKm"] == 0 and s["trainerKm"] and s["driverChange"] is True
        assert c["legs"][0]["starters"][1]["scratched"] and c["legs"][0]["starters"][1]["oddsOpen"] is None
        saved = json.loads((tmp_path / "V85_2026-10-17_16_5.json").read_text())
        assert saved == {f"2026-10-17_16_{5 + i}_1": 4.5 for i in range(8)}
        c2 = build_card("V85_2026-10-17_16_5", odds_dir=tmp_path, fetch_game=lambda g: _game("V85", 8, 300))
        s2 = c2["legs"][0]["starters"][0]
        assert s2["odds"] == 3.0 and s2["oddsOpen"] == 4.5 and s2["oddsDelta"] == -1.5
    assert not list(tmp_path.glob("*.tmp"))


def test_build_card_v75_leg_count(tmp_path: Path) -> None:
    with patch("vai.card.fetch_horse_results", return_value=RESULTS):
        c = build_card("V75_2026-10-17_16_5", odds_dir=tmp_path, fetch_game=lambda g: _game("V75", 7))
    assert c["legCount"] == 7 and c["legs"][0]["starters"][0]["bookingPct"] == 25.0


def test_api_card_endpoint(tmp_path: Path) -> None:
    server, base = _start_test_server()
    VaiRequestHandler.card_odds_dir = tmp_path
    try:
        with patch("vai.card.fetch_json", return_value=_game("V85", 8)) as fj, \
             patch("vai.card.fetch_horse_results", return_value=RESULTS):
            data = _get(f"{base}/api/v1/card/V85_2026-10-17_16_5")
            assert fj.call_args[0][0].endswith("/games/V85_2026-10-17_16_5")
        assert data["legCount"] == 8 and data["sortableColumns"]
        assert (tmp_path / "V85_2026-10-17_16_5.json").is_file()
        status, err = _get_status(f"{base}/api/v1/card/bollnas-2026-07-15")
        assert status == 400 and err["error"]["code"] == "INVALID_ID"
        with patch("vai.card.fetch_json", side_effect=AtgFetchError("down")):
            status, err = _get_status(f"{base}/api/v1/card/V85_2026-10-17_16_6")
        assert status == 502 and err["error"]["code"] == "ATG_UNAVAILABLE"
    finally:
        VaiRequestHandler.card_odds_dir = None
        server.shutdown()


def _with_stats(game: dict, starts: int) -> dict:
    for r in game["races"]:
        for s in r["starts"]:
            s["horse"]["statistics"] = {"life": {"starts": starts}}
    return game


def test_form_disk_cache_keyed_by_life_starts(tmp_path: Path) -> None:
    odds, form = tmp_path / "card-odds", tmp_path / "card-form"
    clear_records_cache()
    with patch("vai.card.fetch_horse_results", return_value=RESULTS) as fh:
        c = build_card("V85_2026-10-17_16_5", odds_dir=odds, fetch_game=lambda g: _with_stats(_game("V85", 8), 40))
        assert fh.call_count == 16 and c["legs"][0]["starters"][0]["formLast5"] == "1-x"
    assert (form / "100.json").is_file()
    clear_records_cache()  # simulate server restart: disk serves form, no ATG calls
    with patch("vai.card.fetch_horse_results", return_value=RESULTS) as fh:
        c = build_card("V85_2026-10-17_16_5", odds_dir=odds, fetch_game=lambda g: _with_stats(_game("V85", 8), 40))
        assert fh.call_count == 0 and c["legs"][0]["starters"][0]["formLast5"] == "1-x"
        # horse raced again (start count changed) → refetch
        build_card("V85_2026-10-17_16_5", odds_dir=odds, fetch_game=lambda g: _with_stats(_game("V85", 8), 41))
        assert fh.call_count == 16
    assert json.loads((form / "100.json").read_text())["lifeStarts"] == 41


def test_include_form_cached_reports_missing(tmp_path: Path) -> None:
    clear_records_cache()
    with patch("vai.card.fetch_horse_results", return_value=RESULTS) as fh:
        c = build_card("V85_2026-10-17_16_5", odds_dir=tmp_path / "o", include_form="cached",
                       fetch_game=lambda g: _with_stats(_game("V85", 8), 3))
        assert fh.call_count == 0 and c["formMissing"] == 16
        assert c["legs"][0]["starters"][0]["odds"] == 4.5 and c["legs"][0]["starters"][0]["formLast5"] is None
        build_card("V85_2026-10-17_16_5", odds_dir=tmp_path / "o", fetch_game=lambda g: _with_stats(_game("V85", 8), 3))
        c = build_card("V85_2026-10-17_16_5", odds_dir=tmp_path / "o", include_form="cached",
                       fetch_game=lambda g: _with_stats(_game("V85", 8), 3))
        assert c["formMissing"] == 0 and c["legs"][0]["starters"][0]["formLast5"] == "1-x"


def test_game_fetch_shared_between_concurrent_callers() -> None:
    import threading
    import time as _t
    from vai.atg_fetch import clear_game_shared, fetch_game_shared
    clear_game_shared()
    calls = []

    def slow():
        calls.append(1)
        _t.sleep(0.2)
        return {"races": [1]}
    out = []
    ts = [threading.Thread(target=lambda: out.append(fetch_game_shared("V85_X", slow))) for _ in range(3)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert len(calls) == 1 and out == [{"races": [1]}] * 3
    clear_game_shared()
