"""Load expert roster from strategies/experts.yaml."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ExpertRosterEntry:
    expert_id: str
    display_name: str
    product_name: str | None = None
    outlet: str | None = None
    source_url: str | None = None
    notes: str | None = None
    publishes_full_system: bool | str | None = None
    free: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


def default_roster_path() -> Path:
    return Path(__file__).resolve().parent.parent / "strategies" / "experts.yaml"


@lru_cache(maxsize=4)
def _load_roster_cached(path_str: str, mtime_ns: int) -> tuple[ExpertRosterEntry, ...]:
    del mtime_ns  # cache key only
    data = yaml.safe_load(Path(path_str).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return ()
    raw = data.get("experts")
    if not isinstance(raw, list):
        return ()
    entries: list[ExpertRosterEntry] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        expert_id = item.get("expert_id")
        display_name = item.get("display_name")
        if not isinstance(expert_id, str) or not expert_id.strip():
            continue
        if not isinstance(display_name, str) or not display_name.strip():
            continue
        free = item.get("free")
        if free is not None and not isinstance(free, bool):
            free = bool(free)
        entries.append(
            ExpertRosterEntry(
                expert_id=expert_id.strip(),
                display_name=display_name.strip(),
                product_name=_opt_str(item.get("product_name")),
                outlet=_opt_str(item.get("outlet")),
                source_url=_opt_str(item.get("source_url")),
                notes=_opt_str(item.get("notes")),
                publishes_full_system=item.get("publishes_full_system"),
                free=free,
            )
        )
    return tuple(entries)


def load_experts_roster(path: str | Path | None = None) -> list[ExpertRosterEntry]:
    roster_path = Path(path) if path is not None else default_roster_path()
    if not roster_path.is_file():
        return []
    mtime_ns = roster_path.stat().st_mtime_ns
    return list(_load_roster_cached(str(roster_path.resolve()), mtime_ns))


def list_experts(
    *,
    path: str | Path | None = None,
    free_only: bool = False,
    exclude_fixture: bool = True,
) -> list[ExpertRosterEntry]:
    entries = load_experts_roster(path)
    if exclude_fixture:
        entries = [e for e in entries if e.expert_id != "fixture"]
    if free_only:
        entries = [e for e in entries if e.free is True]
    return entries


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return str(value)
    text = value.strip()
    return text or None
