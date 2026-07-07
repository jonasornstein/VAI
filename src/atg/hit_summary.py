"""F-052 basic hit summary for Hari mode when leg distributions are available."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def compute_hit_summary(
    selections: Mapping[int, Sequence[int]],
    leg_distributions: Mapping[int, Mapping[int, float]] | None,
) -> dict[str, float] | None:
    """Return P(8), P(≥7), P(≥6), P(≥5) using independent-leg assumption."""
    if not leg_distributions:
        return None

    leg_probs: list[float] = []
    for leg in range(1, 9):
        dist = leg_distributions.get(leg)
        if not dist:
            return None
        horses = selections.get(leg, ())
        if not horses:
            return None
        probability = sum(dist.get(int(horse), 0.0) for horse in horses)
        leg_probs.append(min(1.0, max(0.0, probability)))

    if len(leg_probs) != 8:
        return None

    exact = _exact_distribution(leg_probs)
    return {
        "p8": exact[8],
        "p7plus": sum(exact[7:]),
        "p6plus": sum(exact[6:]),
        "p5plus": sum(exact[5:]),
    }


def _exact_distribution(leg_probs: Sequence[float]) -> list[float]:
    """exact[k] = P(exactly k legs correct) after all legs."""
    distribution = [1.0]
    for probability in leg_probs:
        next_distribution = [0.0] * (len(distribution) + 1)
        for correct, weight in enumerate(distribution):
            next_distribution[correct] += weight * (1.0 - probability)
            next_distribution[correct + 1] += weight * probability
        distribution = next_distribution
    return distribution