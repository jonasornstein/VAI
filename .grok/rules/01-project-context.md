# Project Context — ATG Trotting Betting Systems

## Mission

Help Kricke and Jonte generate well-structured **betting system proposals** for Swedish trotting at ATG, with **V85** as the first priority game.

## Methodology: AIRUP

**A**nalyze → **I**nbox → **R**eview ⇄ **U**pdate → **P**ublish. See `docs/AIRUP.md`.

## What we build

| Output | Description | AIRUP path |
|--------|-------------|------------|
| **Proposal** | Horse selections across legs with cost | `pending/` → `outbox/proposals/` |
| **Documentation** | Trotting rules (Nisse), quant specs (Povl) | `pending/` → `docs/` |
| **Tools** | Generators in `src/` | spec in `pending/specs/` first |

## What we do not build

- ATG account integration or automated bet submission
- Guaranteed-profit systems or financial advice

## Strategy modes

1. **Random** — unbiased or constrained random selection per leg
2. **Expert** — patterns from professional trotting experts' published or internal systems
3. **Quantitative** — mathematical models (e.g. Monte Carlo, probability estimates, value betting)

## Key Swedish / ATG terms

| Term | Meaning |
|------|---------|
| Trav / Trotting | Harness racing — horses pull a sulky |
| Avdelning | Leg / division in a multi-race pool (V85 has 8) |
| System | A combination bet covering multiple horses per leg |
| Rad | Row in a system matrix |
| Spik | Single-horse lock in a leg |
| Gardering | Multiple horses marked in a leg |
| Utdelning | Payout / dividend |

## Session checklist for agents

1. **A** — Confirm game, date/track, mode, reviewer.
2. **I** — Save raw inputs to `inbox/`.
3. Load `docs/betting/<game>.md` and `docs/strategies/<mode>.md`.
4. **R** — Draft to `pending/` with review status.
5. **U** — Revise until approved.
6. **P** — Publish to `outbox/` only when `APPROVED`.