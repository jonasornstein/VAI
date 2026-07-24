"""Expert tip betslip models (UC-12)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExpertTip:
    tip_id: str
    expert_id: str
    expert_name: str
    game: str
    date: str
    track: str
    legs: dict[int, list[int]]
    product_name: str | None = None
    source_url: str | None = None
    source_note: str | None = None
    fetched_at: str | None = None
    status: str = "READY"
    rationale: str | None = None
    path: str | None = None


@dataclass(frozen=True)
class ExpertTipSummary:
    tip_id: str
    expert_id: str
    expert_name: str
    date: str
    track: str
    combinations: int
    cost_sek: float
    cost_breakdown: str
    product_name: str | None = None
    source_url: str | None = None
    status: str = "READY"


@dataclass(frozen=True)
class ExpertManifest:
    mode: str = "expert"
    tip_id: str = ""
    expert_id: str = ""
    expert_name: str = ""
    product_name: str | None = None
    source_url: str | None = None
    source_note: str | None = None
    overridden_legs: tuple[int, ...] = ()


@dataclass(frozen=True)
class ExpertResult:
    selections: dict[int, list[int]]
    combinations: int
    cost_sek: float
    cost_breakdown: str
    manifest: ExpertManifest
    tip: ExpertTip


@dataclass(frozen=True)
class ExpertError:
    code: str
    message: str
    hint: str | None = None
