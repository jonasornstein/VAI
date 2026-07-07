"""F-023 — format proposal markdown artifact."""

from __future__ import annotations

from datetime import datetime, timezone

import yaml

from atg.models.proposal import RandomManifest, RandomResult
from atg.models.race_card import RaceCard


def format_proposal_markdown(
    race_card: RaceCard,
    result: RandomResult,
    *,
    stake_budget_sek: float,
) -> str:
    manifest = result.manifest
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    legs_rows = "\n".join(
        f"| {leg} | {race_card.leg_by_number(leg).race_label} | "
        f"{_format_horses(result.selections[leg])} | {_leg_note(race_card, leg, result.selections[leg])} |"
        for leg in range(1, 9)
    )
    checklist = _operator_checklist(race_card, result)
    manifest_yaml = yaml.safe_dump(
        {
            "mode": manifest.mode,
            "seed": manifest.seed,
            "constraints": {
                "stake_budget_sek": manifest.stake_budget_sek,
                "min_horses_per_leg": manifest.min_horses_per_leg,
                "max_horses_per_leg": manifest.max_horses_per_leg,
                "max_shrink_steps": manifest.max_shrink_steps,
                "shrink_steps_used": manifest.shrink_steps_used,
                "weight_by_field_size": manifest.weight_by_field_size,
            },
        },
        sort_keys=False,
    ).strip()

    return f"""# V85 Proposal — {race_card.track} — {race_card.date}

| Field | Value |
|-------|-------|
| Mode | random |
| AIRUP status | AWAITING_OPERATOR |
| Generated | {generated} |
| SYSTEMKOSTNAD | {stake_budget_sek:.2f} SEK |
| Total cost | {result.cost_sek:.2f} SEK |
| Combinations | {result.combinations} |
| Cost breakdown | {result.cost_breakdown} |

## Legs

| Leg | Race | Horses | Notes |
|-----|------|--------|-------|
{legs_rows}

## Operator checklist (UC-20)

{checklist}

## Rationale

Hari (random): operator marks locked; slumpen fyller på till exakt SYSTEMKOSTNAD ({result.shrink_steps_used} hästar tillagda av slumpen).

## Manifest

```yaml
{manifest_yaml}
```
"""


def _format_horses(horses: list[int]) -> str:
    return ", ".join(str(h) for h in horses)


def _leg_note(race_card: RaceCard, leg: int, horses: list[int]) -> str:
    leg_data = race_card.leg_by_number(leg)
    if len(horses) == 1:
        kind = "Spik"
    else:
        kind = f"Gardering ({len(horses)})"
    parts = [kind]
    if leg_data.reserves:
        parts.append(f"Reserver: {', '.join(str(r) for r in leg_data.reserves)}")
    if leg_data.scratches:
        parts.append(f"Strukna: {', '.join(str(s) for s in leg_data.scratches)}")
    return "; ".join(parts)


def _operator_checklist(race_card: RaceCard, result: RandomResult) -> str:
    legs_ok = all(result.selections.get(leg) for leg in range(1, 9))
    cost_ok = result.cost_sek <= result.manifest.stake_budget_sek + 0.001
    horses_ok = all(
        set(result.selections[leg]).issubset(race_card.horses_for_leg(leg))
        for leg in range(1, 9)
    )
    scratch_ok = all(
        not (set(result.selections[leg]) & set(race_card.leg_by_number(leg).scratches))
        for leg in range(1, 9)
    )
    rows = [
        ("8 avdelningar ifyllda", legs_ok),
        ("Kostnad verifierad mot ATG-formel", cost_ok),
        ("Inga ogiltiga hästnummer", horses_ok),
        ("Inga strukna hästar valda", scratch_ok),
        ("Operator godkänner för ATG-inmatning", False),
    ]
    return "\n".join(
        f"- [{'x' if ok else ' '}] {label}" for label, ok in rows
    )