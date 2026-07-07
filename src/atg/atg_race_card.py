"""F-007 — build RaceCard from ATG game JSON."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from atg.atg_fetch import fetch_v85_game
from atg.models.race_card import Leg, RaceCard
from atg.schedule import parse_date_from_game_id

ATG_GAME_ID_RE = re.compile(r"^V85_\d{4}-\d{2}-\d{2}_\d+_\d+$")


def is_atg_game_id(card_id: str) -> bool:
    return bool(ATG_GAME_ID_RE.match(card_id))


def _format_start_time(value: str | None) -> str | None:
    if not value or len(value) < 16:
        return None
    return value[11:16]


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
            horses.append(number)
            if start.get("scratched"):
                scratches.append(number)

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


def fetch_race_card_from_atg(game_id: str) -> RaceCard:
    if not is_atg_game_id(game_id):
        raise ValueError(f"Invalid ATG game id: {game_id}")
    payload = fetch_v85_game(game_id)
    return parse_atg_game(game_id, payload)