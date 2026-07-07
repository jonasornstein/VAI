"""UC-11 — random mode v1 (F-030, F-031, F-032)."""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence

from atg.cost import V85_ROW_PRICE_SEK, compute_cost_sek, format_cost_breakdown
from atg.models.proposal import RandomError, RandomManifest, RandomResult
from atg.models.race_card import RaceCard

COST_TOLERANCE_SEK = 0.001
MAX_SHRINK_STEPS = 10
NUM_LEGS = 8


def generate_random_v1(
    race_card: RaceCard,
    operator_pools: Mapping[int, Sequence[int]],
    stake_budget_sek: float,
    *,
    seed: int | None = None,
    max_horses_per_leg: Mapping[int, int] | None = None,
) -> RandomResult | RandomError:
    error = _validate_inputs(race_card, operator_pools, stake_budget_sek)
    if error is not None:
        return error

    normalized_pools = {leg: list(operator_pools[leg]) for leg in range(1, NUM_LEGS + 1)}
    caps = _compute_caps(normalized_pools, max_horses_per_leg)

    rng = random.Random(seed)
    selections = _initial_draw(normalized_pools, caps, rng)

    shrink_steps = 0
    combinations, cost_sek = compute_cost_sek(selections)
    breakdown = format_cost_breakdown(selections)

    while cost_sek > stake_budget_sek + COST_TOLERANCE_SEK and shrink_steps < MAX_SHRINK_STEPS:
        leg = _pick_widest_leg(selections)
        if leg is None:
            break
        horse = rng.choice(selections[leg])
        selections[leg].remove(horse)
        selections[leg].sort()
        shrink_steps += 1
        combinations, cost_sek = compute_cost_sek(selections)
        breakdown = format_cost_breakdown(selections)

    if cost_sek > stake_budget_sek + COST_TOLERANCE_SEK:
        return RandomError(
            code="BUDGET_NOT_MET",
            message=f"Cannot meet SYSTEMKOSTNAD after {shrink_steps} shrink steps",
            hint="Raise stake budget, narrow horse pools, or run again with a different seed",
            cost_sek=cost_sek,
            stake_budget_sek=stake_budget_sek,
            combinations=combinations,
            selections={leg: list(horses) for leg, horses in selections.items()},
            shrink_steps_used=shrink_steps,
        )

    manifest = RandomManifest(
        seed=seed,
        stake_budget_sek=stake_budget_sek,
        max_horses_per_leg=caps,
        shrink_steps_used=shrink_steps,
    )
    return RandomResult(
        selections=selections,
        combinations=combinations,
        cost_sek=cost_sek,
        cost_breakdown=breakdown,
        manifest=manifest,
        shrink_steps_used=shrink_steps,
    )


def _validate_inputs(
    race_card: RaceCard,
    operator_pools: Mapping[int, Sequence[int]],
    stake_budget_sek: float,
) -> RandomError | None:
    if len(race_card.legs) != NUM_LEGS:
        return RandomError(
            code="INVALID_RACE_CARD",
            message=f"Race card must have {NUM_LEGS} legs, got {len(race_card.legs)}",
        )

    if set(operator_pools) != set(range(1, NUM_LEGS + 1)):
        return RandomError(
            code="INCOMPLETE_POOLS",
            message="Operator pools must define legs 1..8",
        )

    for leg in range(1, NUM_LEGS + 1):
        pool = list(operator_pools[leg])
        if not pool:
            return RandomError(
                code="EMPTY_POOL",
                message=f"Leg {leg}: operator pool is empty",
                hint="Mark at least one horse per leg",
            )

        allowed = race_card.horses_for_leg(leg)
        invalid = [horse for horse in pool if horse not in allowed]
        if invalid:
            return RandomError(
                code="POOL_NOT_SUBSET",
                message=f"Leg {leg}: horses {invalid} are not on the race card",
            )

    if stake_budget_sek <= 0:
        return RandomError(
            code="INVALID_BUDGET",
            message="SYSTEMKOSTNAD must be greater than 0",
        )

    if stake_budget_sek + COST_TOLERANCE_SEK < V85_ROW_PRICE_SEK:
        return RandomError(
            code="BUDGET_BELOW_MINIMUM",
            message=f"SYSTEMKOSTNAD must be at least {V85_ROW_PRICE_SEK:.2f} SEK",
            hint="Minimum system cost is one spik per leg (0.50 SEK for V85)",
        )

    return None


def _compute_caps(
    pools: dict[int, list[int]],
    max_horses_per_leg: Mapping[int, int] | None,
) -> dict[int, int]:
    caps = {leg: len(pool) for leg, pool in pools.items()}
    if max_horses_per_leg is None:
        return caps
    for leg, override in max_horses_per_leg.items():
        if leg in caps:
            caps[leg] = min(caps[leg], override)
    return caps


def _initial_draw(
    pools: dict[int, list[int]],
    caps: dict[int, int],
    rng: random.Random,
) -> dict[int, list[int]]:
    selections: dict[int, list[int]] = {}
    for leg in range(1, NUM_LEGS + 1):
        pool = pools[leg]
        cap = caps[leg]
        k = rng.randint(1, cap)
        selections[leg] = sorted(rng.sample(pool, k))
    return selections


def _pick_widest_leg(selections: dict[int, list[int]]) -> int | None:
    eligible = [leg for leg in range(1, NUM_LEGS + 1) if len(selections[leg]) > 1]
    if not eligible:
        return None
    max_width = max(len(selections[leg]) for leg in eligible)
    return min(leg for leg in eligible if len(selections[leg]) == max_width)