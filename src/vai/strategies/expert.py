"""UC-12 — expert mode: load professional betslip tips (F-040–F-043)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from vai.cost import compute_cost_sek, format_cost_breakdown
from vai.io.expert_tips import (
    ExpertTipValidationError,
    default_tips_dir,
    find_expert_tip,
    list_expert_tips,
    load_expert_tip,
)
from vai.models.expert_tip import ExpertError, ExpertManifest, ExpertResult, ExpertTip
from vai.models.race_card import RaceCard

NUM_LEGS = 8


def generate_expert_v1(
    tip: ExpertTip | str | Path,
    *,
    race_card: RaceCard | None = None,
    overrides: Mapping[int, Sequence[int]] | None = None,
    tips_dir: str | Path | None = None,
) -> ExpertResult | ExpertError:
    """Load an expert tip (object, path, or tip_id) and return costed selections."""
    resolved = _resolve_tip(tip, tips_dir=tips_dir)
    if isinstance(resolved, ExpertError):
        return resolved

    selections = {leg: list(horses) for leg, horses in resolved.legs.items()}
    overridden: list[int] = []

    if overrides:
        for leg, horses in overrides.items():
            try:
                leg_num = int(leg)
            except (TypeError, ValueError):
                return ExpertError(
                    code="INVALID_OVERRIDE",
                    message=f"Invalid override leg: {leg!r}",
                )
            if not 1 <= leg_num <= NUM_LEGS:
                return ExpertError(
                    code="INVALID_OVERRIDE",
                    message=f"Override leg out of range: {leg_num}",
                )
            cleaned = sorted({int(h) for h in horses})
            if not cleaned:
                return ExpertError(
                    code="EMPTY_LEG",
                    message=f"Override left leg {leg_num} empty",
                    hint="Keep at least one horse per leg",
                )
            selections[leg_num] = cleaned
            overridden.append(leg_num)

    for leg in range(1, NUM_LEGS + 1):
        if not selections.get(leg):
            return ExpertError(code="EMPTY_LEG", message=f"Leg {leg} has no horses")

    if race_card is not None:
        card_error = _validate_against_race_card(selections, race_card)
        if card_error is not None:
            return card_error

    combinations, cost_sek = compute_cost_sek(selections)
    manifest = ExpertManifest(
        mode="expert",
        tip_id=resolved.tip_id,
        expert_id=resolved.expert_id,
        expert_name=resolved.expert_name,
        product_name=resolved.product_name,
        source_url=resolved.source_url,
        source_note=resolved.source_note,
        overridden_legs=tuple(sorted(overridden)),
    )
    return ExpertResult(
        selections=selections,
        combinations=combinations,
        cost_sek=cost_sek,
        cost_breakdown=format_cost_breakdown(selections),
        manifest=manifest,
        tip=resolved,
    )


def list_tips_for_day(
    *,
    date: str | None = None,
    track: str | None = None,
    tips_dir: str | Path | None = None,
):
    root = Path(tips_dir) if tips_dir is not None else default_tips_dir()
    return list_expert_tips(root, date=date, track=track)


def _resolve_tip(
    tip: ExpertTip | str | Path,
    *,
    tips_dir: str | Path | None,
) -> ExpertTip | ExpertError:
    if isinstance(tip, ExpertTip):
        return tip
    path = Path(tip)
    if path.suffix in {".yaml", ".yml"} and path.is_file():
        try:
            return load_expert_tip(path)
        except ExpertTipValidationError as exc:
            return ExpertError(code=exc.code, message=str(exc))
        except OSError as exc:
            return ExpertError(code="INVALID_TIP", message=str(exc))

    tip_id = str(tip)
    root = Path(tips_dir) if tips_dir is not None else default_tips_dir()
    try:
        return find_expert_tip(root, tip_id)
    except ExpertTipValidationError as exc:
        return ExpertError(code=exc.code, message=str(exc))


def _validate_against_race_card(
    selections: dict[int, list[int]],
    race_card: RaceCard,
) -> ExpertError | None:
    for leg in range(1, NUM_LEGS + 1):
        eligible = race_card.horses_for_leg(leg)
        scratches = set(race_card.leg_by_number(leg).scratches)
        for horse in selections[leg]:
            if horse in scratches:
                return ExpertError(
                    code="SCRATCHED_HORSE",
                    message=f"Leg {leg}: horse {horse} is scratched",
                    hint="Override the leg or pick another tip",
                )
            if horse not in eligible:
                return ExpertError(
                    code="INVALID_HORSE",
                    message=f"Leg {leg}: horse {horse} not on race card",
                    hint="Check transcription against startlista",
                )
    return None
