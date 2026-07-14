"""F-006, F-027, F-028 — V85 schedule from vai."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Callable

from vai.atg_fetch import AtgFetchError, fetch_v85_products

GAME_ID_DATE_RE = re.compile(r"^V85_(\d{4}-\d{2}-\d{2})_")


@dataclass(frozen=True)
class V85Round:
    game_id: str
    date: str
    track: str
    track_id: int
    bettable: bool
    settled: bool
    start_time: str | None


@dataclass(frozen=True)
class V85Schedule:
    source: str
    fetched_at: str
    default_date: str
    dates: tuple[str, ...]
    rounds: tuple[V85Round, ...]


def parse_date_from_game_id(game_id: str) -> str | None:
    match = GAME_ID_DATE_RE.match(game_id)
    return match.group(1) if match else None


def _round_date(raw: dict[str, Any]) -> str | None:
    game_id = raw.get("id")
    if isinstance(game_id, str):
        parsed = parse_date_from_game_id(game_id)
        if parsed:
            return parsed
    start_time = raw.get("startTime")
    if isinstance(start_time, str) and len(start_time) >= 10:
        return start_time[:10]
    return None


def _round_track(raw: dict[str, Any]) -> tuple[str, int] | None:
    tracks = raw.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        return None
    first = tracks[0]
    if not isinstance(first, dict):
        return None
    name = first.get("name")
    track_id = first.get("id")
    if not isinstance(name, str) or not name.strip():
        return None
    if not isinstance(track_id, int):
        return None
    return name, track_id


def _parse_round(raw: dict[str, Any], *, settled: bool) -> V85Round | None:
    game_id = raw.get("id")
    if not isinstance(game_id, str) or not game_id.startswith("V85_"):
        return None
    round_date = _round_date(raw)
    track_info = _round_track(raw)
    if round_date is None or track_info is None:
        return None
    track, track_id = track_info
    bettable = bool(raw.get("bettable")) if not settled else False
    start_time = raw.get("startTime")
    return V85Round(
        game_id=game_id,
        date=round_date,
        track=track,
        track_id=track_id,
        bettable=bettable,
        settled=settled,
        start_time=start_time if isinstance(start_time, str) else None,
    )


def parse_v85_products(payload: dict[str, Any]) -> list[V85Round]:
    rounds: list[V85Round] = []
    for key, settled in (("upcoming", False), ("results", True)):
        items = payload.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            parsed = _parse_round(item, settled=settled)
            if parsed is not None:
                rounds.append(parsed)
    return rounds


def resolve_next_v85_date(
    rounds: list[V85Round],
    *,
    today: date | None = None,
) -> str:
    """F-027 — today if unsettled V85 exists, else next future round."""
    today = today or date.today()
    today_iso = today.isoformat()

    upcoming_today = [r for r in rounds if r.date == today_iso and not r.settled]
    if upcoming_today:
        return today_iso

    future_dates = sorted({r.date for r in rounds if not r.settled and r.date >= today_iso})
    if future_dates:
        return future_dates[0]

    raise AtgFetchError("No upcoming V85 rounds found on ATG")


def build_schedule(
    payload: dict[str, Any],
    *,
    today: date | None = None,
) -> V85Schedule:
    today = today or date.today()
    today_iso = today.isoformat()
    all_rounds = parse_v85_products(payload)
    default_date = resolve_next_v85_date(all_rounds, today=today)

    bettable_rounds = [r for r in all_rounds if not r.settled and r.date >= today_iso]
    dates = tuple(sorted({r.date for r in bettable_rounds}))
    if not dates:
        dates = (default_date,)

    return V85Schedule(
        source="atg",
        fetched_at=datetime.now(timezone.utc).isoformat(),
        default_date=default_date,
        dates=dates,
        rounds=tuple(bettable_rounds),
    )


def fetch_atg_schedule(
    *,
    today: date | None = None,
    fetch_products: Callable[[], dict[str, Any]] = fetch_v85_products,
) -> V85Schedule:
    """F-006 — fetch V85 schedule from vai."""
    payload = fetch_products()
    return build_schedule(payload, today=today)


def schedule_to_dict(schedule: V85Schedule) -> dict[str, Any]:
    return {
        "source": schedule.source,
        "fetched_at": schedule.fetched_at,
        "default_date": schedule.default_date,
        "dates": list(schedule.dates),
        "rounds": [
            {
                "game_id": r.game_id,
                "date": r.date,
                "track": r.track,
                "track_id": r.track_id,
                "bettable": r.bettable,
                "settled": r.settled,
                "start_time": r.start_time,
            }
            for r in schedule.rounds
        ],
    }


def rounds_for_date(schedule: V85Schedule, selected_date: str) -> list[V85Round]:
    """F-028 — tracks for DATUM dropdown."""
    return [r for r in schedule.rounds if r.date == selected_date]