---
name: v85-system
description: Generate a V85 Pick8 betting system for a Saturday race day using AIRUP. Draft to pending/; publish to outbox/ after approval. Use for V85, Saturday trav, spelv85, or /v85-system.
argument-hint: "<YYYY-MM-DD> <track> [mode] [budget]"
---

# V85 System Generator (AIRUP)

V85-focused path through **AIRUP**. Full methodology: `docs/AIRUP.md`.

## V85 rules

| Rule | Value |
|------|-------|
| Legs | 8 |
| Min stake | 0.50 SEK / combination |
| Cost | ∏(horses per leg) × 0.50 SEK |

Details: `docs/betting/v85.md`

## AIRUP for V85

| Phase | V85 action |
|-------|------------|
| **A** | Saturday date, track, mode, budget |
| **I** | Race card → `inbox/race-cards/<date>-<track>.yaml` |
| **R** | Draft → `pending/proposals/v85/<date>-<track>/` |
| **U** | Operator tweaks (spik/gardering) |
| **P** | Approved → `outbox/proposals/v85/<date>-<track>/` |

## Build system (R)

| Mode | Doc |
|------|-----|
| random | `docs/strategies/random.md` |
| expert | `docs/strategies/expert.md` |
| quantitative | `docs/strategies/quantitative.md` |

Show cost calculation explicitly.

## Operator checklist (include in draft)

- [ ] 8 avdelningar
- [ ] ATG cost matches proposal
- [ ] Scratches checked race day (Nisse rules — see `docs/betting/v85.md`)

## Handoff

- Review: `/airup-review`
- Full cycle: `/airup`