"""API-key protection for VAI write endpoints (POST/PUT/DELETE that modify data).

Key comes from env ``VAI_API_KEY`` (production: ``/etc/vai/vai.env`` via systemd
``EnvironmentFile=``; never commit it). Clients send it in header ``X-API-Key``.
Fail closed: if ``VAI_API_KEY`` is unset/empty, every protected write gets 503.
"""

from __future__ import annotations

import hmac
import logging
import os
from http import HTTPStatus

API_KEY_ENV = "VAI_API_KEY"
API_KEY_HEADER = "X-API-Key"

log = logging.getLogger("vai.api_auth")

# Pure computation POSTs: nothing is written to disk.
UNPROTECTED_POSTS = frozenset(
    {"/api/v1/generate/random", "/api/v1/generate/expert", "/api/v1/betslips/parse"}
)


def is_protected(method: str, path: str) -> bool:
    method = method.upper()
    if method not in ("POST", "PUT", "DELETE"):
        return False
    if method == "POST" and path in UNPROTECTED_POSTS:
        return False
    return True


def check_api_key(provided: str | None) -> tuple[HTTPStatus | None, str]:
    """Return (None, "ok") when allowed, else (status, reason). Never logs the key."""
    expected = os.environ.get(API_KEY_ENV, "").strip()
    if not expected:
        return HTTPStatus.SERVICE_UNAVAILABLE, "not_configured"
    if not provided:
        return HTTPStatus.UNAUTHORIZED, "missing"
    if not hmac.compare_digest(provided.strip().encode("utf-8"), expected.encode("utf-8")):
        return HTTPStatus.UNAUTHORIZED, "invalid"
    return None, "ok"


def log_write_attempt(*, method: str, path: str, client_ip: str | None, outcome: str) -> None:
    result = "ok" if outcome == "ok" else f"denied({outcome})"
    level = logging.INFO if outcome == "ok" else logging.WARNING
    log.log(level, "write %s method=%s path=%s ip=%s", result, method, path, client_ip or "-")
