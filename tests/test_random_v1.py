from vai.io.pools import empty_operator_pools
from vai.models.proposal import RandomError, RandomResult
from vai.models.race_card import RaceCard
from vai.strategies.random import generate_random_v1


def _minimal_race_card() -> RaceCard:
    from vai.io.race_card import parse_race_card

    legs = []
    for leg in range(1, 9):
        legs.append(
            {
                "leg": leg,
                "race_label": f"V85-{leg}",
                "horses": list(range(1, 13)),
            }
        )
    return parse_race_card(
        {
            "game": "v85",
            "date": "2026-01-01",
            "track": "Test",
            "source": "manual",
            "fetched_at": "2026-01-01T00:00:00Z",
            "settled": False,
            "legs": legs,
        }
    )


def test_minimum_cost_all_spiks() -> None:
    race_card = _minimal_race_card()
    pools = {leg: [leg] for leg in range(1, 9)}
    result = generate_random_v1(race_card, pools, 0.5, seed=99)
    assert isinstance(result, RandomResult)
    assert result.combinations == 1
    assert result.cost_sek == 0.5
    assert result.shrink_steps_used == 0


def test_locked_picks_preserved_at_exact_budget() -> None:
    race_card = _minimal_race_card()
    pools = {leg: [leg] for leg in range(1, 9)}
    result = generate_random_v1(race_card, pools, 500.0, seed=99)
    assert isinstance(result, RandomResult)
    for leg in range(1, 9):
        assert leg in result.selections[leg]
    assert result.cost_sek == 500.0
    assert result.combinations == 1000


def test_forced_spik() -> None:
    race_card = _minimal_race_card()
    pools = {leg: ([7] if leg == 3 else []) for leg in range(1, 9)}
    result = generate_random_v1(race_card, pools, 500.0, seed=1)
    assert isinstance(result, RandomResult)
    assert 7 in result.selections[3]
    assert result.cost_sek == 500.0


def test_empty_picks_hit_exact_budget() -> None:
    race_card = _minimal_race_card()
    pools = empty_operator_pools()
    result = generate_random_v1(race_card, pools, 500.0, seed=1)
    assert isinstance(result, RandomResult)
    assert all(result.selections[leg] for leg in range(1, 9))
    assert result.cost_sek == 500.0
    assert result.combinations == 1000


def test_reproducible_seed() -> None:
    race_card = _minimal_race_card()
    pools = {leg: ([1, 2] if leg == 1 else []) for leg in range(1, 9)}
    first = generate_random_v1(race_card, pools, 500.0, seed=42)
    second = generate_random_v1(race_card, pools, 500.0, seed=42)
    assert isinstance(first, RandomResult)
    assert isinstance(second, RandomResult)
    assert first.selections == second.selections
    assert first.combinations == second.combinations
    assert first.cost_sek == second.cost_sek
    assert first.manifest.seed == 42


def test_golden_seed_42(sample_race_card: RaceCard) -> None:
    pools = empty_operator_pools()
    result = generate_random_v1(sample_race_card, pools, 500.0, seed=42)
    assert isinstance(result, RandomResult)
    assert result.selections == {
        1: [1],
        2: [1, 3, 4, 8, 9],
        3: [3, 8],
        4: [1, 2, 4, 5, 9],
        5: [1, 3, 6, 8, 12],
        6: [9],
        7: [1, 3, 7, 8],
        8: [3],
    }
    assert result.combinations == 1000
    assert result.cost_sek == 500.0
    assert result.cost_breakdown == "1×5×2×5×5×1×4×1"
    assert result.shrink_steps_used == 16


def test_exact_budget_smaller_stake() -> None:
    race_card = _minimal_race_card()
    pools = empty_operator_pools()
    outcome = generate_random_v1(race_card, pools, 12.0, seed=42)
    assert isinstance(outcome, RandomResult)
    assert outcome.cost_sek == 12.0
    assert outcome.combinations == 24


def test_locked_picks_exceed_budget() -> None:
    race_card = _minimal_race_card()
    pools = {leg: [1, 2, 3, 4, 5] for leg in range(1, 9)}
    outcome = generate_random_v1(race_card, pools, 0.5, seed=0)
    assert isinstance(outcome, RandomError)
    assert outcome.code == "BUDGET_NOT_MET"


def test_all_horses_one_leg_suggests_nearest_stake() -> None:
    """Selecting every horse in one leg fixes that factor; budget may need adjustment."""
    race_card = _minimal_race_card()
    pools = {leg: [] for leg in range(1, 9)}
    pools[6] = list(range(1, 13))
    outcome = generate_random_v1(race_card, pools, 20000.0, seed=42)
    assert isinstance(outcome, RandomError)
    assert outcome.code == "BUDGET_NOT_MET"
    assert outcome.suggested_stake_sek is not None
    assert outcome.suggested_combinations is not None
    assert outcome.suggested_combinations % 12 == 0
    retry = generate_random_v1(race_card, pools, outcome.suggested_stake_sek, seed=42)
    assert isinstance(retry, RandomResult)
    assert retry.cost_sek == outcome.suggested_stake_sek


def test_invalid_pick_rejected() -> None:
    race_card = _minimal_race_card()
    pools = {leg: [] for leg in range(1, 9)}
    pools[4] = [99]
    outcome = generate_random_v1(race_card, pools, 500.0, seed=1)
    assert isinstance(outcome, RandomError)
    assert outcome.code == "POOL_NOT_SUBSET"


def test_generator_hits_exact_budget() -> None:
    race_card = _minimal_race_card()
    pools = empty_operator_pools()
    result = generate_random_v1(race_card, pools, 12.0, seed=42)
    assert isinstance(result, RandomResult)
    assert result.cost_sek == 12.0


def test_frozen_leg_uses_only_operator_picks() -> None:
    race_card = _minimal_race_card()
    pools = empty_operator_pools()
    pools[2] = [5]
    pools[4] = [3, 7]
    result = generate_random_v1(
        race_card,
        pools,
        500.0,
        seed=42,
        frozen_legs=frozenset({2, 4}),
    )
    assert isinstance(result, RandomResult)
    assert result.selections[2] == [5]
    assert result.selections[4] == [3, 7]
    assert result.cost_sek == 500.0


def test_frozen_empty_leg_rejected() -> None:
    race_card = _minimal_race_card()
    pools = empty_operator_pools()
    outcome = generate_random_v1(race_card, pools, 500.0, frozen_legs=frozenset({3}))
    assert isinstance(outcome, RandomError)
    assert outcome.code == "FROZEN_EMPTY_LEG"