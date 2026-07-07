from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Leg:
    leg: int
    race_label: str
    horses: tuple[int, ...]
    start_time: str | None = None
    scratches: tuple[int, ...] = ()
    reserves: tuple[int, ...] = ()


@dataclass(frozen=True)
class RaceCard:
    game: str
    date: str
    track: str
    legs: tuple[Leg, ...]
    source: str
    fetched_at: str
    settled: bool

    def leg_by_number(self, leg_num: int) -> Leg:
        for leg in self.legs:
            if leg.leg == leg_num:
                return leg
        raise KeyError(f"Leg {leg_num} not found")

    def horses_for_leg(self, leg_num: int) -> frozenset[int]:
        return frozenset(self.leg_by_number(leg_num).horses)