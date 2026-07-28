"""Load and manage expert roster (defaults + optional working copy)."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

EXPERT_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESERVED_EXPERT_IDS = frozenset({"fixture"})


class ExpertRosterError(Exception):
    """Roster validation or mutation error."""

    def __init__(self, message: str, *, code: str = "INVALID_EXPERT") -> None:
        super().__init__(message)
        self.code = code


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


def working_roster_path(repo_root: str | Path) -> Path:
    return Path(repo_root) / "inbox" / "experts" / "roster.yaml"


def effective_roster_path(repo_root: str | Path | None = None) -> Path:
    """Working roster if present, else shipped defaults."""
    if repo_root is not None:
        working = working_roster_path(repo_root)
        if working.is_file():
            return working
    return default_roster_path()


@lru_cache(maxsize=8)
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
        try:
            entries.append(_entry_from_dict(item, strict=False))
        except ExpertRosterError:
            continue
    return tuple(entries)


def _clear_load_cache() -> None:
    _load_roster_cached.cache_clear()


def load_experts_roster(
    path: str | Path | None = None,
    *,
    repo_root: str | Path | None = None,
) -> list[ExpertRosterEntry]:
    """Load roster from explicit path, else effective (working if present, else defaults)."""
    if path is not None:
        roster_path = Path(path)
    else:
        roster_path = effective_roster_path(repo_root)
    if not roster_path.is_file():
        return []
    mtime_ns = roster_path.stat().st_mtime_ns
    return list(_load_roster_cached(str(roster_path.resolve()), mtime_ns))


def list_experts(
    *,
    path: str | Path | None = None,
    repo_root: str | Path | None = None,
    free_only: bool = False,
    exclude_fixture: bool = True,
) -> list[ExpertRosterEntry]:
    entries = load_experts_roster(path, repo_root=repo_root)
    if exclude_fixture:
        entries = [e for e in entries if e.expert_id != "fixture"]
    if free_only:
        entries = [e for e in entries if e.free is True]
    return entries


def save_experts_roster(
    entries: list[ExpertRosterEntry] | tuple[ExpertRosterEntry, ...],
    path: str | Path,
) -> Path:
    """Write full roster YAML. Creates parent dirs. Clears load cache."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "experts": [_entry_to_yaml_dict(e) for e in entries],
    }
    text = yaml.safe_dump(
        payload,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    header = (
        "# Operator-editable expert roster (full copy).\n"
        "# Defaults: src/vai/strategies/experts.yaml — restore via POST /api/v1/experts/reset\n"
    )
    out.write_text(header + text, encoding="utf-8")
    _clear_load_cache()
    return out


def materialize_working_roster(repo_root: str | Path) -> Path:
    """Ensure working roster exists (copy defaults if missing). Returns working path."""
    working = working_roster_path(repo_root)
    if working.is_file():
        return working
    defaults = load_experts_roster(default_roster_path())
    save_experts_roster(defaults, working)
    return working


def parse_expert_entry(data: dict[str, Any]) -> ExpertRosterEntry:
    """Strict parse for API add/update bodies."""
    return _entry_from_dict(data, strict=True)


def add_expert(
    data: dict[str, Any] | ExpertRosterEntry,
    *,
    repo_root: str | Path,
) -> ExpertRosterEntry:
    """Append expert to working roster. Materializes defaults if needed."""
    entry = data if isinstance(data, ExpertRosterEntry) else parse_expert_entry(data)
    if entry.expert_id in RESERVED_EXPERT_IDS and entry.expert_id == "fixture":
        # Allow fixture only if restoring defaults path; operators should not add it
        pass

    working = materialize_working_roster(repo_root)
    entries = load_experts_roster(working)
    if any(e.expert_id == entry.expert_id for e in entries):
        raise ExpertRosterError(
            f"expert_id already exists: {entry.expert_id!r}",
            code="EXPERT_EXISTS",
        )
    entries.append(entry)
    save_experts_roster(entries, working)
    return entry


def update_expert(
    expert_id: str,
    data: dict[str, Any],
    *,
    repo_root: str | Path,
) -> ExpertRosterEntry:
    """Update metadata for expert_id (id itself immutable)."""
    eid = (expert_id or "").strip()
    if not eid:
        raise ExpertRosterError("expert_id required", code="INVALID_EXPERT")
    if eid in RESERVED_EXPERT_IDS:
        raise ExpertRosterError(
            f"Cannot modify reserved expert_id: {eid!r}",
            code="FORBIDDEN_ID",
        )

    working = materialize_working_roster(repo_root)
    entries = load_experts_roster(working)
    idx = next((i for i, e in enumerate(entries) if e.expert_id == eid), None)
    if idx is None:
        raise ExpertRosterError(f"Unknown expert_id: {eid!r}", code="EXPERT_NOT_FOUND")

    # Build update payload from existing + body; force same id
    merged = entries[idx].to_dict()
    for key in (
        "display_name",
        "product_name",
        "outlet",
        "source_url",
        "notes",
        "publishes_full_system",
        "free",
    ):
        if key in data:
            merged[key] = data[key]
    merged["expert_id"] = eid
    updated = parse_expert_entry(merged)
    entries[idx] = updated
    save_experts_roster(entries, working)
    return updated


def delete_expert(
    expert_id: str,
    *,
    repo_root: str | Path,
) -> ExpertRosterEntry:
    """Remove expert from working roster. Does not delete tip YAML."""
    eid = (expert_id or "").strip()
    if not eid:
        raise ExpertRosterError("expert_id required", code="INVALID_EXPERT")
    if eid in RESERVED_EXPERT_IDS:
        raise ExpertRosterError(
            f"Cannot delete reserved expert_id: {eid!r}",
            code="FORBIDDEN_ID",
        )

    working = materialize_working_roster(repo_root)
    entries = load_experts_roster(working)
    found = next((e for e in entries if e.expert_id == eid), None)
    if found is None:
        raise ExpertRosterError(f"Unknown expert_id: {eid!r}", code="EXPERT_NOT_FOUND")

    remaining = [e for e in entries if e.expert_id != eid]
    save_experts_roster(remaining, working)
    return found


def reset_experts_roster(*, repo_root: str | Path) -> list[ExpertRosterEntry]:
    """Overwrite working roster with shipped defaults (full reset)."""
    defaults = load_experts_roster(default_roster_path())
    working = working_roster_path(repo_root)
    save_experts_roster(defaults, working)
    return defaults


def suggest_expert_id(display_name: str) -> str:
    """Slugify display name for expert_id suggestions."""
    text = (display_name or "").strip().lower()
    # Swedish chars
    for src, dst in (
        ("å", "a"),
        ("ä", "a"),
        ("ö", "o"),
        ("é", "e"),
        ("ü", "u"),
    ):
        text = text.replace(src, dst)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "expert"


def _entry_from_dict(item: dict[str, Any], *, strict: bool) -> ExpertRosterEntry:
    expert_id = item.get("expert_id")
    display_name = item.get("display_name")
    if not isinstance(expert_id, str) or not expert_id.strip():
        if strict:
            raise ExpertRosterError("expert_id is required", code="INVALID_EXPERT")
        raise ExpertRosterError("skip", code="INVALID_EXPERT")
    expert_id = expert_id.strip()
    if strict and not EXPERT_ID_PATTERN.match(expert_id):
        raise ExpertRosterError(
            f"expert_id must match {EXPERT_ID_PATTERN.pattern}: {expert_id!r}",
            code="INVALID_EXPERT",
        )
    if not isinstance(display_name, str) or not display_name.strip():
        if strict:
            raise ExpertRosterError("display_name is required", code="INVALID_EXPERT")
        raise ExpertRosterError("skip", code="INVALID_EXPERT")

    free = item.get("free")
    if free is not None and not isinstance(free, bool):
        free = bool(free)

    pfs = item.get("publishes_full_system")
    if pfs is not None and not isinstance(pfs, (bool, str)):
        pfs = str(pfs)

    return ExpertRosterEntry(
        expert_id=expert_id,
        display_name=display_name.strip(),
        product_name=_opt_str(item.get("product_name")),
        outlet=_opt_str(item.get("outlet")),
        source_url=_opt_str(item.get("source_url")),
        notes=_opt_str(item.get("notes")),
        publishes_full_system=pfs,
        free=free,
    )


def _entry_to_yaml_dict(entry: ExpertRosterEntry) -> dict[str, Any]:
    """Preserve full field set for round-trip (include free: false)."""
    d: dict[str, Any] = {
        "expert_id": entry.expert_id,
        "display_name": entry.display_name,
    }
    if entry.product_name is not None:
        d["product_name"] = entry.product_name
    if entry.outlet is not None:
        d["outlet"] = entry.outlet
    if entry.source_url is not None:
        d["source_url"] = entry.source_url
    if entry.notes is not None:
        d["notes"] = entry.notes
    if entry.publishes_full_system is not None:
        d["publishes_full_system"] = entry.publishes_full_system
    if entry.free is not None:
        d["free"] = entry.free
    return d


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return str(value)
    text = value.strip()
    return text or None
