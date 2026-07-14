from vai.cost import compute_cost_sek, count_combinations, format_cost_breakdown


def test_v85_example_from_rules() -> None:
    selections = {
        1: [7],
        2: [3, 7, 12],
        3: [5],
        4: [2, 9],
        5: [1],
        6: [4, 8, 11, 13],
        7: [6],
        8: [2, 10],
    }
    assert count_combinations(selections) == 48
    combinations, cost = compute_cost_sek(selections)
    assert combinations == 48
    assert cost == 24.0
    assert format_cost_breakdown(selections) == "1×3×1×2×1×4×1×2"


def test_all_spiks_minimum_cost() -> None:
    selections = {leg: [leg] for leg in range(1, 9)}
    combinations, cost = compute_cost_sek(selections)
    assert combinations == 1
    assert cost == 0.5
    assert format_cost_breakdown(selections) == "1×1×1×1×1×1×1×1"


def test_cost_formula_fixtures() -> None:
    fixtures = [
        ({leg: [1] for leg in range(1, 9)}, 1, 0.5),
        ({leg: [1, 2] for leg in range(1, 9)}, 256, 128.0),
        (
            {1: [1], 2: [1, 2, 3], 3: [1], 4: [1, 2], 5: [1], 6: [1], 7: [1], 8: [1]},
            6,
            3.0,
        ),
    ]
    for selections, expected_n, expected_cost in fixtures:
        assert count_combinations(selections) == expected_n
        combinations, cost = compute_cost_sek(selections)
        assert combinations == expected_n
        assert cost == expected_cost