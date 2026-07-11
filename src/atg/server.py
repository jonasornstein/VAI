"""Local HTTP server — mockup + random API (v1.1.2)."""

from __future__ import annotations

import json
import mimetypes
import re
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from atg.atg_fetch import AtgFetchError
from atg.atg_race_card import fetch_atg_race_card_bundle, is_atg_game_id
from atg.hit_summary import compute_hit_summary
from atg.io.race_card_json import list_race_card_ids, load_race_card_by_id, race_card_to_dict
from atg.models.proposal import RandomError, RandomResult
from atg.schedule import fetch_atg_schedule, schedule_to_dict
from atg.strategies.random import generate_random_v1

CARD_ID_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+$")
ATG_GAME_ID_PATTERN = re.compile(r"^V85_\d{4}-\d{2}-\d{2}_\d+_\d+$")
DEFAULT_PORT = 8765


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").is_file() and (parent / "inbox").is_dir():
            return parent
    raise RuntimeError("Could not locate ATG repo root")


class AtgRequestHandler(BaseHTTPRequestHandler):
    repo_root: Path = find_repo_root()
    mockup_dir: Path = repo_root / "outbox" / "mockups"
    race_cards_dir: Path = repo_root / "inbox" / "race-cards"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/" or path == "/index.html":
            self._serve_file(self.mockup_dir / "v85-proposal-ux-mockup-atg.html")
            return
        if path == "/api/v1/schedule/v85":
            self._handle_get_schedule_v85()
            return
        if path == "/api/v1/race-cards":
            self._send_json(HTTPStatus.OK, {"race_cards": list_race_card_ids(self.race_cards_dir)})
            return
        if path.startswith("/api/v1/race-cards/"):
            card_id = path.removeprefix("/api/v1/race-cards/").strip("/")
            self._handle_get_race_card(card_id)
            return
        if path.startswith("/mockup/"):
            rel = path.removeprefix("/mockup/").lstrip("/")
            target = (self.mockup_dir / rel).resolve()
            if not str(target).startswith(str(self.mockup_dir.resolve())):
                self._send_json(HTTPStatus.FORBIDDEN, {"error": {"code": "FORBIDDEN", "message": "Invalid path"}})
                return
            if target.is_file():
                self._serve_file(target)
                return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": {"code": "NOT_FOUND", "message": path}})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/v1/generate/random":
            self._handle_generate_random()
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": {"code": "NOT_FOUND", "message": path}})

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._set_cors_headers()
        self.end_headers()

    def _handle_get_schedule_v85(self) -> None:
        try:
            schedule = fetch_atg_schedule()
        except AtgFetchError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {"error": {"code": "ATG_UNAVAILABLE", "message": str(exc)}},
            )
            return
        self._send_json(HTTPStatus.OK, schedule_to_dict(schedule))

    def _handle_get_race_card(self, card_id: str) -> None:
        if is_atg_game_id(card_id):
            if not ATG_GAME_ID_PATTERN.match(card_id):
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": {"code": "INVALID_ID", "message": card_id}})
                return
            try:
                card, leg_distributions = fetch_atg_race_card_bundle(card_id)
            except AtgFetchError as exc:
                self._send_json(
                    HTTPStatus.BAD_GATEWAY,
                    {"error": {"code": "ATG_UNAVAILABLE", "message": str(exc)}},
                )
                return
            except ValueError as exc:
                self._send_json(
                    HTTPStatus.BAD_GATEWAY,
                    {"error": {"code": "ATG_PARSE_ERROR", "message": str(exc)}},
                )
                return
            payload = race_card_to_dict(card)
            payload["id"] = card_id
            if leg_distributions:
                payload["leg_distributions"] = {
                    str(leg): {str(horse): value for horse, value in horses.items()}
                    for leg, horses in leg_distributions.items()
                }
            self._send_json(HTTPStatus.OK, payload)
            return

        if not CARD_ID_PATTERN.match(card_id):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": {"code": "INVALID_ID", "message": card_id}})
            return
        try:
            card = load_race_card_by_id(self.race_cards_dir, card_id)
        except FileNotFoundError:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": {"code": "NOT_FOUND", "message": card_id}})
            return
        payload = race_card_to_dict(card)
        payload["id"] = card_id
        self._send_json(HTTPStatus.OK, payload)

    def _load_race_card_bundle(self, card_id: str) -> tuple:
        if is_atg_game_id(card_id):
            return fetch_atg_race_card_bundle(card_id)
        return load_race_card_by_id(self.race_cards_dir, card_id), None

    def _handle_generate_random(self) -> None:
        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": {"code": "INVALID_JSON", "message": "Bad JSON body"}})
            return

        card_id = body.get("race_card_id")
        if not isinstance(card_id, str):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": {"code": "MISSING_FIELD", "message": "race_card_id"}})
            return

        try:
            card, leg_distributions = self._load_race_card_bundle(card_id)
        except FileNotFoundError:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": {"code": "NOT_FOUND", "message": card_id}})
            return
        except AtgFetchError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {"error": {"code": "ATG_UNAVAILABLE", "message": str(exc)}},
            )
            return
        except ValueError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {"error": {"code": "ATG_PARSE_ERROR", "message": str(exc)}},
            )
            return

        pools_raw = body.get("pools")
        if not isinstance(pools_raw, dict):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": {"code": "MISSING_FIELD", "message": "pools"}})
            return

        try:
            pools = {int(k): [int(h) for h in v] for k, v in pools_raw.items()}
        except (TypeError, ValueError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": {"code": "INVALID_POOLS", "message": "pools format"}})
            return

        try:
            budget = float(body.get("budget", 500))
        except (TypeError, ValueError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": {"code": "INVALID_BUDGET", "message": "budget"}})
            return

        seed = body.get("seed")
        if seed is not None:
            try:
                seed = int(seed)
            except (TypeError, ValueError):
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": {"code": "INVALID_SEED", "message": "seed"}})
                return

        frozen_legs = frozenset()
        frozen_raw = body.get("frozen_legs")
        if frozen_raw is not None:
            if not isinstance(frozen_raw, list):
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": {"code": "INVALID_FROZEN_LEGS", "message": "frozen_legs must be a list"}},
                )
                return
            try:
                frozen_legs = frozenset(int(leg) for leg in frozen_raw)
            except (TypeError, ValueError):
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": {"code": "INVALID_FROZEN_LEGS", "message": "frozen_legs format"}},
                )
                return

        outcome = generate_random_v1(card, pools, budget, seed=seed, frozen_legs=frozen_legs)
        if isinstance(outcome, RandomError):
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {k: v for k, v in asdict(outcome).items() if v is not None}},
            )
            return

        assert isinstance(outcome, RandomResult)
        response: dict[str, Any] = {
            "selections": {str(k): v for k, v in outcome.selections.items()},
            "combinations": outcome.combinations,
            "cost_sek": outcome.cost_sek,
            "cost_breakdown": outcome.cost_breakdown,
            "shrink_steps_used": outcome.shrink_steps_used,
            "seed": outcome.manifest.seed,
        }
        hit_summary = compute_hit_summary(outcome.selections, leg_distributions)
        if hit_summary is not None:
            response["hit_summary"] = hit_summary
        self._send_json(HTTPStatus.OK, response)

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise json.JSONDecodeError("Expected object", raw.decode("utf-8"), 0)
        return data

    def _serve_file(self, path: Path) -> None:
        if not path.is_file():
            self._send_json(HTTPStatus.NOT_FOUND, {"error": {"code": "NOT_FOUND", "message": str(path)}})
            return
        content = path.read_bytes()
        mime, _ = mimetypes.guess_type(path.name)
        self.send_response(HTTPStatus.OK)
        self._set_cors_headers()
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _set_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


def serve(*, host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> None:
    root = find_repo_root()
    AtgRequestHandler.repo_root = root
    AtgRequestHandler.mockup_dir = root / "outbox" / "mockups"
    AtgRequestHandler.race_cards_dir = root / "inbox" / "race-cards"
    server = ThreadingHTTPServer((host, port), AtgRequestHandler)
    print(f"ATG local UI: http://{host}:{port}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()