import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from vai.api_auth import is_protected
from vai.bets import BetStore, BetValidationError, _rows_by_correct, compute_rows, record_snapshots, validate_bet
from vai.server import VaiRequestHandler
from test_server import TEST_API_KEY, _start_test_server


def _bet(**over):
    body = {
        "date": "2026-10-17",
        "game": "V85",
        "track": "Solvalla",
        "stakePerRow": 0.5,
        "legs": [
            {"leg": 1, "picks": [{"startNo": 1, "horseName": "A", "streckPct": 30.5, "odds": 3.2},
                                 {"startNo": 4, "horseName": "B", "streckPct": 10, "odds": 8.0}]},
            {"leg": 2, "picks": [{"startNo": 7, "horseName": "C", "streckPct": 55, "odds": 1.8}]},
            {"leg": 3, "picks": [{"startNo": 2}, {"startNo": 3}, {"startNo": 5}]},
        ],
    }
    body.update(over)
    return body


@pytest.fixture
def store(tmp_path):
    return BetStore(tmp_path / "vai.sqlite")


def test_compute_rows():
    assert compute_rows([2, 1, 3]) == 6
    assert compute_rows([1]) == 1


def test_create_bet_server_computes_rows_and_price(store):
    bet = store.create_bet(_bet(rows=999, price=1))
    assert bet["rows"] == 6
    assert bet["price"] == 3.0
    assert bet["result"] == {"correct": None, "of": 3, "payout": None, "settled": False}
    assert bet["legs"][0]["picks"][0] == {"startNo": 1, "horseName": "A", "streckPct": 30.5, "odds": 3.2,
                                          "finalOdds": None, "finalStreckPct": None}
    assert bet["legs"][2]["picks"][0]["horseName"] is None


def test_schema_idempotent(tmp_path):
    p = tmp_path / "x.sqlite"
    BetStore(p).create_bet(_bet())
    assert len(BetStore(p).list_bets()) == 1


def _reasons(errors):
    return {(e["leg"], e["startNo"], e["reason"]) for e in errors}


def test_validation_errors():
    body = _bet(legs=[
        {"leg": 1, "picks": []},
        {"leg": 2, "picks": [{"startNo": 5}, {"startNo": 5}]},
        {"leg": 3, "picks": [{"startNo": 1, "odds": -2}]},
    ])
    assert _reasons(validate_bet(body)) == {(1, None, "empty_leg"), (2, 5, "duplicate"), (3, 1, "invalid_value")}
    assert validate_bet(_bet(stakePerRow="x"))[0]["field"] == "stakePerRow"
    assert validate_bet(_bet(date="17/10"))[0]["field"] == "date"


def test_validation_against_card():
    card = {1: {"starters": {1, 2, 3}, "scratched": {4}}, 2: {"starters": {7}, "scratched": set()},
            3: {"starters": {2, 3, 5}, "scratched": set()}}
    assert _reasons(validate_bet(_bet(), card)) == {(1, 4, "scratched")}
    card[2] = {"starters": {1}, "scratched": set()}
    assert (2, 7, "unknown_start") in _reasons(validate_bet(_bet(), card))


def test_create_rejects(store):
    with pytest.raises(BetValidationError):
        store.create_bet(_bet(legs=[{"leg": 1, "picks": []}]))
    assert store.list_bets() == []


def test_rows_by_correct():
    picks = {1: {1, 4}, 2: {7}, 3: {2, 3, 5}}
    assert _rows_by_correct(picks, {1: 1, 2: 7, 3: 2}) == {3: 1, 2: 3, 1: 2}
    assert _rows_by_correct(picks, {1: 9, 2: 7, 3: 2}) == {2: 2, 1: 4}


def test_settle_with_snapshots_and_payout(store):
    store.create_bet(_bet())
    store.create_bet(_bet(game="V64"))
    record_snapshots(store, {"date": "2026-10-17", "game": "V85", "track": "Solvalla", "source": "manual",
                             "phase": "final", "legs": [{"leg": 1, "winnerStartNo": 1, "starts": [
        {"startNo": 1, "horseName": "A", "scratched": False, "odds": 2.9, "streckPct": 33.0}]}]})
    res = store.settle({"date": "2026-10-17", "game": "V85",
                        "legs": [{"leg": 1, "winner": 1, "winnerName": "A"}, {"leg": 2, "winner": 7},
                                 {"leg": 3, "winner": 9}],
                        "payouts": {"3": 1000, "2": 10}})
    assert res["settled"] == 1
    bet = res["bets"][0]
    assert [l["hit"] for l in bet["legs"]] == [True, True, False]
    assert bet["legs"][0]["winnerName"] == "A"
    assert bet["result"] == {"correct": 2, "of": 3, "payout": 30.0, "settled": True}
    assert bet["legs"][0]["picks"][0]["finalOdds"] == 2.9
    assert bet["legs"][0]["picks"][0]["finalStreckPct"] == 33.0
    assert bet["legs"][0]["picks"][1]["finalOdds"] is None
    other = store.list_bets()[0] if store.list_bets()[0]["game"] == "V64" else store.list_bets()[1]
    assert other["result"]["settled"] is False


def test_settle_partial_and_no_payouts(store):
    store.create_bet(_bet())
    bet = store.settle({"date": "2026-10-17", "game": "V85", "legs": [{"leg": 1, "winner": 1}]})["bets"][0]
    assert bet["result"]["settled"] is False
    assert bet["legs"][1]["hit"] is None
    bet = store.settle({"date": "2026-10-17", "game": "V85",
                        "legs": [{"leg": 2, "winner": 7}, {"leg": 3, "winner": 5}]})["bets"][0]
    assert bet["result"] == {"correct": 3, "of": 3, "payout": None, "settled": True}


# --- HTTP -------------------------------------------------------------------
@pytest.fixture
def server(tmp_path):
    srv, base = _start_test_server()
    VaiRequestHandler.bet_store = BetStore(tmp_path / "vai.sqlite")
    yield base
    srv.shutdown()
    srv.server_close()
    VaiRequestHandler.bet_store = None


def _req(base, method, path, key=TEST_API_KEY, body=None):
    headers = {"Content-Type": "application/json"}
    if key is not None:
        headers["X-API-Key"] = key
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urlopen(Request(base + path, data=data, headers=headers, method=method)) as r:
            return r.status, json.loads(r.read() or b"{}")
    except HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


ENDPOINTS = [("GET", "/api/bets", None), ("GET", "/api/bets?date=2026-10-17", None), ("POST", "/api/bets", {}),
             ("POST", "/api/bets/settle", {}), ("POST", "/api/snapshots", {})]


def test_is_protected_includes_get():
    assert is_protected("GET", "/api/bets")
    assert is_protected("POST", "/api/snapshots")
    assert not is_protected("GET", "/api/betsx")


@pytest.mark.parametrize("method,path,body", ENDPOINTS)
def test_auth_401(server, method, path, body):
    assert _req(server, method, path, key=None, body=body)[0] == 401
    assert _req(server, method, path, key="wrong", body=body)[0] == 401


@pytest.mark.parametrize("method,path,body", ENDPOINTS)
def test_auth_503_without_server_key(server, monkeypatch, method, path, body):
    monkeypatch.delenv("VAI_API_KEY", raising=False)
    status, resp = _req(server, method, path, body=body)
    assert status == 503
    assert resp["error"]["code"] == "API_KEY_NOT_CONFIGURED"


def test_http_flow(server):
    status, bet = _req(server, "POST", "/api/bets", body=_bet())
    assert status == 201 and bet["rows"] == 6 and bet["price"] == 3.0
    status, resp = _req(server, "POST", "/api/bets", body=_bet(legs=[{"leg": 2, "picks": []}]))
    assert status == 422 and resp["errors"][0]["reason"] == "empty_leg"
    status, resp = _req(server, "POST", "/api/snapshots", body={
        "date": "2026-10-17", "game": "V85", "source": "manual", "phase": "final",
        "legs": [{"leg": 2, "winnerStartNo": 7, "starts": [{"startNo": 7, "odds": 1.7, "streckPct": 60}]}]})
    assert status == 201 and resp["inserted"] == 1
    status, resp = _req(server, "POST", "/api/bets/settle", body={
        "date": "2026-10-17", "game": "V85", "legs": [{"leg": 1, "winner": 4}, {"leg": 2, "winner": 7},
                                                     {"leg": 3, "winner": 3}], "payouts": {"3": 250}})
    assert status == 200 and resp["bets"][0]["result"]["payout"] == 250
    status, resp = _req(server, "GET", "/api/bets?date=2026-10-17")
    assert status == 200 and len(resp["bets"]) == 1
    assert resp["bets"][0]["legs"][1]["picks"][0]["finalOdds"] == 1.7
    assert _req(server, "GET", "/api/bets?date=2026-10-18")[1] == {"bets": []}
    assert _req(server, "GET", "/api/bets?date=bad")[0] == 422


def test_http_rejects_scratched_from_yaml_card(server):
    # inbox/race-cards has a v85 card for 2026-07-11 (Årjäng); 99 is never a start number there.
    body = _bet(date="2026-07-11", game="v85", legs=[{"leg": 1, "picks": [{"startNo": 1}, {"startNo": 29}]}])
    status, resp = _req(server, "POST", "/api/bets", body=body)
    assert status == 422
    assert resp["errors"] == [{"leg": 1, "startNo": 29, "reason": "unknown_start"}]


def test_http_rejects_scratched_from_snapshots(server):
    status, _ = _req(server, "POST", "/api/snapshots", body={
        "date": "2026-10-17", "game": "V85", "source": "manual", "phase": "pre", "legs": [
            {"leg": 1, "starts": [{"startNo": 1, "scratched": False}, {"startNo": 4, "scratched": True}]},
            {"leg": 2, "starts": [{"startNo": 7}]},
            {"leg": 3, "starts": [{"startNo": 2}, {"startNo": 3}, {"startNo": 5}]}]})
    assert status == 201
    status, resp = _req(server, "POST", "/api/bets", body=_bet())
    assert status == 422 and resp["errors"] == [{"leg": 1, "startNo": 4, "reason": "scratched"}]
