from atg.hit_summary import compute_hit_summary


def test_hit_summary_independent_legs() -> None:
    selections = {leg: [1] for leg in range(1, 9)}
    leg_distributions = {leg: {1: 0.10, 2: 0.20} for leg in range(1, 9)}
    summary = compute_hit_summary(selections, leg_distributions)
    assert summary is not None
    assert abs(summary["p8"] - 0.10**8) < 1e-12
    assert summary["p7plus"] > summary["p8"]
    assert summary["p5plus"] > summary["p6plus"] > summary["p7plus"] > summary["p8"]


def test_hit_summary_missing_distributions_returns_none() -> None:
    assert compute_hit_summary({1: [1]}, None) is None