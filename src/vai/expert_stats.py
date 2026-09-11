"""F-049 — count how often each horse is selected per leg across expert tips."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vai.io.expert_tips import iter_expert_tips
from vai.io.experts_roster import list_experts
from vai.models.expert_tip import ExpertTip

NUM_LEGS = 8


@dataclass(frozen=True)
class HorseStat:
    horse: int
    count: int
    pct: float
    expert_ids: tuple[str, ...]
    expert_names: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "horse": self.horse,
            "count": self.count,
            "pct": self.pct,
            "expert_ids": list(self.expert_ids),
            "expert_names": list(self.expert_names),
        }


@dataclass(frozen=True)
class ExpertTipRef:
    tip_id: str
    expert_id: str
    expert_name: str

    def to_dict(self) -> dict[str, str]:
        return {
            "tip_id": self.tip_id,
            "expert_id": self.expert_id,
            "expert_name": self.expert_name,
        }


@dataclass(frozen=True)
class ExpertHorseStats:
    date: str
    track: str
    tip_count: int
    expert_count: int
    tips: tuple[ExpertTipRef, ...]
    legs: dict[int, tuple[HorseStat, ...]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "track": self.track,
            "tip_count": self.tip_count,
            "expert_count": self.expert_count,
            "tips": [t.to_dict() for t in self.tips],
            "legs": {str(leg): [row.to_dict() for row in rows] for leg, rows in sorted(self.legs.items())},
        }


def compute_expert_horse_stats(
    tips: Sequence[ExpertTip],
    *,
    date: str = "",
    track: str = "",
) -> ExpertHorseStats:
    """Count horse appearances per leg. Each tip is one vote. pct = 100 * count / N."""
    resolved_date = date or (tips[0].date if tips else "")
    resolved_track = track or (tips[0].track if tips else "")
    n = len(tips)
    refs = tuple(
        ExpertTipRef(tip_id=t.tip_id, expert_id=t.expert_id, expert_name=t.expert_name) for t in tips
    )
    expert_count = len({t.expert_id for t in tips})

    legs: dict[int, tuple[HorseStat, ...]] = {}
    for leg in range(1, NUM_LEGS + 1):
        # horse -> list of (expert_id, expert_name) in tip order (one entry per tip)
        picked: dict[int, list[tuple[str, str]]] = defaultdict(list)
        for tip in tips:
            seen: set[int] = set()
            for horse in tip.legs.get(leg, ()):
                number = int(horse)
                if number in seen:
                    continue
                seen.add(number)
                picked[number].append((tip.expert_id, tip.expert_name))
        rows: list[HorseStat] = []
        for horse, names in picked.items():
            count = len(names)
            pct = round(100.0 * count / n, 1) if n else 0.0
            rows.append(
                HorseStat(
                    horse=horse,
                    count=count,
                    pct=pct,
                    expert_ids=tuple(eid for eid, _ in names),
                    expert_names=tuple(ename for _, ename in names),
                )
            )
        rows.sort(key=lambda row: (-row.count, row.horse))
        legs[leg] = tuple(rows)

    return ExpertHorseStats(
        date=resolved_date,
        track=resolved_track,
        tip_count=n,
        expert_count=expert_count,
        tips=refs,
        legs=legs,
    )


def expert_horse_stats_for_round(
    tips_dir: str | Path,
    *,
    date: str,
    track: str,
    repo_root: str | Path | None = None,
    visible_only: bool = True,
    free_only: bool = False,
    exclude_fixture: bool = True,
    allowed_expert_ids: Iterable[str] | None = None,
) -> ExpertHorseStats:
    """Load tips for date+track, filter to the shown roster, then F-049."""
    allowed: set[str] | None
    if allowed_expert_ids is not None:
        allowed = {eid for eid in allowed_expert_ids}
    elif repo_root is not None:
        experts = list_experts(
            repo_root=repo_root,
            free_only=free_only,
            exclude_fixture=exclude_fixture,
            visible_only=visible_only,
        )
        allowed = {e.expert_id for e in experts}
    else:
        allowed = None

    selected: list[ExpertTip] = []
    for tip in iter_expert_tips(tips_dir, date=date, track=track):
        if exclude_fixture and tip.expert_id == "fixture":
            continue
        if allowed is not None and tip.expert_id not in allowed:
            continue
        selected.append(tip)
    return compute_expert_horse_stats(selected, date=date, track=track)
