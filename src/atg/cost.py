"""F-060, F-061, F-062 — system cost calculation."""

from __future__ import annotations

from math import prod

V85_ROW_PRICE_SEK = 0.50


def count_combinations(selections: dict[int, list[int]], *, num_legs: int = 8) -> int:
    counts = [len(selections[i]) for i in range(1, num_legs + 1)]
    if any(c == 0 for c in counts):
        raise ValueError("Each leg must have at least one selected horse")
    return prod(counts)


def compute_cost_sek(
    selections: dict[int, list[int]],
    *,
    row_price_sek: float = V85_ROW_PRICE_SEK,
    num_legs: int = 8,
) -> tuple[int, float]:
    combinations = count_combinations(selections, num_legs=num_legs)
    return combinations, combinations * row_price_sek


def format_cost_breakdown(selections: dict[int, list[int]], *, num_legs: int = 8) -> str:
    counts = [str(len(selections[i])) for i in range(1, num_legs + 1)]
    return "×".join(counts)