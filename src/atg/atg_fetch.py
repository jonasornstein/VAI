"""Read-only fetch helpers for ATG racinginfo API."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ATG_PRODUCTS_V85_URL = "https://www.atg.se/services/racinginfo/v1/api/products/V85"
ATG_GAME_URL_TEMPLATE = "https://www.atg.se/services/racinginfo/v1/api/games/{game_id}"
USER_AGENT = "ATG-Proposal-Toolkit/1.1.2 (read-only; local operator UI)"


class AtgFetchError(RuntimeError):
    pass


def fetch_json(url: str, *, timeout: float = 15.0) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
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
    return fetch_json(ATG_GAME_URL_TEMPLATE.format(game_id=game_id))