import json
import threading
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from atg.schedule import V85Round, V85Schedule
from atg.server import AtgRequestHandler, find_repo_root

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
    AtgRequestHandler.repo_root = root
    AtgRequestHandler.mockup_dir = root / "outbox" / "mockups"
    AtgRequestHandler.race_cards_dir = root / "inbox" / "race-cards"
    server = ThreadingHTTPServer(("127.0.0.1", 0), AtgRequestHandler)
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


def test_api_schedule_v85() -> None:
    server, base = _start_test_server()
    try:
        with patch("atg.server.fetch_atg_schedule", return_value=MOCK_SCHEDULE):
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