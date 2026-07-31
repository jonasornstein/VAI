import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from vai.activity_log import ActivityLogger
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


def _start_test_server(
    *,
    activity_log: Path | None = None,
    trusted_proxy_hops: int = 1,
    trusted_proxies: frozenset[str] | None = None,
) -> tuple[ThreadingHTTPServer, str]:
    root = find_repo_root()
    VaiRequestHandler.repo_root = root
    VaiRequestHandler.mockup_dir = root / "outbox" / "mockups"
    VaiRequestHandler.race_cards_dir = root / "inbox" / "race-cards"
    VaiRequestHandler.expert_tips_dir = root / "inbox" / "expert-tips"
    VaiRequestHandler.activity_logger = ActivityLogger(activity_log) if activity_log else None
    VaiRequestHandler.trusted_proxy_hops = trusted_proxy_hops
    VaiRequestHandler.trusted_proxies = trusted_proxies or frozenset()
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


def _delete(url: str) -> tuple[int, dict]:
    request = Request(url, method="DELETE")
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
        VaiRequestHandler.activity_logger = None


def test_activity_log_records_request_with_xff(tmp_path: Path) -> None:
    log_path = tmp_path / "activity.jsonl"
    server, base = _start_test_server(activity_log=log_path)
    try:
        with patch("vai.server.fetch_atg_schedule", return_value=MOCK_SCHEDULE):
            request = Request(
                f"{base}/api/v1/schedule/v85",
                headers={
                    "X-Forwarded-For": "203.0.113.44",
                    "User-Agent": "VAI-Test/1.0",
                },
            )
            with urlopen(request) as response:
                assert response.status == 200
                json.loads(response.read().decode("utf-8"))
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) >= 1
        event = json.loads(lines[-1])
        assert event["operation"] == "get_schedule_v85"
        assert event["method"] == "GET"
        assert event["path"] == "/api/v1/schedule/v85"
        assert event["status"] == 200
        assert event["outcome"] == "success"
        assert event["client_ip"] == "203.0.113.44"
        assert event["peer_ip"] in ("127.0.0.1", "::1")
        assert event["user_agent"] == "VAI-Test/1.0"
        assert "ts" in event and event["ts"].endswith("Z")
        assert event["event_id"]
        assert "seed" not in event
        assert "body" not in event
    finally:
        server.shutdown()
        server.server_close()
        VaiRequestHandler.activity_logger = None


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
        assert created["combinations"] == 1
        assert created["cost_sek"] == 0.5
        assert created["summary"]["tip_id"] == "bjorn-goop-2026-08-01"
        assert created["summary"]["cost_breakdown"] == "1×1×1×1×1×1×1×1"
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

        del_status, deleted = _delete(
            f"{base}/api/v1/expert-tips/bjorn-goop-2026-08-01"
        )
        assert del_status == 200
        assert deleted["ok"] is True
        assert deleted["tip_id"] == "bjorn-goop-2026-08-01"
        assert not (tmp_path / "2026-08-01-solvalla" / "bjorn-goop-2026-08-01.yaml").is_file()
        listed_after = _get(
            f"{base}/api/v1/expert-tips?date=2026-08-01&track=Solvalla&expert_id=bjorn-goop"
        )
        assert listed_after["tips"] == []

        missing_status, missing = _delete(f"{base}/api/v1/expert-tips/no-such-tip")
        assert missing_status == 404
        assert missing["error"]["code"] == "TIP_NOT_FOUND"
    finally:
        VaiRequestHandler.expert_tips_dir = original_dir
        server.shutdown()
        server.server_close()


def test_api_experts_add_delete_reset(tmp_path: Path) -> None:
    """Mutations use an isolated repo_root so inbox/experts is not polluted."""
    # Point working roster under tmp; keep tips/mockup from real repo for GET annotations
    isolated = tmp_path / "repo"
    (isolated / "inbox" / "experts").mkdir(parents=True)
    (isolated / "pyproject.toml").write_text("[project]\nname='vai-test'\n", encoding="utf-8")

    server, base = _start_test_server()
    original_root = VaiRequestHandler.repo_root
    try:
        VaiRequestHandler.repo_root = isolated

        status, created = _post(
            f"{base}/api/v1/experts",
            {
                "expert_id": "eddie-ostlund",
                "display_name": "Eddie Östlund",
                "outlet": "Travcash",
                "free": True,
            },
        )
        assert status == 201, created
        assert created["ok"] is True
        assert created["expert"]["expert_id"] == "eddie-ostlund"
        assert (isolated / "inbox" / "experts" / "roster.yaml").is_file()

        listed = _get(f"{base}/api/v1/experts")
        ids = {e["expert_id"] for e in listed["experts"]}
        assert "eddie-ostlund" in ids
        assert "bjorn-goop" in ids

        conflict_status, conflict = _post(
            f"{base}/api/v1/experts",
            {"expert_id": "eddie-ostlund", "display_name": "Dup"},
        )
        assert conflict_status == 409
        assert conflict["error"]["code"] == "EXPERT_EXISTS"

        put_status, put_body = _put(
            f"{base}/api/v1/experts/eddie-ostlund",
            {"notes": "Travcash free tipster", "free": True},
        )
        assert put_status == 200
        assert put_body["expert"]["notes"] == "Travcash free tipster"

        # DELETE soft-hides (visible=false); row stays on roster
        del_status, deleted = _delete(f"{base}/api/v1/experts/eddie-ostlund")
        assert del_status == 200
        assert deleted["expert_id"] == "eddie-ostlund"
        assert deleted["expert"]["visible"] is False
        listed2 = _get(f"{base}/api/v1/experts")
        eddie = next(e for e in listed2["experts"] if e["expert_id"] == "eddie-ostlund")
        assert eddie["visible"] is False
        visible_only = _get(f"{base}/api/v1/experts?visible=1")
        assert all(e["expert_id"] != "eddie-ostlund" for e in visible_only["experts"])

        put_vis, put_vis_body = _put(
            f"{base}/api/v1/experts/eddie-ostlund",
            {"visible": True},
        )
        assert put_vis == 200
        assert put_vis_body["expert"]["visible"] is True

        # Soft-hide a default expert then reset (customs dropped; defaults restored visible)
        del2_status, del2_body = _delete(f"{base}/api/v1/experts/leboff")
        assert del2_status == 200
        assert del2_body["expert"]["visible"] is False
        leboff = next(
            e for e in _get(f"{base}/api/v1/experts")["experts"] if e["expert_id"] == "leboff"
        )
        assert leboff["visible"] is False

        reset_status, reset_body = _post(f"{base}/api/v1/experts/reset", {})
        assert reset_status == 200
        assert reset_body["restored"] is True
        reset_ids = {e["expert_id"] for e in reset_body["experts"]}
        assert "leboff" in reset_ids
        assert "eddie-ostlund" not in reset_ids
        assert "fixture" not in reset_ids
        leboff_restored = next(
            e for e in reset_body["experts"] if e["expert_id"] == "leboff"
        )
        assert leboff_restored.get("visible", True) is True

        fixture_status, fixture_err = _delete(f"{base}/api/v1/experts/fixture")
        assert fixture_status == 400
        assert fixture_err["error"]["code"] == "FORBIDDEN_ID"

        # Counts on list endpoint
        listed_counts = _get(f"{base}/api/v1/experts")
        assert "counts" in listed_counts
        assert listed_counts["counts"]["total"] == len(listed_counts["experts"])
        assert listed_counts["counts"]["visible"] == sum(
            1 for e in listed_counts["experts"] if e.get("visible", True)
        )
        assert "with_tip" in listed_counts["counts"]

        # Bulk visibility + reorder
        hide_status, hide_body = _put(
            f"{base}/api/v1/experts/visibility",
            {"visible": False},
        )
        assert hide_status == 200, hide_body
        assert hide_body["ok"] is True
        assert hide_body["updated"] >= 1
        assert all(e["visible"] is False for e in hide_body["experts"])
        visible_none = _get(f"{base}/api/v1/experts?visible=1")
        assert visible_none["experts"] == []
        assert visible_none["counts"]["visible"] == 0
        assert visible_none["counts"]["total"] == hide_body["updated"] or visible_none[
            "counts"
        ]["total"] == len(hide_body["experts"])

        show_status, show_body = _put(
            f"{base}/api/v1/experts/visibility",
            {"visible": True},
        )
        assert show_status == 200, show_body
        assert all(e["visible"] is True for e in show_body["experts"])

        order_ids = [e["expert_id"] for e in show_body["experts"]]
        reversed_ids = list(reversed(order_ids))
        reorder_status, reorder_body = _put(
            f"{base}/api/v1/experts/reorder",
            {"order": reversed_ids},
        )
        assert reorder_status == 200, reorder_body
        assert [e["expert_id"] for e in reorder_body["experts"]] == reversed_ids
        listed_after = _get(f"{base}/api/v1/experts")
        assert [e["expert_id"] for e in listed_after["experts"]] == reversed_ids

        bad_reorder_status, bad_reorder = _put(
            f"{base}/api/v1/experts/reorder",
            {"order": reversed_ids[:-1]},
        )
        assert bad_reorder_status == 400
        assert bad_reorder["error"]["code"] == "INVALID_EXPERT"
    finally:
        VaiRequestHandler.repo_root = original_root
        server.shutdown()
        server.server_close()
