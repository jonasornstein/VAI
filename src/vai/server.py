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

from vai.activity_log import ActivityLogger
from vai.atg_fetch import AtgFetchError
from vai.atg_race_card import fetch_atg_race_card_bundle, is_atg_game_id
from vai.hit_summary import compute_hit_summary
from vai.io.betslip import (
    BetslipValidationError,
    default_betslips_dir,
    delete_betslip_file,
    delete_betslip_files,
    list_betslips,
    load_betslip_file,
    parse_betslip_yaml,
    save_betslip_file,
    validate_betslip_payload,
)
from vai.io.expert_tips import (
    ExpertTipValidationError,
    delete_expert_tip,
    find_expert_tip,
    find_expert_tip_for,
    list_expert_tips,
    save_expert_tip,
    tip_to_dict,
    tip_to_summary,
)
from vai.io.experts_roster import (
    ExpertRosterError,
    add_expert,
    delete_expert,
    list_experts,
    reorder_experts,
    reset_experts_roster,
    set_all_visible,
    update_expert,
)
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
    betslips_dir: Path = repo_root / "betslips"
    activity_logger: ActivityLogger | None = None
    trusted_proxy_hops: int = 1
    trusted_proxies: frozenset[str] = frozenset()

    def log_message(self, format: str, *args: Any) -> None:
        # Structured activity log replaces default access lines.
        return

    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        """Emit one activity event per completed response (timestamp, IP, operation)."""
        logger = type(self).activity_logger
        if logger is None or not logger.enabled:
            return
        try:
            status = int(code)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            status = 0
        peer_ip = None
        if self.client_address:
            peer_ip = self.client_address[0]
        path = urlparse(self.path).path if self.path else "/"
        logger.emit_from_request(
            method=self.command or "GET",
            path=path,
            status=status,
            peer_ip=peer_ip,
            headers=self.headers,
            trusted_proxy_hops=type(self).trusted_proxy_hops,
            trusted_proxies=type(self).trusted_proxies,
        )

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
        # Activity stats viewer — always from repo tree (same file git deploy updates).
        if path == "/vai-stats.html":
            self._serve_file(
                self.repo_root / "vai-stats.html",
                content_type="text/html; charset=utf-8",
                cache_control="no-cache",
            )
            return
        if path == "/activity.jsonl":
            self._serve_activity_jsonl()
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
        if path.startswith("/api/v1/expert-tips/"):
            tip_id = path.removeprefix("/api/v1/expert-tips/").strip("/")
            self._handle_get_expert_tip(tip_id, parsed.query)
            return
        if path == "/api/v1/experts":
            self._handle_list_experts(parsed.query)
            return
        if path.startswith("/api/v1/experts/"):
            expert_id = path.removeprefix("/api/v1/experts/").strip("/")
            if expert_id and expert_id not in ("reset", "visibility", "reorder"):
                self._handle_get_expert(expert_id)
                return
        if path == "/api/v1/betslips":
            self._handle_list_betslips(parsed.query)
            return
        if path.startswith("/api/v1/betslips/"):
            name = path.removeprefix("/api/v1/betslips/").strip("/")
            if name and name not in ("parse", "delete"):
                self._handle_get_betslip(name)
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
        if path == "/api/v1/betslips/parse":
            self._handle_parse_betslip()
            return
        if path == "/api/v1/betslips/delete":
            self._handle_delete_betslips_batch()
            return
        if path == "/api/v1/betslips":
            self._handle_save_betslip()
            return
        if path == "/api/v1/expert-tips":
            self._handle_save_expert_tip()
            return
        if path == "/api/v1/experts/reset":
            self._handle_reset_experts()
            return
        if path == "/api/v1/experts":
            self._handle_add_expert()
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": {"code": "NOT_FOUND", "message": path}})

    def do_PUT(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/v1/expert-tips":
            self._handle_save_expert_tip()
            return
        if path == "/api/v1/experts/visibility":
            self._handle_set_all_experts_visible()
            return
        if path == "/api/v1/experts/reorder":
            self._handle_reorder_experts()
            return
        if path.startswith("/api/v1/experts/"):
            expert_id = path.removeprefix("/api/v1/experts/").strip("/")
            if expert_id and expert_id not in ("reset", "visibility", "reorder"):
                self._handle_update_expert(expert_id)
                return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": {"code": "NOT_FOUND", "message": path}})

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/v1/expert-tips/"):
            tip_id = path.removeprefix("/api/v1/expert-tips/").strip("/")
            self._handle_delete_expert_tip(tip_id, parsed.query)
            return
        if path == "/api/v1/expert-tips":
            self._handle_delete_expert_tip(None, parsed.query)
            return
        if path.startswith("/api/v1/experts/"):
            expert_id = path.removeprefix("/api/v1/experts/").strip("/")
            if expert_id and expert_id != "reset":
                self._handle_delete_expert(expert_id)
                return
        if path.startswith("/api/v1/betslips/"):
            name = path.removeprefix("/api/v1/betslips/").strip("/")
            if name and name not in ("parse", "delete"):
                self._handle_delete_betslip(name)
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
        # Default: return all (manage UI needs hidden experts to re-show).
        # visible=1 / visible_only=1 → only visible; visible=0 → only hidden.
        visible_param = (params.get("visible") or params.get("visible_only") or [None])[0]
        visible_filter: bool | None = None
        if visible_param is not None:
            v = str(visible_param).lower()
            if v in ("1", "true", "yes"):
                visible_filter = True
            elif v in ("0", "false", "no"):
                visible_filter = False
        # Full roster (excl. fixture unless include_fixture) for counts; free filter
        # does not shrink total — "N synliga av M" uses full roster size.
        all_for_counts = list_experts(
            repo_root=self.repo_root,
            free_only=False,
            exclude_fixture=not include_fixture,
            visible_only=False,
        )
        experts = list_experts(
            repo_root=self.repo_root,
            free_only=free_only,
            exclude_fixture=not include_fixture,
            visible_only=visible_filter is True,
        )
        if visible_filter is False:
            experts = [e for e in experts if e.visible is False]
        # Annotate how many tips exist for optional date/track filter
        date = (params.get("date") or [None])[0]
        track = (params.get("track") or [None])[0]
        tips = list_expert_tips(self.expert_tips_dir, date=date, track=track)
        tip_counts: dict[str, int] = {}
        for tip in tips:
            tip_counts[tip.expert_id] = tip_counts.get(tip.expert_id, 0) + 1
        expert_payloads = [
            {
                **e.to_dict(),
                "tips_for_filter": tip_counts.get(e.expert_id, 0),
                "has_tip": tip_counts.get(e.expert_id, 0) > 0,
            }
            for e in experts
        ]
        payload = {
            "experts": expert_payloads,
            "counts": {
                "total": len(all_for_counts),
                "visible": sum(1 for e in all_for_counts if e.visible is True),
                "with_tip": sum(1 for e in expert_payloads if e["has_tip"]),
            },
        }
        self._send_json(HTTPStatus.OK, payload)

    def _handle_get_expert(self, expert_id: str) -> None:
        if not CARD_ID_PATTERN.match(expert_id):
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": "INVALID_ID", "message": expert_id}},
            )
            return
        experts = list_experts(repo_root=self.repo_root, exclude_fixture=False)
        found = next((e for e in experts if e.expert_id == expert_id), None)
        if found is None:
            self._send_json(
                HTTPStatus.NOT_FOUND,
                {"error": {"code": "EXPERT_NOT_FOUND", "message": expert_id}},
            )
            return
        self._send_json(HTTPStatus.OK, {"expert": found.to_dict()})

    def _handle_add_expert(self) -> None:
        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": "INVALID_JSON", "message": "Bad JSON body"}},
            )
            return
        try:
            entry = add_expert(body, repo_root=self.repo_root)
        except ExpertRosterError as exc:
            status = HTTPStatus.BAD_REQUEST
            if exc.code == "EXPERT_EXISTS":
                status = HTTPStatus.CONFLICT
            elif exc.code == "FORBIDDEN_ID":
                status = HTTPStatus.BAD_REQUEST
            self._send_json(status, {"error": {"code": exc.code, "message": str(exc)}})
            return
        except OSError as exc:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": {"code": "WRITE_FAILED", "message": str(exc)}},
            )
            return
        self._send_json(HTTPStatus.CREATED, {"ok": True, "expert": entry.to_dict()})

    def _handle_update_expert(self, expert_id: str) -> None:
        if not CARD_ID_PATTERN.match(expert_id):
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": "INVALID_ID", "message": expert_id}},
            )
            return
        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": "INVALID_JSON", "message": "Bad JSON body"}},
            )
            return
        try:
            entry = update_expert(expert_id, body, repo_root=self.repo_root)
        except ExpertRosterError as exc:
            status = HTTPStatus.BAD_REQUEST
            if exc.code == "EXPERT_NOT_FOUND":
                status = HTTPStatus.NOT_FOUND
            self._send_json(status, {"error": {"code": exc.code, "message": str(exc)}})
            return
        except OSError as exc:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": {"code": "WRITE_FAILED", "message": str(exc)}},
            )
            return
        self._send_json(HTTPStatus.OK, {"ok": True, "expert": entry.to_dict()})

    def _handle_delete_expert(self, expert_id: str) -> None:
        if not CARD_ID_PATTERN.match(expert_id):
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": "INVALID_ID", "message": expert_id}},
            )
            return
        try:
            deleted = delete_expert(expert_id, repo_root=self.repo_root)
        except ExpertRosterError as exc:
            status = HTTPStatus.BAD_REQUEST
            if exc.code == "EXPERT_NOT_FOUND":
                status = HTTPStatus.NOT_FOUND
            self._send_json(status, {"error": {"code": exc.code, "message": str(exc)}})
            return
        except OSError as exc:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": {"code": "WRITE_FAILED", "message": str(exc)}},
            )
            return
        self._send_json(
            HTTPStatus.OK,
            {"ok": True, "expert_id": deleted.expert_id, "expert": deleted.to_dict()},
        )

    def _handle_set_all_experts_visible(self) -> None:
        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": "INVALID_JSON", "message": "Bad JSON body"}},
            )
            return
        if "visible" not in body:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {
                    "error": {
                        "code": "INVALID_EXPERT",
                        "message": "visible (bool) is required",
                    }
                },
            )
            return
        visible = body.get("visible")
        if not isinstance(visible, bool):
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {
                    "error": {
                        "code": "INVALID_EXPERT",
                        "message": "visible must be a boolean",
                    }
                },
            )
            return
        try:
            entries, updated = set_all_visible(visible, repo_root=self.repo_root)
        except ExpertRosterError as exc:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": exc.code, "message": str(exc)}},
            )
            return
        except OSError as exc:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": {"code": "WRITE_FAILED", "message": str(exc)}},
            )
            return
        self._send_json(
            HTTPStatus.OK,
            {
                "ok": True,
                "updated": updated,
                "visible": visible,
                "experts": [e.to_dict() for e in entries],
            },
        )

    def _handle_reorder_experts(self) -> None:
        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": "INVALID_JSON", "message": "Bad JSON body"}},
            )
            return
        order = body.get("order")
        if not isinstance(order, list):
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {
                    "error": {
                        "code": "INVALID_EXPERT",
                        "message": "order must be a list of expert_id strings",
                    }
                },
            )
            return
        try:
            entries = reorder_experts(order, repo_root=self.repo_root)
        except ExpertRosterError as exc:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": exc.code, "message": str(exc)}},
            )
            return
        except OSError as exc:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": {"code": "WRITE_FAILED", "message": str(exc)}},
            )
            return
        self._send_json(
            HTTPStatus.OK,
            {"ok": True, "experts": [e.to_dict() for e in entries]},
        )

    def _handle_reset_experts(self) -> None:
        try:
            entries = reset_experts_roster(repo_root=self.repo_root)
        except OSError as exc:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": {"code": "WRITE_FAILED", "message": str(exc)}},
            )
            return
        # Match list shape without tip annotations
        self._send_json(
            HTTPStatus.OK,
            {
                "ok": True,
                "restored": True,
                "experts": [e.to_dict() for e in entries if e.expert_id != "fixture"],
            },
        )

    def _handle_list_expert_tips(self, query: str) -> None:
        params = parse_qs(query)
        date = (params.get("date") or [None])[0]
        track = (params.get("track") or [None])[0]
        expert_id = (params.get("expert_id") or [None])[0]
        tips = list_expert_tips(
            self.expert_tips_dir,
            date=date,
            track=track,
            expert_id=expert_id,
        )
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

    def _handle_get_expert_tip(self, tip_id: str, query: str) -> None:
        """Full tip with legs. tip_id may be literal id, or use query expert_id+date+track via tip_id='lookup'."""
        params = parse_qs(query)
        if tip_id == "lookup" or tip_id == "_lookup":
            expert_id = (params.get("expert_id") or [None])[0]
            date = (params.get("date") or [None])[0]
            track = (params.get("track") or [None])[0]
            if not expert_id or not date or not track:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {
                        "error": {
                            "code": "MISSING_FIELD",
                            "message": "expert_id, date, and track required for lookup",
                        }
                    },
                )
                return
            tip = find_expert_tip_for(
                self.expert_tips_dir,
                expert_id=expert_id,
                date=date,
                track=track,
            )
            if tip is None:
                self._send_json(
                    HTTPStatus.NOT_FOUND,
                    {"error": {"code": "TIP_NOT_FOUND", "message": "No tip for expert/date/track"}},
                )
                return
            self._send_json(HTTPStatus.OK, {"tip": tip_to_dict(tip)})
            return

        if not tip_id or not CARD_ID_PATTERN.match(tip_id):
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": "INVALID_ID", "message": tip_id}},
            )
            return
        try:
            tip = find_expert_tip(self.expert_tips_dir, tip_id)
        except ExpertTipValidationError as exc:
            status = HTTPStatus.NOT_FOUND if exc.code == "TIP_NOT_FOUND" else HTTPStatus.BAD_REQUEST
            self._send_json(status, {"error": {"code": exc.code, "message": str(exc)}})
            return
        self._send_json(HTTPStatus.OK, {"tip": tip_to_dict(tip)})

    def _handle_save_expert_tip(self) -> None:
        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": "INVALID_JSON", "message": "Bad JSON body"}},
            )
            return

        # Normalize legs keys to int-friendly form for parser
        legs_raw = body.get("legs")
        if isinstance(legs_raw, dict):
            try:
                body = {
                    **body,
                    "legs": {int(k): [int(h) for h in v] for k, v in legs_raw.items()},
                }
            except (TypeError, ValueError):
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": {"code": "INVALID_TIP", "message": "legs format invalid"}},
                )
                return

        try:
            tip = save_expert_tip(self.expert_tips_dir, body)
        except ExpertTipValidationError as exc:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": exc.code, "message": str(exc)}},
            )
            return
        except OSError as exc:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": {"code": "WRITE_FAILED", "message": str(exc)}},
            )
            return

        rel_path = None
        if tip.path:
            try:
                rel_path = str(Path(tip.path).resolve().relative_to(self.repo_root.resolve()))
            except ValueError:
                rel_path = tip.path

        summary = tip_to_summary(tip)
        self._send_json(
            HTTPStatus.OK,
            {
                "ok": True,
                "tip_id": tip.tip_id,
                "path": rel_path,
                "tip": tip_to_dict(tip),
                "combinations": summary.combinations,
                "cost_sek": summary.cost_sek,
                "cost_breakdown": summary.cost_breakdown,
                "summary": {
                    "tip_id": summary.tip_id,
                    "expert_id": summary.expert_id,
                    "expert_name": summary.expert_name,
                    "product_name": summary.product_name,
                    "date": summary.date,
                    "track": summary.track,
                    "combinations": summary.combinations,
                    "cost_sek": summary.cost_sek,
                    "cost_breakdown": summary.cost_breakdown,
                    "source_url": summary.source_url,
                    "status": summary.status,
                },
            },
        )

    def _handle_delete_expert_tip(self, tip_id: str | None, query: str) -> None:
        params = parse_qs(query)
        expert_id = (params.get("expert_id") or [None])[0]
        date = (params.get("date") or [None])[0]
        track = (params.get("track") or [None])[0]
        # Path segment may be a real tip_id, or empty when using query only
        if tip_id in ("", "lookup", "_lookup"):
            tip_id = None
        try:
            deleted = delete_expert_tip(
                self.expert_tips_dir,
                tip_id=tip_id,
                expert_id=expert_id,
                date=date,
                track=track,
            )
        except ExpertTipValidationError as exc:
            status = HTTPStatus.NOT_FOUND if exc.code == "TIP_NOT_FOUND" else HTTPStatus.BAD_REQUEST
            if exc.code == "FORBIDDEN":
                status = HTTPStatus.FORBIDDEN
            self._send_json(status, {"error": {"code": exc.code, "message": str(exc)}})
            return
        except OSError as exc:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": {"code": "DELETE_FAILED", "message": str(exc)}},
            )
            return
        self._send_json(
            HTTPStatus.OK,
            {
                "ok": True,
                "tip_id": deleted.tip_id,
                "expert_id": deleted.expert_id,
                "date": deleted.date,
                "track": deleted.track,
            },
        )

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

    def _betslips_dir(self) -> Path:
        out_dir = type(self).betslips_dir
        if not out_dir:
            out_dir = default_betslips_dir(self.repo_root)
        return Path(out_dir)

    def _handle_list_betslips(self, query: str) -> None:
        qs = parse_qs(query)
        date = (qs.get("date") or [None])[0]
        track = (qs.get("track") or [None])[0]
        items = list_betslips(self._betslips_dir(), date=date, track=track)
        self._send_json(HTTPStatus.OK, {"betslips": items})

    def _handle_get_betslip(self, filename: str) -> None:
        try:
            path, payload, yaml_text = load_betslip_file(self._betslips_dir(), filename)
        except BetslipValidationError as exc:
            status = HTTPStatus.NOT_FOUND if exc.code == "NOT_FOUND" else HTTPStatus.BAD_REQUEST
            self._send_json(status, {"error": {"code": exc.code, "message": str(exc)}})
            return
        self._send_json(
            HTTPStatus.OK,
            {
                "filename": path.name,
                "yaml": yaml_text,
                "betslip": payload,
            },
        )

    def _handle_delete_betslip(self, filename: str) -> None:
        try:
            path = delete_betslip_file(self._betslips_dir(), filename)
        except BetslipValidationError as exc:
            status = HTTPStatus.NOT_FOUND if exc.code == "NOT_FOUND" else HTTPStatus.BAD_REQUEST
            self._send_json(status, {"error": {"code": exc.code, "message": str(exc)}})
            return
        self._send_json(HTTPStatus.OK, {"deleted": path.name})

    def _handle_delete_betslips_batch(self) -> None:
        try:
            body = self._read_json_body()
        except json.JSONDecodeError as exc:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": "INVALID_JSON", "message": str(exc)}},
            )
            return
        filenames = body.get("filenames")
        if not isinstance(filenames, list):
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {
                    "error": {
                        "code": "INVALID_BODY",
                        "message": "Expected {filenames: string[]}",
                    }
                },
            )
            return
        result = delete_betslip_files(self._betslips_dir(), [str(f) for f in filenames])
        self._send_json(HTTPStatus.OK, result)

    def _handle_parse_betslip(self) -> None:
        """Parse YAML (or JSON object) betslip text into validated JSON."""
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        content_type = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        try:
            if content_type == "application/json":
                try:
                    body = json.loads(raw.decode("utf-8") or "{}")
                except json.JSONDecodeError as exc:
                    self._send_json(
                        HTTPStatus.BAD_REQUEST,
                        {"error": {"code": "INVALID_JSON", "message": str(exc)}},
                    )
                    return
                if isinstance(body, dict) and "yaml" in body:
                    payload = parse_betslip_yaml(str(body["yaml"]))
                elif isinstance(body, dict) and "text" in body:
                    payload = parse_betslip_yaml(str(body["text"]))
                elif isinstance(body, dict):
                    payload = validate_betslip_payload(body)
                else:
                    self._send_json(
                        HTTPStatus.BAD_REQUEST,
                        {
                            "error": {
                                "code": "INVALID_BODY",
                                "message": "Expected JSON object or {yaml|text: string}",
                            }
                        },
                    )
                    return
            else:
                # Raw YAML body (text/yaml, text/plain, or unspecified)
                payload = parse_betslip_yaml(raw.decode("utf-8"))
        except BetslipValidationError as exc:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": exc.code, "message": str(exc)}},
            )
            return
        self._send_json(HTTPStatus.OK, {"betslip": payload})

    def _handle_save_betslip(self) -> None:
        """Validate payload, write unique YAML under betslips/, return filename."""
        try:
            body = self._read_json_body()
        except json.JSONDecodeError as exc:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": "INVALID_JSON", "message": str(exc)}},
            )
            return
        try:
            if isinstance(body.get("yaml"), str):
                payload = parse_betslip_yaml(body["yaml"])
            elif isinstance(body.get("betslip"), dict):
                payload = validate_betslip_payload(body["betslip"])
            else:
                payload = validate_betslip_payload(body)
            path = save_betslip_file(payload, directory=self._betslips_dir())
            yaml_text = path.read_text(encoding="utf-8")
            # Re-parse so response betslip matches written file (incl. saved_at).
            payload = parse_betslip_yaml(yaml_text)
        except BetslipValidationError as exc:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": exc.code, "message": str(exc)}},
            )
            return
        try:
            rel = str(path.relative_to(self.repo_root))
        except ValueError:
            rel = str(path)
        self._send_json(
            HTTPStatus.OK,
            {
                "filename": path.name,
                "path": rel,
                "yaml": yaml_text,
                "betslip": payload,
            },
        )

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

    def _serve_activity_jsonl(self) -> None:
        """Serve the live activity log for vai-stats.html (operator tool)."""
        logger = type(self).activity_logger
        log_path = logger.path if logger is not None and logger.enabled else None
        if log_path is None or not log_path.is_file():
            self._send_json(
                HTTPStatus.NOT_FOUND,
                {
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Activity log not available (disabled or empty path)",
                    }
                },
            )
            return
        self._serve_file(
            log_path,
            content_type="application/x-ndjson; charset=utf-8",
            cache_control="no-cache",
        )

    def _serve_file(
        self,
        path: Path,
        *,
        content_type: str | None = None,
        cache_control: str | None = None,
    ) -> None:
        if not path.is_file():
            self._send_json(HTTPStatus.NOT_FOUND, {"error": {"code": "NOT_FOUND", "message": str(path)}})
            return
        content = path.read_bytes()
        if content_type:
            mime = content_type
        else:
            guessed, _ = mimetypes.guess_type(path.name)
            mime = guessed or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self._set_cors_headers()
        self.send_header("Content-Type", mime)
        if cache_control:
            self.send_header("Cache-Control", cache_control)
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
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


def serve(
    *,
    host: str = "127.0.0.1",
    port: int = DEFAULT_PORT,
    activity_log: Path | None | object = ...,
    trusted_proxy_hops: int = 1,
    trusted_proxies: frozenset[str] | None = None,
) -> None:
    """Run the local UI server.

    ``activity_log``:
      - omitted / Ellipsis → default ``{repo}/logs/activity.jsonl``
      - ``None`` → disabled
      - ``Path`` → write JSONL there
    """
    from vai.activity_log import ActivityLogger, parse_activity_log_path

    root = find_repo_root()
    VaiRequestHandler.repo_root = root
    VaiRequestHandler.mockup_dir = root / "outbox" / "mockups"
    VaiRequestHandler.race_cards_dir = root / "inbox" / "race-cards"
    VaiRequestHandler.expert_tips_dir = root / "inbox" / "expert-tips"
    VaiRequestHandler.betslips_dir = root / "betslips"
    VaiRequestHandler.trusted_proxy_hops = max(0, int(trusted_proxy_hops))
    VaiRequestHandler.trusted_proxies = trusted_proxies or frozenset()

    if activity_log is ...:
        log_path = parse_activity_log_path(None, repo_root=root)
    elif activity_log is None:
        log_path = None
    else:
        log_path = Path(activity_log)  # type: ignore[arg-type]
    VaiRequestHandler.activity_logger = ActivityLogger(log_path)

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
    print(f"  Activity stats: http://{host}:{port}/vai-stats.html")
    if log_path is None:
        print("  Activity log: disabled")
    else:
        print(f"  Activity log: {log_path}")
        print(f"  Activity log URL: http://{host}:{port}/activity.jsonl")
    if port != 8765:
        print("  Production (if deployed): https://vai.ornstein.work/  (port 8765)")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()