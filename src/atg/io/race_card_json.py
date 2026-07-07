"""Serialize race cards for local UI API."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from atg.io.race_card import load_race_card
from atg.models.race_card import Leg, RaceCard


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
    data = asdict(leg)
    data["horses"] = list(leg.horses)
    data["scratches"] = list(leg.scratches)
    data["reserves"] = list(leg.reserves)
    return data