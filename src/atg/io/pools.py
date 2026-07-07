"""Load operator horse pools from YAML or race card defaults."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from atg.models.race_card import RaceCard


class PoolsValidationError(ValueError):
    pass


def pools_from_race_card(race_card: RaceCard) -> dict[int, list[int]]:
    return {leg.leg: list(leg.horses) for leg in race_card.legs}


def empty_operator_pools() -> dict[int, list[int]]:
    return {leg: [] for leg in range(1, 9)}


def load_operator_pools(path: str | Path) -> dict[int, list[int]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PoolsValidationError("Pools file must be a YAML mapping")

    raw_pools = data.get("pools", data)
    if not isinstance(raw_pools, dict):
        raise PoolsValidationError("pools must be a mapping of leg number to horse list")

    pools: dict[int, list[int]] = {}
    for key, value in raw_pools.items():
        leg = int(key)
        if not 1 <= leg <= 8:
            raise PoolsValidationError(f"Invalid leg number: {leg}")
        if not isinstance(value, list) or not value:
            raise PoolsValidationError(f"Leg {leg}: pool must be a non-empty list")
        horses = [int(h) for h in value]
        pools[leg] = horses

    if set(pools) != set(range(1, 9)):
        raise PoolsValidationError("Pools must define legs 1..8")

    return pools