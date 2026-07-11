"""F-001 / F-005 — load and validate race card YAML."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from atg.models.race_card import Leg, RaceCard, RaceInfo


class RaceCardValidationError(ValueError):
    pass


def load_race_card(path: str | Path) -> RaceCard:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return parse_race_card(data)


def parse_race_card(data: dict[str, Any]) -> RaceCard:
    _require_mapping(data, "race card root")

    game = _require_str(data, "game")
    if game != "v85":
        raise RaceCardValidationError(f"Unsupported game '{game}'; v1 supports v85 only")

    date = _require_iso_field(data, "date")
    track = _require_str(data, "track")
    source = _require_str(data, "source")
    fetched_at = _require_iso_field(data, "fetched_at")
    settled = bool(data.get("settled", False))

    raw_legs = data.get("legs")
    if not isinstance(raw_legs, list):
        raise RaceCardValidationError("legs must be a list")

    legs = tuple(_parse_leg(item) for item in raw_legs)
    if len(legs) != 8:
        raise RaceCardValidationError(f"V85 requires exactly 8 legs, got {len(legs)}")

    leg_numbers = [leg.leg for leg in legs]
    if sorted(leg_numbers) != list(range(1, 9)):
        raise RaceCardValidationError("Leg numbers must be unique integers 1..8")

    return RaceCard(
        game=game,
        date=date,
        track=track,
        legs=legs,
        source=source,
        fetched_at=fetched_at,
        settled=settled,
    )


def _parse_leg(item: Any) -> Leg:
    _require_mapping(item, "leg object")
    leg_num = item.get("leg")
    if not isinstance(leg_num, int) or not 1 <= leg_num <= 8:
        raise RaceCardValidationError(f"Invalid leg number: {leg_num!r}")

    race_label = _require_str(item, "race_label")
    horses = _parse_horse_list(item.get("horses"), field="horses")
    scratches = _parse_horse_list(item.get("scratches", []), field="scratches", allow_empty=True)
    reserves = _parse_horse_list(item.get("reserves", []), field="reserves", allow_empty=True)

    if not horses:
        raise RaceCardValidationError(f"Leg {leg_num}: horses must be non-empty")

    horse_set = set(horses)
    if len(horse_set) != len(horses):
        raise RaceCardValidationError(f"Leg {leg_num}: duplicate horse numbers")

    if horse_set & set(scratches):
        raise RaceCardValidationError(f"Leg {leg_num}: scratches overlap horses")

    start_time = item.get("start_time")
    if start_time is not None and not isinstance(start_time, str):
        raise RaceCardValidationError(f"Leg {leg_num}: start_time must be a string")

    return Leg(
        leg=leg_num,
        race_label=race_label,
        horses=horses,
        start_time=start_time,
        scratches=scratches,
        reserves=reserves,
        race_info=_parse_race_info(item.get("race_info"), leg_num),
        horse_names=_parse_horse_names(item.get("horse_names"), leg_num),
    )


def _parse_horse_names(value: Any, leg_num: int) -> tuple[tuple[int, str], ...]:
    if value is None:
        return ()
    _require_mapping(value, f"leg {leg_num} horse_names")
    names: list[tuple[int, str]] = []
    for key, name in value.items():
        number = int(key) if isinstance(key, str) and key.isdigit() else key
        if not isinstance(number, int) or number <= 0:
            raise RaceCardValidationError(f"Leg {leg_num}: horse_names keys must be positive integers")
        if not isinstance(name, str) or not name.strip():
            raise RaceCardValidationError(f"Leg {leg_num}: horse_names values must be non-empty strings")
        names.append((number, name.strip()))
    names.sort(key=lambda item: item[0])
    return tuple(names)


def _parse_race_info(value: Any, leg_num: int) -> RaceInfo | None:
    if value is None:
        return None
    _require_mapping(value, f"leg {leg_num} race_info")

    race_name = value.get("race_name")
    if race_name is not None and (not isinstance(race_name, str) or not race_name.strip()):
        raise RaceCardValidationError(f"Leg {leg_num}: race_info.race_name must be a non-empty string")

    distance_m = value.get("distance_m")
    if distance_m is not None and (not isinstance(distance_m, int) or distance_m <= 0):
        raise RaceCardValidationError(f"Leg {leg_num}: race_info.distance_m must be a positive integer")

    start_method = value.get("start_method")
    if start_method is not None:
        if not isinstance(start_method, str) or start_method.strip().lower() not in {"volt", "auto", "volte"}:
            raise RaceCardValidationError(f"Leg {leg_num}: race_info.start_method must be volt or auto")
        start_method = "volt" if start_method.strip().lower() in {"volt", "volte"} else "auto"

    class_summary = value.get("class_summary")
    if class_summary is not None and (not isinstance(class_summary, str) or not class_summary.strip()):
        raise RaceCardValidationError(f"Leg {leg_num}: race_info.class_summary must be a non-empty string")

    status = value.get("status")
    if status is not None and (not isinstance(status, str) or not status.strip()):
        raise RaceCardValidationError(f"Leg {leg_num}: race_info.status must be a non-empty string")

    if not any([race_name, distance_m, start_method, class_summary, status]):
        return None

    return RaceInfo(
        race_name=race_name.strip() if isinstance(race_name, str) else None,
        distance_m=distance_m,
        start_method=start_method,
        class_summary=class_summary.strip() if isinstance(class_summary, str) else None,
        status=status.strip() if isinstance(status, str) else None,
    )


def _parse_horse_list(
    value: Any,
    *,
    field: str,
    allow_empty: bool = False,
) -> tuple[int, ...]:
    if value is None:
        if allow_empty:
            return ()
        raise RaceCardValidationError(f"{field} is required")
    if not isinstance(value, list):
        raise RaceCardValidationError(f"{field} must be a list")
    horses: list[int] = []
    for item in value:
        if not isinstance(item, int) or item <= 0:
            raise RaceCardValidationError(f"{field} must contain positive integers")
        horses.append(item)
    if not horses and not allow_empty:
        raise RaceCardValidationError(f"{field} must be non-empty")
    return tuple(horses)


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RaceCardValidationError(f"{label} must be a mapping")
    return value


def _require_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RaceCardValidationError(f"{key} is required and must be a non-empty string")
    return value


def _require_iso_field(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.isoformat()
    return _require_str(data, key)