# Documentation Standards

## Principles

1. **Single source of truth** — each fact lives in one canonical doc; link elsewhere.
2. **Owner attribution** — betting rules: Nisse; quant/strategy math: Povl; requirements: product owner.
3. **Status markers** — use `DRAFT`, `REVIEW`, `APPROVED` in doc headers where content awaits expert sign-off.
4. **Change log** — significant docs (SRS, ROSTER, betting rules) include a version table at the bottom.

## File naming

- Lowercase with hyphens: `trotting-fundamentals.md`
- Game-specific: `docs/betting/v85.md`, future `v75.md`, etc.
- Strategy-specific: `docs/strategies/<mode>.md`

## RUP requirements (replaces monolithic SRS)

| Artifact | Canonical path | Draft path |
|----------|----------------|------------|
| Vision | `docs/VISION.md` | `pending/requirements/` |
| Use-case model & specs | `docs/requirements/` | `pending/requirements/use-cases/` |
| Supplementary (FURPS+) | `docs/requirements/supplementary-specification.md` | `pending/requirements/` |
| Index / traceability | `docs/SRS.md` | — |

New functional requirements use **`UC-*`** IDs and step-by-step narratives — not `FR-*` bullet lists.

## Required sections for betting game docs

Each `docs/betting/<game>.md` should eventually contain:

1. Overview and schedule
2. Leg structure (how many races, how selected)
3. Stake rules (minimum, reduced-stake variants if any)
4. Payout structure (8 correct, consolation for 7/6/5)
5. System cost formula with examples
6. ATG entry notes for Kricke/Jonte
7. Edge cases (scratches, late withdrawals, reserves) — Nisse
8. References to official ATG materials

## Required sections for proposal output

**AIRUP paths:**

- Draft proposals: `pending/proposals/<game>/<date>-<track>/`
- Published proposals: `outbox/proposals/<game>/<date>-<track>/`

Each proposal should include:

```markdown
# V85 Proposal — <track> — <YYYY-MM-DD>

| Field | Value |
|-------|-------|
| Mode | random \| expert \| quantitative |
| AIRUP status | AWAITING_* \| APPROVED |
| Generated | <ISO timestamp> |
| Total cost | <SEK> |
| Combinations | <count> |

## Legs

| Leg | Horses | Notes |
|-----|--------|-------|
| 1 | 3, 7, 12 | … |

## Rationale

<Brief explanation per mode>
```

## Do not

- Create new markdown files unless asked or a clear gap exists in the doc map (see AGENTS.md).
- Copy official ATG regulation PDFs into the repo without permission review.
- Present DRAFT rules as final without marking them.