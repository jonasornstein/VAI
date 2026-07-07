from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RandomManifest:
    mode: str = "random"
    seed: int | None = None
    stake_budget_sek: float = 500.0
    min_horses_per_leg: int = 1
    max_horses_per_leg: dict[int, int] = field(default_factory=dict)
    max_shrink_steps: int = 10
    shrink_steps_used: int = 0
    weight_by_field_size: bool = False


@dataclass(frozen=True)
class RandomResult:
    selections: dict[int, list[int]]
    combinations: int
    cost_sek: float
    cost_breakdown: str
    manifest: RandomManifest
    shrink_steps_used: int


@dataclass(frozen=True)
class RandomError:
    code: str
    message: str
    hint: str | None = None
    cost_sek: float | None = None
    stake_budget_sek: float | None = None
    combinations: int | None = None
    selections: dict[int, list[int]] | None = None
    shrink_steps_used: int | None = None