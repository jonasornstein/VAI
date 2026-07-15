"""F-007 — build RaceCard from ATG game JSON."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from vai.atg_fetch import fetch_v85_game
from vai.models.race_card import Leg, RaceCard, RaceInfo
from vai.schedule import parse_date_from_game_id

ATG_GAME_ID_RE = re.compile(r"^V85_\d{4}-\d{2}-\d{2}_\d+_\d+$")


def is_atg_game_id(card_id: str) -> bool:
    return bool(ATG_GAME_ID_RE.match(card_id))


def _format_start_time(value: str | None) -> str | None:
    if not value or len(value) < 16:
        return None
    return value[11:16]


def _normalize_start_method(value: str | None) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    key = value.strip().lower()
    if key == "volte":
        return "volt"
    if key == "auto":
        return "auto"
    return key


def extract_horse_names(starts: list[Any]) -> tuple[tuple[int, str], ...]:
    """Map start number -> horse name from ATG starts[].horse.name."""
    names: list[tuple[int, str]] = []
    for start in starts:
        if not isinstance(start, dict):
            continue
        number = start.get("number")
        if not isinstance(number, int) or number <= 0:
            continue
        horse = start.get("horse")
        if not isinstance(horse, dict):
            continue
        name = horse.get("name")
        if isinstance(name, str) and name.strip():
            names.append((number, name.strip()))
    names.sort(key=lambda item: item[0])
    return tuple(names)


def extract_race_info(race: dict[str, Any]) -> RaceInfo | None:
    """F-029 — per-leg race metadata from ATG races[] object."""
    race_name = race.get("name")
    distance = race.get("distance")
    terms = race.get("terms")
    status = race.get("status")

    class_summary: str | None = None
    if isinstance(terms, list) and terms and isinstance(terms[0], str):
        class_summary = terms[0].strip() or None

    start_method = _normalize_start_method(
        race.get("startMethod") if isinstance(race.get("startMethod"), str) else None
    )
    distance_m = distance if isinstance(distance, int) and distance > 0 else None
    race_name_str = race_name.strip() if isinstance(race_name, str) and race_name.strip() else None
    status_str = status if isinstance(status, str) and status.strip() else None

    if not any([race_name_str, distance_m, start_method, class_summary, status_str]):
        return None

    return RaceInfo(
        race_name=race_name_str,
        distance_m=distance_m,
        start_method=start_method,
        class_summary=class_summary,
        status=status_str,
    )


def _track_name(game: dict[str, Any], game_id: str) -> str:
    races = game.get("races")
    if isinstance(races, list) and races:
        first = races[0]
        if isinstance(first, dict):
            track = first.get("track")
            if isinstance(track, dict):
                name = track.get("name")
                if isinstance(name, str) and name.strip():
                    return name
    return "Unknown"


def _is_settled(game: dict[str, Any]) -> bool:
    status = game.get("status")
    if status == "results":
        return True
    races = game.get("races")
    if isinstance(races, list) and races:
        return all(isinstance(r, dict) and r.get("status") == "results" for r in races)
    return False


def parse_atg_game(game_id: str, payload: dict[str, Any]) -> RaceCard:
    races = payload.get("races")
    if not isinstance(races, list) or len(races) != 8:
        raise ValueError(f"ATG game {game_id} must contain exactly 8 races")

    round_date = parse_date_from_game_id(game_id)
    if round_date is None:
        first = races[0]
        if isinstance(first, dict) and isinstance(first.get("date"), str):
            round_date = first["date"]
    if round_date is None:
        raise ValueError(f"Could not determine date for ATG game {game_id}")

    legs: list[Leg] = []
    for index, race in enumerate(races, start=1):
        if not isinstance(race, dict):
            raise ValueError(f"Race {index} in {game_id} is not an object")
        starts = race.get("starts")
        if not isinstance(starts, list) or not starts:
            raise ValueError(f"Race {index} in {game_id} has no starts")

        horses: list[int] = []
        scratches: list[int] = []
        for start in starts:
            if not isinstance(start, dict):
                continue
            number = start.get("number")
            if not isinstance(number, int) or number <= 0:
                continue
            if start.get("scratched"):
                scratches.append(number)
            else:
                horses.append(number)

        if not horses:
            raise ValueError(f"Race {index} in {game_id} has no horse numbers")

        race_number = race.get("number")
        race_label = f"V85-{index}"
        if isinstance(race_number, int):
            race_label = f"V85-{race_number}"

        legs.append(
            Leg(
                leg=index,
                race_label=race_label,
                horses=tuple(horses),
                start_time=_format_start_time(
                    race.get("scheduledStartTime") if isinstance(race.get("scheduledStartTime"), str) else race.get("startTime")
                ),
                scratches=tuple(scratches),
                race_info=extract_race_info(race),
                horse_names=extract_horse_names(starts),
            )
        )

    return RaceCard(
        game="v85",
        date=round_date,
        track=_track_name(payload, game_id),
        legs=tuple(legs),
        source="atg",
        fetched_at=datetime.now(timezone.utc).isoformat(),
        settled=_is_settled(payload),
    )


def _iter_start_pools(
    payload: dict[str, Any],
) -> list[tuple[int, int, dict[str, Any]]]:
    """Yield (leg_index, start_number, pools_dict) for each start with pools."""
    races = payload.get("races")
    if not isinstance(races, list):
        return []
    out: list[tuple[int, int, dict[str, Any]]] = []
    for index, race in enumerate(races, start=1):
        if not isinstance(race, dict):
            continue
        starts = race.get("starts")
        if not isinstance(starts, list):
            continue
        for start in starts:
            if not isinstance(start, dict):
                continue
            number = start.get("number")
            if not isinstance(number, int):
                continue
            pools = start.get("pools")
            if not isinstance(pools, dict):
                continue
            out.append((index, number, pools))
    return out


def extract_leg_distributions(payload: dict[str, Any]) -> dict[int, dict[int, float]]:
    """Map leg -> horse -> V85 bet fraction from ATG game JSON."""
    distributions: dict[int, dict[int, float]] = {}
    for index, number, pools in _iter_start_pools(payload):
        v85_pool = pools.get("V85")
        if not isinstance(v85_pool, dict):
            continue
        bet_distribution = v85_pool.get("betDistribution")
        if isinstance(bet_distribution, (int, float)):
            distributions.setdefault(index, {})[number] = float(bet_distribution) / 10000.0
    return distributions


def extract_leg_odds(payload: dict[str, Any]) -> dict[int, dict[int, float]]:
    """Map leg -> horse -> win odds (decimal) from ATG vinnare pool.

    ATG stores odds as integer hundredths (e.g. 813 → 8.13).
    """
    odds_map: dict[int, dict[int, float]] = {}
    for index, number, pools in _iter_start_pools(payload):
        vinnare = pools.get("vinnare")
        if not isinstance(vinnare, dict):
            continue
        raw = vinnare.get("odds")
        if isinstance(raw, (int, float)) and raw > 0:
            odds_map.setdefault(index, {})[number] = float(raw) / 100.0
    return odds_map


def fetch_race_card_from_atg(game_id: str) -> RaceCard:
    card, _, _ = fetch_atg_race_card_bundle(game_id)
    return card


def fetch_atg_race_card_bundle(
    game_id: str,
) -> tuple[RaceCard, dict[int, dict[int, float]], dict[int, dict[int, float]]]:
    """Return (race_card, leg_distributions, leg_odds)."""
    if not is_atg_game_id(game_id):
        raise ValueError(f"Invalid ATG game id: {game_id}")
    payload = fetch_v85_game(game_id)
    return (
        parse_atg_game(game_id, payload),
        extract_leg_distributions(payload),
        extract_leg_odds(payload),
    )