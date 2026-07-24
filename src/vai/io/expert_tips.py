"""F-040 — load and list expert tip YAML from inbox/expert-tips/."""

from __future__ import annotations

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


def load_expert_tip(path: str | Path) -> ExpertTip:
    tip_path = Path(path)
    data = yaml.safe_load(tip_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ExpertTipValidationError("Tip root must be a mapping")
    return parse_expert_tip(data, path=str(tip_path))


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
