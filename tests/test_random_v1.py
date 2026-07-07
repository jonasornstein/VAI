from atg.models.proposal import RandomError, RandomResult
from atg.models.race_card import RaceCard
from atg.strategies.random import generate_random_v1


def _minimal_race_card() -> RaceCard:
    from atg.io.race_card import parse_race_card

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
    result = generate_random_v1(race_card, pools, 500.0, seed=99)
    assert isinstance(result, RandomResult)
    assert result.combinations == 1
    assert result.cost_sek == 0.5
    assert result.shrink_steps_used == 0


def test_forced_spik() -> None:
    race_card = _minimal_race_card()
    pools = {leg: [7] if leg == 3 else [1, 2, 3] for leg in range(1, 9)}
    result = generate_random_v1(race_card, pools, 500.0, seed=1)
    assert isinstance(result, RandomResult)
    assert result.selections[3] == [7]


def test_reproducible_seed() -> None:
    race_card = _minimal_race_card()
    pools = {leg: [1, 2, 3, 4] for leg in range(1, 9)}
    first = generate_random_v1(race_card, pools, 500.0, seed=42)
    second = generate_random_v1(race_card, pools, 500.0, seed=42)
    assert isinstance(first, RandomResult)
    assert isinstance(second, RandomResult)
    assert first.selections == second.selections
    assert first.combinations == second.combinations
    assert first.cost_sek == second.cost_sek
    assert first.manifest.seed == 42


def test_golden_seed_42(sample_race_card: RaceCard) -> None:
    from atg.io.pools import pools_from_race_card

    pools = pools_from_race_card(sample_race_card)
    result = generate_random_v1(sample_race_card, pools, 500.0, seed=42)
    assert isinstance(result, RandomResult)
    # Golden values — fixed seed 42, full pools, budget 500 SEK
    assert result.selections == {
        1: [2, 3, 4, 8, 11],
        2: [1],
        3: [2, 6, 7, 10],
        4: [1, 2, 4, 5, 9],
        5: [3, 6, 8, 11, 12],
        6: [2, 5],
        7: [7],
        8: [4],
    }
    assert result.combinations == 1000
    assert result.cost_sek == 500.0
    assert result.cost_breakdown == "5×1×4×5×5×2×1×1"
    assert result.shrink_steps_used == 8


def test_greedy_shrink_reduces_cost() -> None:
    race_card = _minimal_race_card()
    pools = {
        1: [1, 2, 3, 4, 5],
        2: [1, 2, 3, 4],
        3: [1, 2, 3, 4, 5, 6],
        4: [1],
        5: [1],
        6: [1],
        7: [1],
        8: [1],
    }

    outcome = generate_random_v1(race_card, pools, 10.0, seed=1)
    assert isinstance(outcome, RandomResult)
    assert outcome.shrink_steps_used == 1
    assert outcome.combinations == 18
    assert outcome.cost_sek == 9.0
    assert [len(outcome.selections[leg]) for leg in range(1, 9)] == [2, 3, 3, 1, 1, 1, 1, 1]


def test_budget_not_met_abort() -> None:
    race_card = _minimal_race_card()
    pools = {leg: [1, 2, 3, 4, 5] for leg in range(1, 9)}
    outcome = generate_random_v1(race_card, pools, 0.5, seed=0)
    assert isinstance(outcome, RandomError)
    assert outcome.code == "BUDGET_NOT_MET"
    assert outcome.shrink_steps_used == 10
    assert outcome.cost_sek is not None
    assert outcome.cost_sek > 0.5


def test_empty_pool_rejected() -> None:
    race_card = _minimal_race_card()
    pools = {leg: [1, 2] for leg in range(1, 9)}
    pools[4] = []
    outcome = generate_random_v1(race_card, pools, 500.0, seed=1)
    assert isinstance(outcome, RandomError)
    assert outcome.code == "EMPTY_POOL"


def test_generator_respects_budget() -> None:
    race_card = _minimal_race_card()
    pools = {leg: [1, 2, 3, 4] for leg in range(1, 9)}
    result = generate_random_v1(race_card, pools, 12.0, seed=42)
    assert isinstance(result, RandomResult)
    assert result.cost_sek <= 12.0