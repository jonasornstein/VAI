"""Local HTTP server — mockup + random/expert API (v1.3.0)."""

from __future__ import annotations

import json
import mimetypes
import re
import sys
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from vai.atg_fetch import AtgFetchError
from vai.atg_race_card import fetch_atg_race_card_bundle, is_atg_game_id
from vai.hit_summary import compute_hit_summary
from vai.io.expert_tips import list_expert_tips
from vai.io.experts_roster import list_experts
from vai.io.race_card_json import list_race_card_ids, load_race_card_by_id, race_card_to_dict
from vai.models.expert_tip import ExpertError, ExpertResult
from vai.models.proposal import RandomError, RandomResult
from vai.schedule import fetch_atg_schedule, schedule_to_dict
from vai.strategies.expert import generate_expert_v1
from vai.strategies.random import generate_random_v1

CARD_ID_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+$")
ATG_GAME_ID_PATTERN = re.compile(r"^V85_\d{4}-\d{2}-\d{2}_\d+_\d+$")
# Dev default: avoid clash with production vai.service on 8765 (see deploy/vai.service).
DEFAULT_PORT = 8766


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").is_file() and (parent / "inbox").is_dir():
            return parent
    cwd = Path.cwd()
    if (cwd / "pyproject.toml").is_file() and (cwd / "inbox").is_dir():
        return cwd
    raise RuntimeError("Could not locate VAI repo root")


class VaiRequestHandler(BaseHTTPRequestHandler):
    repo_root: Path = find_repo_root()
    mockup_dir: Path = repo_root / "outbox" / "mockups"
    race_cards_dir: Path = repo_root / "inbox" / "race-cards"
    expert_tips_dir: Path = repo_root / "inbox" / "expert-tips"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_HEAD(self) -> None:
        """Support health checks (curl -I) without a response body."""
        self._head_only = True
        try:
            self.do_GET()
        finally:
            self._head_only = False

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
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
        if path == "/api/v1/expert-tips":
            self._handle_list_expert_tips(parsed.query)
            return
        if path == "/api/v1/experts":
            self._handle_list_experts(parsed.query)
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
        if path == "/api/v1/generate/expert":
            self._handle_generate_expert()
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
                card, leg_distributions, leg_odds = fetch_atg_race_card_bundle(card_id)
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
            if leg_odds:
                payload["leg_odds"] = {
                    str(leg): {str(horse): value for horse, value in horses.items()}
                    for leg, horses in leg_odds.items()
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
        return load_race_card_by_id(self.race_cards_dir, card_id), None, None

    def _handle_list_experts(self, query: str) -> None:
        params = parse_qs(query)
        free_only = (params.get("free") or ["0"])[0] in ("1", "true", "yes")
        include_fixture = (params.get("include_fixture") or ["0"])[0] in ("1", "true", "yes")
        experts = list_experts(free_only=free_only, exclude_fixture=not include_fixture)
        # Annotate how many tips exist for optional date/track filter
        date = (params.get("date") or [None])[0]
        track = (params.get("track") or [None])[0]
        tips = list_expert_tips(self.expert_tips_dir, date=date, track=track)
        tip_counts: dict[str, int] = {}
        for tip in tips:
            tip_counts[tip.expert_id] = tip_counts.get(tip.expert_id, 0) + 1
        payload = {
            "experts": [
                {
                    **e.to_dict(),
                    "tips_for_filter": tip_counts.get(e.expert_id, 0),
                    "has_tip": tip_counts.get(e.expert_id, 0) > 0,
                }
                for e in experts
            ]
        }
        self._send_json(HTTPStatus.OK, payload)

    def _handle_list_expert_tips(self, query: str) -> None:
        params = parse_qs(query)
        date = (params.get("date") or [None])[0]
        track = (params.get("track") or [None])[0]
        tips = list_expert_tips(self.expert_tips_dir, date=date, track=track)
        payload = {
            "tips": [
                {
                    "tip_id": t.tip_id,
                    "expert_id": t.expert_id,
                    "expert_name": t.expert_name,
                    "product_name": t.product_name,
                    "date": t.date,
                    "track": t.track,
                    "combinations": t.combinations,
                    "cost_sek": t.cost_sek,
                    "cost_breakdown": t.cost_breakdown,
                    "source_url": t.source_url,
                    "status": t.status,
                }
                for t in tips
            ]
        }
        self._send_json(HTTPStatus.OK, payload)

    def _handle_generate_expert(self) -> None:
        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": {"code": "INVALID_JSON", "message": "Bad JSON body"}})
            return

        tip_id = body.get("tip_id")
        if not isinstance(tip_id, str) or not tip_id.strip():
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": {"code": "MISSING_FIELD", "message": "tip_id"}})
            return

        card = None
        leg_distributions = None
        card_id = body.get("race_card_id")
        if card_id is not None:
            if not isinstance(card_id, str):
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": {"code": "INVALID_FIELD", "message": "race_card_id"}},
                )
                return
            try:
                card, leg_distributions, _leg_odds = self._load_race_card_bundle(card_id)
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

        overrides = None
        overrides_raw = body.get("overrides")
        if overrides_raw is not None:
            if not isinstance(overrides_raw, dict):
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": {"code": "INVALID_OVERRIDES", "message": "overrides must be an object"}},
                )
                return
            try:
                overrides = {int(k): [int(h) for h in v] for k, v in overrides_raw.items()}
            except (TypeError, ValueError):
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": {"code": "INVALID_OVERRIDES", "message": "overrides format"}},
                )
                return

        outcome = generate_expert_v1(
            tip_id.strip(),
            race_card=card,
            overrides=overrides,
            tips_dir=self.expert_tips_dir,
        )
        if isinstance(outcome, ExpertError):
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {k: v for k, v in asdict(outcome).items() if v is not None}},
            )
            return

        assert isinstance(outcome, ExpertResult)
        response: dict[str, Any] = {
            "selections": {str(k): v for k, v in outcome.selections.items()},
            "combinations": outcome.combinations,
            "cost_sek": outcome.cost_sek,
            "cost_breakdown": outcome.cost_breakdown,
            "tip_id": outcome.manifest.tip_id,
            "expert_id": outcome.manifest.expert_id,
            "expert_name": outcome.manifest.expert_name,
            "product_name": outcome.manifest.product_name,
            "source_url": outcome.manifest.source_url,
            "source_note": outcome.manifest.source_note,
            "overridden_legs": list(outcome.manifest.overridden_legs),
            "rationale": outcome.tip.rationale,
        }
        hit_summary = compute_hit_summary(outcome.selections, leg_distributions)
        if hit_summary is not None:
            response["hit_summary"] = hit_summary
        self._send_json(HTTPStatus.OK, response)

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
            card, leg_distributions, _leg_odds = self._load_race_card_bundle(card_id)
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
        if not getattr(self, "_head_only", False):
            self.wfile.write(content)

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not getattr(self, "_head_only", False):
            self.wfile.write(body)

    def _set_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


def serve(*, host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> None:
    root = find_repo_root()
    VaiRequestHandler.repo_root = root
    VaiRequestHandler.mockup_dir = root / "outbox" / "mockups"
    VaiRequestHandler.race_cards_dir = root / "inbox" / "race-cards"
    VaiRequestHandler.expert_tips_dir = root / "inbox" / "expert-tips"
    try:
        server = ThreadingHTTPServer((host, port), VaiRequestHandler)
    except OSError as exc:
        print(f"Could not bind {host}:{port}: {exc}", file=sys.stderr)
        if port == 8765:
            print(
                "Port 8765 is usually production (vai.service). "
                f"For the dev clone use: python -m vai serve --port {DEFAULT_PORT}",
                file=sys.stderr,
            )
        raise SystemExit(1) from exc
    print(f"VAI local UI: http://{host}:{port}/")
    print(f"  Experts API: http://{host}:{port}/api/v1/experts")
    if port != 8765:
        print("  Production (if deployed): https://vai.ornstein.work/  (port 8765)")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()