"""F-040 — load, list, and save expert tip YAML from inbox/expert-tips/."""

from __future__ import annotations

import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from vai.cost import compute_cost_sek, format_cost_breakdown
from vai.models.expert_tip import ExpertTip, ExpertTipSummary

NUM_LEGS = 8


class ExpertTipValidationError(ValueError):
    def __init__(self, message: str, *, code: str = "INVALID_TIP") -> None:
        super().__init__(message)
        self.code = code


def default_tips_dir(repo_root: Path | None = None) -> Path:
    if repo_root is None:
        here = Path(__file__).resolve()
        for parent in here.parents:
            if (parent / "pyproject.toml").is_file() and (parent / "inbox").is_dir():
                return parent / "inbox" / "expert-tips"
        cwd = Path.cwd()
        return cwd / "inbox" / "expert-tips"
    return repo_root / "inbox" / "expert-tips"


def track_slug(track: str) -> str:
    """Folder slug: Bollnäs → bollnas, Årjäng → arjang."""
    nfkd = unicodedata.normalize("NFKD", track.strip())
    asciiish = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    return "".join(ch for ch in asciiish.casefold() if ch.isalnum())


def default_tip_id(expert_id: str, date: str) -> str:
    return f"{expert_id.strip()}-{date.strip()}"


def _existing_tip_ids(tips_dir: str | Path) -> set[str]:
    """All tip_id values currently loadable under tips_dir."""
    root = Path(tips_dir)
    if not root.is_dir():
        return set()
    ids: set[str] = set()
    for path in root.rglob("*.yaml"):
        if path.name.startswith("."):
            continue
        try:
            tip = load_expert_tip(path)
        except (ExpertTipValidationError, OSError, yaml.YAMLError):
            continue
        ids.add(tip.tip_id)
    return ids


def allocate_tip_id(tips_dir: str | Path, expert_id: str, date: str) -> str:
    """Return a tip_id not already used: base, then base-2, base-3, …"""
    base = default_tip_id(expert_id, date)
    used = _existing_tip_ids(tips_dir)
    if base not in used:
        return base
    n = 2
    while True:
        candidate = f"{base}-{n}"
        if candidate not in used:
            return candidate
        n += 1
        if n > 10_000:
            raise ExpertTipValidationError(
                f"Could not allocate tip_id for {expert_id!r} {date!r}",
                code="TIP_ID_COLLISION",
            )


def tip_dir(tips_dir: str | Path, date: str, track: str) -> Path:
    return Path(tips_dir) / f"{date.strip()}-{track_slug(track)}"


def tip_path(tips_dir: str | Path, date: str, track: str, tip_id: str) -> Path:
    return tip_dir(tips_dir, date, track) / f"{tip_id.strip()}.yaml"


def load_expert_tip(path: str | Path) -> ExpertTip:
    tip_path_obj = Path(path)
    data = yaml.safe_load(tip_path_obj.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ExpertTipValidationError("Tip root must be a mapping")
    return parse_expert_tip(data, path=str(tip_path_obj))


def parse_expert_tip(data: dict[str, Any], *, path: str | None = None) -> ExpertTip:
    tip_id = _require_str(data, "tip_id")
    expert_id = _require_str(data, "expert_id")
    expert_name = _require_str(data, "expert_name")
    game = _require_str(data, "game")
    if game != "v85":
        raise ExpertTipValidationError(
            f"Unsupported game '{game}'; only v85",
            code="UNSUPPORTED_GAME",
        )
    date = _require_str(data, "date")
    track = _require_str(data, "track")
    legs = _parse_legs(data.get("legs"))
    status = str(data.get("status") or "READY")
    return ExpertTip(
        tip_id=tip_id,
        expert_id=expert_id,
        expert_name=expert_name,
        game=game,
        date=date,
        track=track,
        legs=legs,
        product_name=_optional_str(data.get("product_name")),
        source_url=_optional_str(data.get("source_url")),
        source_note=_optional_str(data.get("source_note")),
        fetched_at=_optional_str(data.get("fetched_at")),
        status=status,
        rationale=_optional_str(data.get("rationale")),
        path=path,
    )


def list_expert_tips(
    tips_dir: str | Path,
    *,
    date: str | None = None,
    track: str | None = None,
    expert_id: str | None = None,
) -> list[ExpertTipSummary]:
    root = Path(tips_dir)
    if not root.is_dir():
        return []

    summaries: list[ExpertTipSummary] = []
    for path in sorted(root.rglob("*.yaml")):
        if path.name.startswith("."):
            continue
        try:
            tip = load_expert_tip(path)
        except (ExpertTipValidationError, OSError, yaml.YAMLError):
            continue
        if date is not None and tip.date != date:
            continue
        if track is not None and not _tracks_match(tip.track, track):
            continue
        if expert_id is not None and tip.expert_id != expert_id:
            continue
        combinations, cost_sek = compute_cost_sek(tip.legs)
        summaries.append(
            ExpertTipSummary(
                tip_id=tip.tip_id,
                expert_id=tip.expert_id,
                expert_name=tip.expert_name,
                date=tip.date,
                track=tip.track,
                combinations=combinations,
                cost_sek=cost_sek,
                cost_breakdown=format_cost_breakdown(tip.legs),
                product_name=tip.product_name,
                source_url=tip.source_url,
                status=tip.status,
            )
        )
    summaries.sort(key=lambda s: (s.date, s.track, s.expert_name, s.tip_id))
    return summaries


def find_expert_tip(tips_dir: str | Path, tip_id: str) -> ExpertTip:
    root = Path(tips_dir)
    if not root.is_dir():
        raise ExpertTipValidationError(f"Tips directory not found: {root}", code="TIP_NOT_FOUND")
    for path in root.rglob("*.yaml"):
        try:
            tip = load_expert_tip(path)
        except (ExpertTipValidationError, OSError, yaml.YAMLError):
            continue
        if tip.tip_id == tip_id:
            return tip
    raise ExpertTipValidationError(f"Unknown tip_id: {tip_id}", code="TIP_NOT_FOUND")


def find_expert_tip_for(
    tips_dir: str | Path,
    *,
    expert_id: str,
    date: str,
    track: str,
) -> ExpertTip | None:
    """Return the tip for expert+date+track, or None if missing."""
    root = Path(tips_dir)
    if not root.is_dir():
        return None
    for path in sorted(root.rglob("*.yaml")):
        if path.name.startswith("."):
            continue
        try:
            tip = load_expert_tip(path)
        except (ExpertTipValidationError, OSError, yaml.YAMLError):
            continue
        if tip.expert_id != expert_id:
            continue
        if tip.date != date:
            continue
        if not _tracks_match(tip.track, track):
            continue
        return tip
    return None


def tip_to_summary(tip: ExpertTip) -> ExpertTipSummary:
    combinations, cost_sek = compute_cost_sek(tip.legs)
    return ExpertTipSummary(
        tip_id=tip.tip_id,
        expert_id=tip.expert_id,
        expert_name=tip.expert_name,
        date=tip.date,
        track=tip.track,
        combinations=combinations,
        cost_sek=cost_sek,
        cost_breakdown=format_cost_breakdown(tip.legs),
        product_name=tip.product_name,
        source_url=tip.source_url,
        status=tip.status,
    )


def tip_to_dict(tip: ExpertTip, *, include_path: bool = False) -> dict[str, Any]:
    """Full tip payload for API / form prefill (includes legs)."""
    payload: dict[str, Any] = {
        "tip_id": tip.tip_id,
        "expert_id": tip.expert_id,
        "expert_name": tip.expert_name,
        "game": tip.game,
        "date": tip.date,
        "track": tip.track,
        "legs": {str(k): v for k, v in sorted(tip.legs.items())},
        "status": tip.status,
    }
    if tip.product_name is not None:
        payload["product_name"] = tip.product_name
    if tip.source_url is not None:
        payload["source_url"] = tip.source_url
    if tip.source_note is not None:
        payload["source_note"] = tip.source_note
    if tip.fetched_at is not None:
        payload["fetched_at"] = tip.fetched_at
    if tip.rationale is not None:
        payload["rationale"] = tip.rationale
    if include_path and tip.path is not None:
        payload["path"] = tip.path
    return payload


def save_expert_tip(
    tips_dir: str | Path,
    data: dict[str, Any] | ExpertTip,
    *,
    fetched_at: str | None = None,
) -> ExpertTip:
    """Validate and write tip YAML.

    - With ``tip_id``: update that tip file if it exists, otherwise create it.
    - Without ``tip_id``: allocate a new unique id (``expert-date``, ``-2``, …)
      so the same expert can have multiple systems for one omgång.
    """
    root = Path(tips_dir)
    if isinstance(data, ExpertTip):
        raw: dict[str, Any] = tip_to_dict(data)
    else:
        raw = dict(data)

    expert_id = _optional_str(raw.get("expert_id")) or ""
    date = _optional_str(raw.get("date")) or ""
    track = _optional_str(raw.get("track")) or ""

    requested_id = _optional_str(raw.get("tip_id"))
    existing_by_id: ExpertTip | None = None
    if requested_id:
        try:
            existing_by_id = find_expert_tip(root, requested_id)
        except ExpertTipValidationError as exc:
            if exc.code != "TIP_NOT_FOUND":
                raise
            existing_by_id = None
        raw["tip_id"] = requested_id
    elif expert_id and date:
        raw["tip_id"] = allocate_tip_id(root, expert_id, date)
    # else: parse_expert_tip will raise Missing tip_id

    if not _optional_str(raw.get("status")):
        raw["status"] = existing_by_id.status if existing_by_id is not None else "DRAFT"

    if fetched_at is not None:
        raw["fetched_at"] = fetched_at
    elif not _optional_str(raw.get("fetched_at")):
        if existing_by_id is not None and existing_by_id.fetched_at:
            raw["fetched_at"] = existing_by_id.fetched_at
        else:
            raw["fetched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Validate before choosing path so missing fields raise cleanly.
    tip = parse_expert_tip(raw)

    if existing_by_id is not None and existing_by_id.path:
        out_path = Path(existing_by_id.path)
        # If date/track changed, prefer canonical path for the new location
        # but keep overwriting same tip_id file when path still valid.
        if tip.date != existing_by_id.date or not _tracks_match(tip.track, existing_by_id.track):
            out_path = tip_path(root, tip.date, tip.track, tip.tip_id)
    else:
        out_path = tip_path(root, tip.date, tip.track, tip.tip_id)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = _tip_yaml_payload(tip)
    out_path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, default_flow_style=None),
        encoding="utf-8",
    )
    # If we moved tip_id to a new path, remove the old file
    if (
        existing_by_id is not None
        and existing_by_id.path
        and Path(existing_by_id.path).resolve() != out_path.resolve()
        and Path(existing_by_id.path).is_file()
    ):
        try:
            Path(existing_by_id.path).unlink()
        except OSError:
            pass

    return ExpertTip(
        tip_id=tip.tip_id,
        expert_id=tip.expert_id,
        expert_name=tip.expert_name,
        game=tip.game,
        date=tip.date,
        track=tip.track,
        legs=tip.legs,
        product_name=tip.product_name,
        source_url=tip.source_url,
        source_note=tip.source_note,
        fetched_at=tip.fetched_at,
        status=tip.status,
        rationale=tip.rationale,
        path=str(out_path),
    )


def delete_expert_tip(
    tips_dir: str | Path,
    *,
    tip_id: str | None = None,
    expert_id: str | None = None,
    date: str | None = None,
    track: str | None = None,
) -> ExpertTip:
    """Delete a tip YAML file. Resolve by tip_id or expert_id+date+track."""
    root = Path(tips_dir)
    tip: ExpertTip | None = None

    if tip_id and tip_id.strip():
        tip = find_expert_tip(root, tip_id.strip())
    elif expert_id and date and track:
        tip = find_expert_tip_for(
            root,
            expert_id=expert_id.strip(),
            date=date.strip(),
            track=track.strip(),
        )
        if tip is None:
            raise ExpertTipValidationError(
                f"No tip for expert_id={expert_id!r} date={date!r} track={track!r}",
                code="TIP_NOT_FOUND",
            )
    else:
        raise ExpertTipValidationError(
            "Provide tip_id or expert_id+date+track",
            code="MISSING_FIELD",
        )

    if not tip.path:
        raise ExpertTipValidationError(
            f"Tip has no path: {tip.tip_id}",
            code="TIP_NOT_FOUND",
        )
    path = Path(tip.path)
    # Safety: only delete files under tips_dir
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ExpertTipValidationError(
            f"Tip path outside tips directory: {path}",
            code="FORBIDDEN",
        ) from exc
    if not path.is_file():
        raise ExpertTipValidationError(
            f"Tip file not found: {path}",
            code="TIP_NOT_FOUND",
        )
    path.unlink()
    # Remove empty parent folder under tips_dir (not the tips root itself)
    parent = path.parent
    if parent != root.resolve() and parent.is_dir() and not any(parent.iterdir()):
        try:
            parent.rmdir()
        except OSError:
            pass
    return tip


def _tip_yaml_payload(tip: ExpertTip) -> dict[str, Any]:
    """Ordered dict for human-readable YAML."""
    payload: dict[str, Any] = {
        "tip_id": tip.tip_id,
        "expert_id": tip.expert_id,
        "expert_name": tip.expert_name,
    }
    if tip.product_name is not None:
        payload["product_name"] = tip.product_name
    payload["game"] = tip.game
    payload["date"] = tip.date
    payload["track"] = tip.track
    if tip.source_url is not None:
        payload["source_url"] = tip.source_url
    if tip.source_note is not None:
        payload["source_note"] = tip.source_note
    if tip.fetched_at is not None:
        payload["fetched_at"] = tip.fetched_at
    payload["status"] = tip.status
    payload["legs"] = {leg: tip.legs[leg] for leg in range(1, NUM_LEGS + 1)}
    if tip.rationale is not None:
        payload["rationale"] = tip.rationale
    return payload


def _parse_legs(raw: Any) -> dict[int, list[int]]:
    if not isinstance(raw, dict):
        raise ExpertTipValidationError("legs must be a mapping of leg -> horses")
    legs: dict[int, list[int]] = {}
    for key, value in raw.items():
        try:
            leg = int(key)
        except (TypeError, ValueError) as exc:
            raise ExpertTipValidationError(f"Invalid leg key: {key!r}") from exc
        if not 1 <= leg <= NUM_LEGS:
            raise ExpertTipValidationError(f"Leg number out of range: {leg}")
        if not isinstance(value, list) or not value:
            raise ExpertTipValidationError(f"Leg {leg}: horses must be a non-empty list")
        horses: list[int] = []
        for item in value:
            try:
                horse = int(item)
            except (TypeError, ValueError) as exc:
                raise ExpertTipValidationError(f"Leg {leg}: invalid horse {item!r}") from exc
            horses.append(horse)
        if len(set(horses)) != len(horses):
            raise ExpertTipValidationError(f"Leg {leg}: duplicate horse numbers")
        legs[leg] = sorted(horses)
    missing = [leg for leg in range(1, NUM_LEGS + 1) if leg not in legs]
    if missing:
        raise ExpertTipValidationError(f"Missing legs: {missing}")
    return legs


def _tracks_match(a: str, b: str) -> bool:
    return _normalize_track(a) == _normalize_track(b)


def _normalize_track(name: str) -> str:
    return "".join(ch for ch in name.casefold() if ch.isalnum())


def _require_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ExpertTipValidationError(f"Missing or invalid field: {key}")
    return value.strip()


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return str(value)
    text = value.strip()
    return text or None
