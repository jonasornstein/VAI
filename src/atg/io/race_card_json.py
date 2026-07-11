"""Serialize race cards for local UI API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from atg.io.race_card import load_race_card
from atg.models.race_card import Leg, RaceCard, RaceInfo


def list_race_card_ids(race_cards_dir: Path) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for path in sorted(race_cards_dir.glob("*.yaml")):
        card = load_race_card(path)
        card_id = path.stem
        cards.append({"id": card_id, "date": card.date, "track": card.track})
    return cards


def load_race_card_by_id(race_cards_dir: Path, card_id: str) -> RaceCard:
    path = race_cards_dir / f"{card_id}.yaml"
    if not path.is_file():
        raise FileNotFoundError(card_id)
    return load_race_card(path)


def race_card_to_dict(card: RaceCard) -> dict[str, Any]:
    return {
        "id": f"{card.date}-{card.track.lower()}",
        "game": card.game,
        "date": card.date,
        "track": card.track,
        "source": card.source,
        "fetched_at": card.fetched_at,
        "settled": card.settled,
        "legs": [_leg_to_dict(leg) for leg in card.legs],
    }


def _leg_to_dict(leg: Leg) -> dict[str, Any]:
    data: dict[str, Any] = {
        "leg": leg.leg,
        "race_label": leg.race_label,
        "horses": list(leg.horses),
        "scratches": list(leg.scratches),
        "reserves": list(leg.reserves),
    }
    if leg.start_time is not None:
        data["start_time"] = leg.start_time
    if leg.race_info is not None:
        data["race_info"] = _race_info_to_dict(leg.race_info)
    if leg.horse_names:
        data["horse_names"] = {str(number): name for number, name in leg.horse_names}
    return data


def _race_info_to_dict(info: RaceInfo) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if info.race_name is not None:
        payload["race_name"] = info.race_name
    if info.distance_m is not None:
        payload["distance_m"] = info.distance_m
    if info.start_method is not None:
        payload["start_method"] = info.start_method
    if info.class_summary is not None:
        payload["class_summary"] = info.class_summary
    if info.status is not None:
        payload["status"] = info.status
    return payload