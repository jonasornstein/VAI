"""UC-11 — random mode v1 (F-030, F-031, F-032).

Operator may mark zero, one, or several horses per leg. Those picks are locked.
On generate, the engine fills each leg to counts whose product matches
SYSTEMKOSTNAD exactly (V85 row price 0.50 SEK).
"""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from math import prod

from vai.cost import V85_ROW_PRICE_SEK, compute_cost_sek, format_cost_breakdown
from vai.models.proposal import RandomError, RandomManifest, RandomResult
from vai.models.race_card import RaceCard

COST_TOLERANCE_SEK = 0.001
NUM_LEGS = 8


def generate_random_v1(
    race_card: RaceCard,
    operator_pools: Mapping[int, Sequence[int]],
    stake_budget_sek: float,
    *,
    seed: int | None = None,
    max_horses_per_leg: Mapping[int, int] | None = None,
    frozen_legs: frozenset[int] | None = None,
) -> RandomResult | RandomError:
    frozen = frozen_legs or frozenset()
    error = _validate_inputs(race_card, operator_pools, stake_budget_sek, frozen_legs=frozen)
    if error is not None:
        return error

    target_error = _target_combinations(stake_budget_sek)
    if isinstance(target_error, RandomError):
        return target_error
    target_combinations = target_error

    operator_picks = {leg: sorted(set(operator_pools[leg])) for leg in range(1, NUM_LEGS + 1)}
    eligible = {leg: sorted(race_card.horses_for_leg(leg)) for leg in range(1, NUM_LEGS + 1)}
    caps = _compute_caps(eligible, max_horses_per_leg)
    min_counts: dict[int, int] = {}
    max_counts: dict[int, int] = {}

    for leg in range(1, NUM_LEGS + 1):
        pick_count = len(operator_picks[leg])
        if leg in frozen:
            if pick_count == 0:
                return RandomError(
                    code="FROZEN_EMPTY_LEG",
                    message=f"Leg {leg} is frozen but has no marked horses",
                    hint="Mark at least one horse or unfreeze the leg",
                )
            min_counts[leg] = pick_count
            max_counts[leg] = pick_count
        else:
            min_counts[leg] = max(1, pick_count)
            max_counts[leg] = caps[leg]

    for leg in range(1, NUM_LEGS + 1):
        if min_counts[leg] > max_counts[leg]:
            return RandomError(
                code="POOL_TOO_WIDE",
                message=f"Leg {leg}: operator marked more horses than allowed",
                hint="Deselect horses or raise per-leg cap",
            )

    solutions = _find_count_vectors(target_combinations, min_counts, max_counts)
    if not solutions:
        min_rows = prod(min_counts[leg] for leg in range(1, NUM_LEGS + 1))
        suggested_combinations = _nearest_achievable_combinations(
            target_combinations, min_counts, max_counts
        )
        suggested_stake = (
            suggested_combinations * V85_ROW_PRICE_SEK if suggested_combinations else None
        )
        hint = "Change picks or adjust budget"
        if suggested_stake is not None:
            hint = (
                f"Nearest achievable SYSTEMKOSTNAD is {suggested_stake:.2f} SEK "
                f"({suggested_combinations} rows)"
            )
        return RandomError(
            code="BUDGET_NOT_MET",
            message="Cannot reach exact SYSTEMKOSTNAD with current horse marks",
            hint=hint,
            cost_sek=min_rows * V85_ROW_PRICE_SEK,
            stake_budget_sek=stake_budget_sek,
            combinations=min_rows,
            selections={leg: list(operator_picks[leg]) for leg in range(1, NUM_LEGS + 1)},
            shrink_steps_used=0,
            suggested_stake_sek=suggested_stake,
            suggested_combinations=suggested_combinations,
        )

    rng = random.Random(seed)
    counts = rng.choice(solutions)
    selections: dict[int, list[int]] = {}
    fill_steps = 0

    for leg in range(1, NUM_LEGS + 1):
        try:
            selections[leg] = _select_horses_for_leg(
                eligible[leg],
                operator_picks[leg],
                counts[leg - 1],
                rng,
            )
        except ValueError:
            return RandomError(
                code="BUDGET_NOT_MET",
                message=f"Leg {leg}: cannot satisfy exact SYSTEMKOSTNAD",
                hint="Change picks or adjust budget",
            )
        fill_steps += max(0, counts[leg - 1] - min_counts[leg])

    combinations, cost_sek = compute_cost_sek(selections)
    breakdown = format_cost_breakdown(selections)

    manifest = RandomManifest(
        seed=seed,
        stake_budget_sek=stake_budget_sek,
        max_horses_per_leg=caps,
        shrink_steps_used=fill_steps,
    )
    return RandomResult(
        selections=selections,
        combinations=combinations,
        cost_sek=cost_sek,
        cost_breakdown=breakdown,
        manifest=manifest,
        shrink_steps_used=fill_steps,
    )


def _target_combinations(stake_budget_sek: float) -> int | RandomError:
    combinations = stake_budget_sek / V85_ROW_PRICE_SEK
    rounded = round(combinations)
    if abs(rounded - combinations) > COST_TOLERANCE_SEK:
        return RandomError(
            code="INVALID_BUDGET",
            message="SYSTEMKOSTNAD must be a multiple of 0.50 SEK",
            hint="V85 row price is 0.50 SEK per combination",
        )
    if rounded < 1:
        return RandomError(
            code="BUDGET_BELOW_MINIMUM",
            message=f"SYSTEMKOSTNAD must be at least {V85_ROW_PRICE_SEK:.2f} SEK",
        )
    return int(rounded)


def _nearest_achievable_combinations(
    target: int,
    min_counts: dict[int, int],
    max_counts: dict[int, int],
) -> int | None:
    """Return combination count closest to target, preferring at-or-below on ties."""
    best_below: int | None = None
    best_above: int | None = None

    def min_product_from(leg: int) -> int:
        return prod(min_counts[i] for i in range(leg, NUM_LEGS + 1))

    def max_product_from(leg: int) -> int:
        return prod(max_counts[i] for i in range(leg, NUM_LEGS + 1))

    def dfs(leg: int, partial: int) -> None:
        nonlocal best_below, best_above
        if leg > NUM_LEGS:
            return
        if leg == NUM_LEGS:
            for count in range(min_counts[leg], max_counts[leg] + 1):
                product = partial * count
                if product <= target and (best_below is None or product > best_below):
                    best_below = product
                if product >= target and (best_above is None or product < best_above):
                    best_above = product
            return

        max_remaining = max_product_from(leg + 1)
        min_remaining = min_product_from(leg + 1)

        for count in range(min_counts[leg], max_counts[leg] + 1):
            new_partial = partial * count
            subtree_max = new_partial * max_remaining
            subtree_min = new_partial * min_remaining
            if best_below is not None and subtree_max <= best_below:
                continue
            if best_above is not None and subtree_min >= best_above:
                continue
            dfs(leg + 1, new_partial)

    dfs(1, 1)
    if best_below is None and best_above is None:
        return None
    if best_below is None:
        return best_above
    if best_above is None:
        return best_below
    if target - best_below <= best_above - target:
        return best_below
    return best_above


def _find_count_vectors(
    target: int,
    min_counts: dict[int, int],
    max_counts: dict[int, int],
) -> list[tuple[int, ...]]:
    solutions: list[tuple[int, ...]] = []

    def dfs(leg: int, prefix: list[int], partial: int) -> None:
        if leg > NUM_LEGS:
            return
        if leg == NUM_LEGS:
            if target % partial != 0:
                return
            final_count = target // partial
            if min_counts[leg] <= final_count <= max_counts[leg]:
                solutions.append(tuple(prefix + [final_count]))
            return

        for count in range(min_counts[leg], max_counts[leg] + 1):
            new_partial = partial * count
            if new_partial > target:
                break
            if target % new_partial != 0:
                continue
            dfs(leg + 1, prefix + [count], new_partial)

    dfs(1, [], 1)
    return solutions


def _select_horses_for_leg(
    eligible: list[int],
    locked: list[int],
    count: int,
    rng: random.Random,
) -> list[int]:
    if count < len(locked):
        raise ValueError("count below locked picks")
    if count > len(eligible):
        raise ValueError("count above eligible horses")
    remaining = [horse for horse in eligible if horse not in locked]
    extra = count - len(locked)
    extras = rng.sample(remaining, extra) if extra else []
    return sorted(locked + extras)


def _validate_inputs(
    race_card: RaceCard,
    operator_pools: Mapping[int, Sequence[int]],
    stake_budget_sek: float,
    *,
    frozen_legs: frozenset[int] | None = None,
) -> RandomError | None:
    frozen = frozen_legs or frozenset()
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

    for leg in frozen:
        if not 1 <= leg <= NUM_LEGS:
            return RandomError(
                code="INVALID_FROZEN_LEG",
                message=f"Invalid frozen leg number: {leg}",
            )

    for leg in range(1, NUM_LEGS + 1):
        picks = list(operator_pools[leg])
        if len(set(picks)) != len(picks):
            return RandomError(
                code="DUPLICATE_PICK",
                message=f"Leg {leg}: duplicate horse numbers in operator picks",
            )

        allowed = race_card.horses_for_leg(leg)
        invalid = [horse for horse in picks if horse not in allowed]
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
    eligible: dict[int, list[int]],
    max_horses_per_leg: Mapping[int, int] | None,
) -> dict[int, int]:
    caps = {leg: len(horses) for leg, horses in eligible.items()}
    if max_horses_per_leg is None:
        return caps
    for leg, override in max_horses_per_leg.items():
        if leg in caps:
            caps[leg] = min(caps[leg], override)
    return caps