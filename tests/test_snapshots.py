"""K-35: manual odds/streck snapshots (JR legal decision: manual Update only)."""
import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest

from vai.bets import BetStore, BetValidationError, parse_start_time, record_snapshots
from test_bets import _bet, _req, server  # noqa: F401  (fixture re-export)

NOW = datetime(2026, 10, 17, 12, 0, tzinfo=timezone.utc)  # 14:00 Stockholm


@pytest.fixture
def store(tmp_path):
    return BetStore(tmp_path / "vai.sqlite")


def _snap(phase="pre", source="manual", legs=None, **over):
    body = {"date": "2026-10-17", "game": "V85", "track": "Solvalla", "source": source, "phase": phase,
            "legs": legs if legs is not None else [
                {"leg": 1, "startTime": "2026-10-17T16:20:00+02:00",
                 "starts": [{"startNo": 1, "horseName": "A", "odds": 3.2, "streckPct": 30.5},
                            {"startNo": 2, "scratched": True},
                            {"startNo": 3, "odds": 5.0, "streckPct": 12}]}]}
    body.update(over)
    return body


def _reasons(exc):
    return [(e["leg"], e["startNo"], e["reason"]) for e in exc.value.errors]


def test_inserts_history_with_taken_at_source_and_minutes(store):
    r1 = record_snapshots(store, _snap(), now=NOW)
    r2 = record_snapshots(store, _snap(), now=NOW.replace(minute=30))
    assert r1["takenAt"] == "2026-10-17T12:00:00+00:00" and r1["source"] == "manual"
    assert r1["inserted"] == 3 and r1["legs"][0]["minutesToStart"] == 140.0
    assert r2["legs"][0]["minutesToStart"] == 110.0 and r2["snapshotId"] != r1["snapshotId"]
    conn = store.connect()
    rows = conn.execute("SELECT source, phase, taken_at, scratched FROM snapshot_starts WHERE start_no=2").fetchall()
    assert [tuple(r) for r in rows] == [("manual", "pre", "2026-10-17T12:00:00+00:00", 1),
                                        ("manual", "pre", "2026-10-17T12:30:00+00:00", 1)]


@pytest.mark.parametrize("src", ["atg", "auto", None, "MANUAL"])
def test_rejects_non_manual_source(store, src):
    with pytest.raises(BetValidationError) as exc:
        record_snapshots(store, _snap(source=src), now=NOW)
    assert (None, None, "invalid_source") in _reasons(exc)
    assert store.connect().execute("SELECT COUNT(*) FROM snapshot_starts").fetchone()[0] == 0


def test_incomplete_field_against_local_card(store):
    card = {1: {"starters": {1, 3, 4}, "scratched": {2}, "startTime": None}}
    legs = [{"leg": 1, "starts": [{"startNo": 1}, {"startNo": 3}]}]
    with pytest.raises(BetValidationError) as exc:
        record_snapshots(store, _snap(legs=legs), card=card, now=NOW)
    assert _reasons(exc) == [(1, 2, "incomplete_field"), (1, 4, "incomplete_field")]


def test_unknown_start_against_local_card(store):
    card = {1: {"starters": {1}, "scratched": set(), "startTime": None}}
    with pytest.raises(BetValidationError) as exc:
        record_snapshots(store, _snap(legs=[{"leg": 1, "starts": [{"startNo": 1}, {"startNo": 9}]}]), card=card, now=NOW)
    assert _reasons(exc) == [(1, 9, "unknown_start")]


def test_incomplete_field_against_prior_snapshot(store):
    record_snapshots(store, _snap(), now=NOW)
    legs = [{"leg": 1, "starts": [{"startNo": 1}, {"startNo": 3}]}]
    with pytest.raises(BetValidationError) as exc:
        record_snapshots(store, _snap(legs=legs), now=NOW)
    assert _reasons(exc) == [(1, 2, "incomplete_field")]


def test_local_card_start_time_wins_over_payload(store):
    card = {1: {"starters": {1, 3}, "scratched": {2},
                "startTime": parse_start_time("14:10", "2026-10-17")}}
    r = record_snapshots(store, _snap(), card=card, now=NOW)
    assert r["legs"][0]["minutesToStart"] == 10.0  # 14:10 Stockholm = 12:10 UTC


def test_minutes_negative_after_start_and_none_without_time(store):
    legs = [{"leg": 1, "startTime": "2026-10-17T11:45:00Z", "starts": [{"startNo": 1}]},
            {"leg": 2, "starts": [{"startNo": 1}]}]
    r = record_snapshots(store, _snap(legs=legs), now=NOW)
    assert [l["minutesToStart"] for l in r["legs"]] == [-15.0, None]


def test_final_requires_decided_leg(store):
    with pytest.raises(BetValidationError) as exc:
        record_snapshots(store, _snap(phase="final"), now=NOW)
    assert _reasons(exc) == [(1, None, "not_decided")]
    # winner given -> ok
    legs = _snap()["legs"]
    legs[0]["winnerStartNo"] = 3
    assert record_snapshots(store, _snap(phase="final", legs=legs), now=NOW)["legs"][0]["winnerStartNo"] == 3
    # start time passed -> ok
    assert record_snapshots(store, _snap(phase="final"), now=NOW.replace(hour=15))["phase"] == "final"


def test_winner_must_be_running_start(store):
    legs = _snap()["legs"]
    legs[0]["winnerStartNo"] = 2  # scratched
    with pytest.raises(BetValidationError) as exc:
        record_snapshots(store, _snap(legs=legs), now=NOW)
    assert _reasons(exc) == [(1, 2, "invalid_value")]


def test_invalid_phase(store):
    with pytest.raises(BetValidationError) as exc:
        record_snapshots(store, _snap(phase="live"), now=NOW)
    assert exc.value.errors[0]["field"] == "phase"


def test_settle_uses_only_latest_final(store):
    store.create_bet(_bet(legs=[{"leg": 1, "picks": [{"startNo": 1}, {"startNo": 3}]}]))
    record_snapshots(store, _snap(), now=NOW)  # pre: must not feed settle
    store.settle({"date": "2026-10-17", "game": "V85", "legs": [{"leg": 1, "winner": 3}]})
    picks = store.list_bets()[0]["legs"][0]["picks"]
    assert picks[0]["finalOdds"] is None
    f1 = _snap()["legs"]
    f1[0]["starts"][0]["odds"] = 2.5
    record_snapshots(store, _snap(phase="final", legs=f1), now=NOW)  # decided via settled winner
    f2 = _snap()["legs"]
    f2[0]["starts"][0].update(odds=2.1, streckPct=40.0)
    record_snapshots(store, _snap(phase="final", legs=f2), now=NOW.replace(minute=5))
    record_snapshots(store, _snap(), now=NOW.replace(minute=10))  # later pre ignored
    bet = store.settle({"date": "2026-10-17", "game": "V85", "legs": [{"leg": 1, "winner": 3}]})["bets"][0]
    p = bet["legs"][0]["picks"]
    assert (p[0]["finalOdds"], p[0]["finalStreckPct"]) == (2.1, 40.0)
    assert store.connect().execute("SELECT COUNT(*) FROM snapshot_starts").fetchone()[0] == 12


def test_http_snapshot_and_errors(server):  # noqa: F811
    status, resp = _req(server, "POST", "/api/snapshots", body=_snap(source="atg"))
    assert status == 422 and resp == {"errors": [{"leg": None, "startNo": None, "reason": "invalid_source",
                                                  "field": "source"}]}
    status, resp = _req(server, "POST", "/api/snapshots", body=_snap())
    assert status == 201 and resp["source"] == "manual" and resp["inserted"] == 3
    assert resp["takenAt"].endswith("+00:00")


def test_http_yaml_card_incomplete_field(server):  # noqa: F811
    # inbox/race-cards/2026-07-11-arjang.yaml is a v85 card; leg 1 has more than one start.
    body = _snap(date="2026-07-11", game="v85", legs=[{"leg": 1, "starts": [{"startNo": 1}]}])
    status, resp = _req(server, "POST", "/api/snapshots", body=body)
    assert status == 422
    assert {e["reason"] for e in resp["errors"]} == {"incomplete_field"}
    assert all(e["leg"] == 1 for e in resp["errors"])


def test_no_automatic_collector_code():
    """JR decision: no timers/threads/loops/ATG fetch in the snapshot path."""
    src = Path(__file__).resolve().parents[1] / "src" / "vai" / "bets.py"
    text = src.read_text()
    tree = ast.parse(text)
    imported = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
                for a in (n.names if isinstance(n, ast.Import) else [ast.alias(n.module or "")])}
    assert not imported & {"sched", "asyncio", "urllib", "requests", "httpx", "subprocess"}
    assert "atg_race_card" not in text and "Timer(" not in text and "time.sleep" not in text
