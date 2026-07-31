"""Structured user-activity logging for the VAI HTTP server (F-110, F-111).

JSON Lines events: timestamp, client IP, operation/function, outcome.
See pending/specs/activity-logging-v1.md.
"""

from __future__ import annotations

import ipaddress
import json
import re
import threading
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

# Max User-Agent length stored in an event.
_USER_AGENT_MAX = 256

# Loopback peers are always allowed to supply X-Forwarded-For (local nginx).
_LOOPBACK_NETWORKS = (
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
)


@dataclass(frozen=True)
class ActivityEvent:
    """One structured activity-log record."""

    ts: str
    event_id: str
    event_type: str
    operation: str
    method: str
    path: str
    status: int
    outcome: str
    client_ip: str | None
    peer_ip: str | None
    function: str | None = None
    actor: str | None = None
    user_agent: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_rfc3339(*, when: datetime | None = None) -> str:
    """RFC 3339 UTC timestamp with millisecond precision (…Z)."""
    moment = when if when is not None else datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    else:
        moment = moment.astimezone(timezone.utc)
    # Milliseconds, always Z
    ms = moment.microsecond // 1000
    base = moment.strftime("%Y-%m-%dT%H:%M:%S")
    return f"{base}.{ms:03d}Z"


def _is_loopback(ip: str | None) -> bool:
    if not ip:
        return False
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return any(addr in net for net in _LOOPBACK_NETWORKS)


def _parse_ip(token: str) -> str | None:
    token = token.strip()
    if not token:
        return None
    # Strip surrounding brackets / optional port for IPv6 forms like "[::1]:123"
    if token.startswith("["):
        end = token.find("]")
        if end != -1:
            token = token[1:end]
    elif token.count(":") == 1 and not token.startswith(":"):
        # IPv4:port
        host, _, port = token.rpartition(":")
        if port.isdigit():
            token = host
    try:
        return str(ipaddress.ip_address(token))
    except ValueError:
        return None


def parse_x_forwarded_for(header_value: str | None) -> list[str]:
    """Parse X-Forwarded-For into a list of IP strings (left = client side)."""
    if not header_value:
        return []
    result: list[str] = []
    for part in header_value.split(","):
        parsed = _parse_ip(part)
        if parsed is not None:
            result.append(parsed)
    return result


def is_trusted_peer(peer_ip: str | None, trusted_proxies: frozenset[str]) -> bool:
    """True if peer may contribute X-Forwarded-For (loopback or explicit list)."""
    if not peer_ip:
        return False
    if _is_loopback(peer_ip):
        return True
    normalized = _parse_ip(peer_ip) or peer_ip
    return normalized in trusted_proxies


def resolve_client_ip(
    peer_ip: str | None,
    x_forwarded_for: str | None,
    *,
    trusted_proxy_hops: int = 1,
    trusted_proxies: frozenset[str] | None = None,
) -> str | None:
    """Derive end-client IP; ignore XFF unless peer is trusted (F-111).

    Builds address chain as ``X-Forwarded-For`` entries plus the TCP peer (rightmost).
    With ``trusted_proxy_hops=N``, skip N addresses from the right (proxies) and
    take the next address as the client — same model as Express ``trust proxy N``.

    Example (nginx on loopback, hops=1): XFF ``203.0.113.10``, peer ``127.0.0.1``
    → client ``203.0.113.10``.
    """
    peer = _parse_ip(peer_ip) if peer_ip else None
    if peer is None and peer_ip:
        peer = peer_ip  # keep raw if unparseable

    trusted = trusted_proxies if trusted_proxies is not None else frozenset()
    hops = max(0, int(trusted_proxy_hops))

    if not is_trusted_peer(peer, trusted) or hops == 0:
        return peer

    chain = parse_x_forwarded_for(x_forwarded_for)
    if peer is not None and (not chain or chain[-1] != peer):
        chain = chain + [peer]
    if not chain:
        return peer

    # Client sits just left of the N trusted hops from the right.
    idx = len(chain) - hops - 1
    if idx < 0:
        return peer
    return chain[idx]


def classify_request(method: str, path: str) -> tuple[str, str, str | None]:
    """Map HTTP method + path → (operation, event_type, function label)."""
    method_u = (method or "GET").upper()
    raw_path = path or "/"
    # Drop query string if present
    path_only = urlparse(raw_path).path or "/"
    if path_only != "/" and path_only.endswith("/"):
        path_only = path_only.rstrip("/") or "/"

    if method_u == "OPTIONS":
        return "cors_preflight", "access", "do_OPTIONS"

    # Exact routes
    exact: dict[tuple[str, str], tuple[str, str, str]] = {
        ("GET", "/"): ("serve_index", "access", "_serve_file"),
        ("HEAD", "/"): ("serve_index", "access", "_serve_file"),
        ("GET", "/index.html"): ("serve_index", "access", "_serve_file"),
        ("HEAD", "/index.html"): ("serve_index", "access", "_serve_file"),
        ("GET", "/api/v1/schedule/v85"): ("get_schedule_v85", "access", "_handle_get_schedule_v85"),
        ("GET", "/api/v1/race-cards"): ("list_race_cards", "access", "do_GET"),
        ("GET", "/api/v1/expert-tips"): ("list_expert_tips", "access", "_handle_list_expert_tips"),
        ("POST", "/api/v1/expert-tips"): ("save_expert_tip", "change", "_handle_save_expert_tip"),
        ("PUT", "/api/v1/expert-tips"): ("save_expert_tip", "change", "_handle_save_expert_tip"),
        ("DELETE", "/api/v1/expert-tips"): ("delete_expert_tip", "change", "_handle_delete_expert_tip"),
        ("GET", "/api/v1/experts"): ("list_experts", "access", "_handle_list_experts"),
        ("POST", "/api/v1/experts"): ("add_expert", "change", "_handle_add_expert"),
        ("POST", "/api/v1/experts/reset"): ("reset_experts", "change", "_handle_reset_experts"),
        ("PUT", "/api/v1/experts/visibility"): (
            "set_experts_visibility",
            "change",
            "_handle_set_all_experts_visible",
        ),
        ("PUT", "/api/v1/experts/reorder"): ("reorder_experts", "change", "_handle_reorder_experts"),
        ("POST", "/api/v1/generate/random"): (
            "generate_random",
            "generation",
            "_handle_generate_random",
        ),
        ("POST", "/api/v1/generate/expert"): (
            "generate_expert",
            "generation",
            "_handle_generate_expert",
        ),
    }
    hit = exact.get((method_u, path_only))
    if hit is not None:
        return hit

    if path_only.startswith("/mockup/"):
        return "serve_mockup", "access", "_serve_file"

    m = re.match(r"^/api/v1/race-cards/([^/]+)$", path_only)
    if m and method_u in ("GET", "HEAD"):
        return "get_race_card", "access", "_handle_get_race_card"

    m = re.match(r"^/api/v1/expert-tips/([^/]+)$", path_only)
    if m:
        if method_u in ("GET", "HEAD"):
            return "get_expert_tip", "access", "_handle_get_expert_tip"
        if method_u == "DELETE":
            return "delete_expert_tip", "change", "_handle_delete_expert_tip"

    m = re.match(r"^/api/v1/experts/([^/]+)$", path_only)
    if m:
        segment = m.group(1)
        if segment in ("reset", "visibility", "reorder"):
            return "not_found", "error", None
        if method_u in ("GET", "HEAD"):
            return "get_expert", "access", "_handle_get_expert"
        if method_u == "PUT":
            return "update_expert", "change", "_handle_update_expert"
        if method_u == "DELETE":
            return "delete_expert", "change", "_handle_delete_expert"

    return "http_request", "access", None


def build_activity_event(
    *,
    method: str,
    path: str,
    status: int,
    peer_ip: str | None,
    x_forwarded_for: str | None = None,
    user_agent: str | None = None,
    actor: str | None = None,
    trusted_proxy_hops: int = 1,
    trusted_proxies: frozenset[str] | None = None,
    when: datetime | None = None,
    event_id: str | None = None,
) -> ActivityEvent:
    """Build a complete activity event for one HTTP response."""
    operation, event_type, function = classify_request(method, path)
    path_only = urlparse(path or "/").path or "/"
    try:
        status_int = int(status)
    except (TypeError, ValueError):
        status_int = 0

    if status_int == 404 and operation in ("http_request", "not_found"):
        operation = "not_found"
        event_type = "error"
    elif status_int >= 400 and operation == "http_request":
        event_type = "error"

    client_ip = resolve_client_ip(
        peer_ip,
        x_forwarded_for,
        trusted_proxy_hops=trusted_proxy_hops,
        trusted_proxies=trusted_proxies,
    )
    peer_norm = _parse_ip(peer_ip) if peer_ip else peer_ip

    ua = user_agent
    if ua is not None:
        ua = ua.strip()
        if len(ua) > _USER_AGENT_MAX:
            ua = ua[:_USER_AGENT_MAX]
        if not ua:
            ua = None

    outcome = "success" if 0 < status_int < 400 else "failure"
    if status_int == 0:
        outcome = "failure"

    return ActivityEvent(
        ts=utc_now_rfc3339(when=when),
        event_id=event_id or str(uuid.uuid4()),
        event_type=event_type,
        operation=operation,
        method=(method or "GET").upper(),
        path=path_only,
        status=status_int,
        outcome=outcome,
        client_ip=client_ip,
        peer_ip=peer_norm,
        function=function,
        actor=actor,
        user_agent=ua,
    )


class ActivityLogger:
    """Thread-safe JSONL writer. ``path=None`` disables file logging."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path
        self._lock = threading.Lock()
        self._disabled_warned = False
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path | None:
        return self._path

    @property
    def enabled(self) -> bool:
        return self._path is not None

    def emit(self, event: ActivityEvent) -> None:
        if self._path is None:
            return
        line = json.dumps(event.to_dict(), ensure_ascii=False, separators=(",", ":"))
        try:
            with self._lock:
                with self._path.open("a", encoding="utf-8") as fh:
                    fh.write(line + "\n")
        except OSError as exc:
            if not self._disabled_warned:
                self._disabled_warned = True
                print(f"activity log write failed: {exc}", flush=True)

    def emit_from_request(
        self,
        *,
        method: str,
        path: str,
        status: int,
        peer_ip: str | None,
        headers: Mapping[str, str] | None = None,
        trusted_proxy_hops: int = 1,
        trusted_proxies: frozenset[str] | None = None,
    ) -> ActivityEvent:
        headers = headers or {}
        # Case-insensitive header lookup
        xff = _header_get(headers, "X-Forwarded-For")
        ua = _header_get(headers, "User-Agent")
        event = build_activity_event(
            method=method,
            path=path,
            status=status,
            peer_ip=peer_ip,
            x_forwarded_for=xff,
            user_agent=ua,
            trusted_proxy_hops=trusted_proxy_hops,
            trusted_proxies=trusted_proxies,
        )
        self.emit(event)
        return event


def _header_get(headers: Mapping[str, str], name: str) -> str | None:
    target = name.lower()
    for key, value in headers.items():
        if key.lower() == target:
            return value
    return None


def parse_activity_log_path(
    raw: str | None,
    *,
    repo_root: Path,
    default_relative: str = "logs/activity.jsonl",
) -> Path | None:
    """Resolve CLI/env log path. ``none`` / empty → disabled."""
    if raw is None:
        return (repo_root / default_relative).resolve()
    stripped = raw.strip()
    if not stripped or stripped.lower() in ("none", "off", "false", "0", "-"):
        return None
    path = Path(stripped).expanduser()
    if not path.is_absolute():
        path = repo_root / path
    return path.resolve()


def parse_trusted_proxies(raw: str | None) -> frozenset[str]:
    """Comma-separated IP list → frozenset of normalized addresses."""
    if not raw or not raw.strip():
        return frozenset()
    out: set[str] = set()
    for part in raw.split(","):
        parsed = _parse_ip(part)
        if parsed is not None:
            out.add(parsed)
    return frozenset(out)
