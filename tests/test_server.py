import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from vai.schedule import V85Round, V85Schedule
from vai.server import VaiRequestHandler, find_repo_root

MOCK_SCHEDULE = V85Schedule(
    source="atg",
    fetched_at="2026-07-07T12:00:00+00:00",
    default_date="2026-07-11",
    dates=("2026-07-11",),
    rounds=(
        V85Round(
            game_id="V85_2026-07-11_31_5",
            date="2026-07-11",
            track="Årjäng",
            track_id=31,
            bettable=True,
            settled=False,
            start_time="2026-07-11T16:10:00",
        ),
    ),
)


def _start_test_server() -> tuple[ThreadingHTTPServer, str]:
    root = find_repo_root()
    VaiRequestHandler.repo_root = root
    VaiRequestHandler.mockup_dir = root / "outbox" / "mockups"
    VaiRequestHandler.race_cards_dir = root / "inbox" / "race-cards"
    VaiRequestHandler.expert_tips_dir = root / "inbox" / "expert-tips"
    server = ThreadingHTTPServer(("127.0.0.1", 0), VaiRequestHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{port}"


def _get(url: str) -> dict:
    with urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def _post(url: str, payload: dict) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def _put(url: str, payload: dict) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="PUT")
    try:
        with urlopen(request) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_head_index_returns_200_without_body() -> None:
    server, base = _start_test_server()
    try:
        request = Request(f"{base}/", method="HEAD")
        with urlopen(request) as response:
            assert response.status == 200
            assert response.read() == b""
            assert int(response.headers["Content-Length"]) > 0
    finally:
        server.shutdown()
        server.server_close()


def test_api_schedule_v85() -> None:
    server, base = _start_test_server()
    try:
        with patch("vai.server.fetch_atg_schedule", return_value=MOCK_SCHEDULE):
            schedule = _get(f"{base}/api/v1/schedule/v85")
        assert schedule["default_date"] == "2026-07-11"
        assert schedule["dates"] == ["2026-07-11"]
        assert schedule["rounds"][0]["game_id"] == "V85_2026-07-11_31_5"
        assert schedule["rounds"][0]["track"] == "Årjäng"
    finally:
        server.shutdown()
        server.server_close()


def test_api_race_cards_and_generate() -> None:
    server, base = _start_test_server()
    try:
        listing = _get(f"{base}/api/v1/race-cards")
        assert listing["race_cards"]
        card_id = listing["race_cards"][0]["id"]

        card = _get(f"{base}/api/v1/race-cards/{card_id}")
        assert len(card["legs"]) == 8

        pools = {str(leg["leg"]): [] for leg in card["legs"]}
        status, result = _post(
            f"{base}/api/v1/generate/random",
            {"race_card_id": card_id, "pools": pools, "budget": 500, "seed": 42},
        )
        assert status == 200
        assert result["combinations"] == 1000
        assert result["cost_sek"] == 500.0
    finally:
        server.shutdown()
        server.server_close()

def test_api_experts_roster() -> None:
    server, base = _start_test_server()
    try:
        data = _get(f"{base}/api/v1/experts")
        assert data["experts"]
        ids = {e["expert_id"] for e in data["experts"]}
        assert "bjorn-goop" in ids
        assert "referenten" in ids
        assert "fixture" not in ids
        goop = next(e for e in data["experts"] if e["expert_id"] == "bjorn-goop")
        assert goop["display_name"] == "Björn Goop"
        assert "product_name" in goop

        free = _get(f"{base}/api/v1/experts?free=1")
        assert free["experts"]
        assert all(e.get("free") is True for e in free["experts"])

        with_day = _get(f"{base}/api/v1/experts?date=2026-07-18&track=Axevalla&include_fixture=1")
        # fixture tip exists for that day but fixture excluded unless include_fixture
        fixture_listed = [e for e in with_day["experts"] if e["expert_id"] == "fixture"]
        assert len(fixture_listed) == 1
        assert fixture_listed[0]["has_tip"] is True
    finally:
        server.shutdown()
        server.server_close()


def test_api_expert_tips_list_and_generate() -> None:
    server, base = _start_test_server()
    try:
        tips = _get(f"{base}/api/v1/expert-tips?date=2026-07-18&track=Axevalla")
        assert tips["tips"]
        tip_id = tips["tips"][0]["tip_id"]
        assert tip_id == "fixture-axevalla-2026-07-18"
        assert tips["tips"][0]["cost_sek"] == 54.0

        listing = _get(f"{base}/api/v1/race-cards")
        card_ids = [c["id"] for c in listing["race_cards"]]
        card_id = (
            "2026-07-18-axevalla"
            if "2026-07-18-axevalla" in card_ids
            else listing["race_cards"][0]["id"]
        )

        status, result = _post(
            f"{base}/api/v1/generate/expert",
            {"race_card_id": card_id, "tip_id": tip_id},
        )
        assert status == 200
        assert result["combinations"] == 108
        assert result["cost_sek"] == 54.0
        assert result["expert_name"] == "Fixture Expert"
        assert len(result["selections"]) == 8

        detail = _get(f"{base}/api/v1/expert-tips/{tip_id}")
        assert detail["tip"]["tip_id"] == tip_id
        assert detail["tip"]["legs"]["1"] == [1]
    finally:
        server.shutdown()
        server.server_close()


def test_api_expert_tips_save_and_lookup(tmp_path: Path) -> None:
    server, base = _start_test_server()
    original_dir = VaiRequestHandler.expert_tips_dir
    VaiRequestHandler.expert_tips_dir = tmp_path
    try:
        legs = {str(leg): [1] for leg in range(1, 9)}
        status, created = _put(
            f"{base}/api/v1/expert-tips",
            {
                "expert_id": "bjorn-goop",
                "expert_name": "Björn Goop",
                "product_name": "Björnkollen",
                "game": "v85",
                "date": "2026-08-01",
                "track": "Solvalla",
                "legs": legs,
                "source_note": "via UI test",
            },
        )
        assert status == 200
        assert created["ok"] is True
        assert created["tip_id"] == "bjorn-goop-2026-08-01"
        assert (tmp_path / "2026-08-01-solvalla" / "bjorn-goop-2026-08-01.yaml").is_file()

        listed = _get(
            f"{base}/api/v1/expert-tips?date=2026-08-01&track=Solvalla&expert_id=bjorn-goop"
        )
        assert len(listed["tips"]) == 1

        lookup = _get(
            f"{base}/api/v1/expert-tips/lookup"
            "?expert_id=bjorn-goop&date=2026-08-01&track=Solvalla"
        )
        assert lookup["tip"]["legs"]["1"] == [1]
        assert lookup["tip"]["source_note"] == "via UI test"

        legs2 = {str(leg): [2] for leg in range(1, 9)}
        status2, updated = _put(
            f"{base}/api/v1/expert-tips",
            {
                "expert_id": "bjorn-goop",
                "expert_name": "Björn Goop",
                "game": "v85",
                "date": "2026-08-01",
                "track": "Solvalla",
                "legs": legs2,
            },
        )
        assert status2 == 200
        assert updated["tip"]["legs"]["1"] == [2]
        assert len(list(tmp_path.rglob("*.yaml"))) == 1

        bad_status, bad = _put(
            f"{base}/api/v1/expert-tips",
            {
                "expert_id": "x",
                "expert_name": "X",
                "game": "v85",
                "date": "2026-08-01",
                "track": "Solvalla",
                "legs": {str(leg): [1] for leg in range(1, 8)},
            },
        )
        assert bad_status == 400
        assert bad["error"]["code"] == "INVALID_TIP"
    finally:
        VaiRequestHandler.expert_tips_dir = original_dir
        server.shutdown()
        server.server_close()
