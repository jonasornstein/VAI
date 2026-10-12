"""Read-only fetch helpers for ATG racinginfo API."""

from __future__ import annotations

import copy
import http.client
import json
import ssl
import threading
import time
from typing import Any, Callable
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ATG_PRODUCTS_V85_URL = "https://www.atg.se/services/racinginfo/v1/api/products/V85"
ATG_GAME_URL_TEMPLATE = "https://www.atg.se/services/racinginfo/v1/api/games/{game_id}"
ATG_HORSE_RESULTS_URL = "https://www.atg.se/services/racinginfo/v1/api/horses/{horse_id}/results"
USER_AGENT = "ATG-Proposal-Toolkit/1.1.4 (read-only; local operator UI)"


class AtgFetchError(RuntimeError):
    pass


_SSL_CTX = ssl.create_default_context()
_POOL_LOCK = threading.Lock()
_IDLE: dict[str, list[http.client.HTTPSConnection]] = {}
_MAX_IDLE = 8


def _keepalive_get(url: str, timeout: float) -> bytes:
    """GET over a pooled persistent HTTPS connection (saves the TLS handshake, ~0.6 s/call).

    Connections are shared across server request threads; at most _MAX_IDLE are kept."""
    parts = urlsplit(url)
    host = parts.netloc
    path = parts.path + ("?" + parts.query if parts.query else "")
    for attempt in (0, 1):
        with _POOL_LOCK:
            idle = _IDLE.setdefault(host, [])
            conn = idle.pop() if idle and attempt == 0 else None
        if conn is None:
            conn = http.client.HTTPSConnection(host, timeout=timeout, context=_SSL_CTX)
        conn.timeout = timeout
        try:
            conn.request("GET", path, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            resp = conn.getresponse()
            body = resp.read()
        except (http.client.HTTPException, OSError):
            conn.close()
            if attempt:
                raise
            continue  # stale keep-alive socket → one fresh retry
        with _POOL_LOCK:
            idle = _IDLE.setdefault(host, [])
            if not resp.will_close and len(idle) < _MAX_IDLE:
                idle.append(conn)
            else:
                conn.close()
        if resp.status >= 400:
            raise HTTPError(url, resp.status, resp.reason, resp.headers, None)
        return body
    raise AssertionError("unreachable")


def fetch_json(url: str, *, timeout: float = 15.0) -> dict[str, Any]:
    try:
        if url.startswith("https://www.atg.se/"):
            try:
                raw = _keepalive_get(url, timeout)
            except (http.client.HTTPException, OSError) as exc:
                if isinstance(exc, HTTPError):
                    raise
                raise URLError(exc) from exc
        else:
            request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urlopen(request, timeout=timeout) as response:
                raw = response.read()
        payload = json.loads(raw.decode("utf-8"))
    except HTTPError as exc:
        raise AtgFetchError(f"ATG HTTP {exc.code} for {url}") from exc
    except URLError as exc:
        raise AtgFetchError(f"ATG unreachable: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise AtgFetchError(f"ATG returned invalid JSON for {url}") from exc

    if not isinstance(payload, dict):
        raise AtgFetchError(f"ATG response must be an object for {url}")
    return payload


def fetch_v85_products() -> dict[str, Any]:
    return fetch_json(ATG_PRODUCTS_V85_URL)


def fetch_v85_game(game_id: str) -> dict[str, Any]:
    return fetch_game_shared(game_id)


def fetch_horse_results(horse_id: int) -> dict[str, Any]:
    return fetch_json(ATG_HORSE_RESULTS_URL.format(horse_id=horse_id))

# Short-lived shared game payload: the UI's race-cards and card requests for the same
# user action hit ATG once (concurrent callers wait for the in-flight fetch). Not a timer.
GAME_SHARE_SECONDS = 5.0
_GAME_LOCK = threading.Lock()
_GAME_SHARED: dict[str, tuple[float, dict[str, Any]]] = {}
_GAME_INFLIGHT: dict[str, threading.Event] = {}


def fetch_game_shared(game_id: str, fetch: Callable[[], dict[str, Any]] | None = None) -> dict[str, Any]:
    fetch = fetch or (lambda: fetch_json(ATG_GAME_URL_TEMPLATE.format(game_id=game_id)))
    while True:
        with _GAME_LOCK:
            hit = _GAME_SHARED.get(game_id)
            if hit and time.monotonic() - hit[0] < GAME_SHARE_SECONDS:
                return copy.deepcopy(hit[1])
            ev = _GAME_INFLIGHT.get(game_id)
            if ev is None:
                ev = _GAME_INFLIGHT[game_id] = threading.Event()
                owner = True
            else:
                owner = False
        if not owner:
            ev.wait(30)
            with _GAME_LOCK:
                hit = _GAME_SHARED.get(game_id)
            if hit and time.monotonic() - hit[0] < GAME_SHARE_SECONDS:
                return copy.deepcopy(hit[1])
            return fetch()  # owner failed → fetch ourselves (errors propagate)
        try:
            data = fetch()
            with _GAME_LOCK:
                _GAME_SHARED[game_id] = (time.monotonic(), copy.deepcopy(data))
            return data
        finally:
            with _GAME_LOCK:
                _GAME_INFLIGHT.pop(game_id, None)
            ev.set()


def clear_game_shared() -> None:
    with _GAME_LOCK:
        _GAME_SHARED.clear()
