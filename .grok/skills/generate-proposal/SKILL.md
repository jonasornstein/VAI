---
name: generate-proposal
description: Generate a betting system proposal for ATG trotting (V85 priority) following AIRUP. Draft to pending/; publish to outbox/ after approval. Use for betting system, proposal, spelsystem, or /generate-proposal.
argument-hint: "<mode> <game> <date> [options]"
---

# Generate Proposal (AIRUP)

Create a **betting system proposal** for manual ATG entry. Follows **AIRUP** — see `docs/AIRUP.md`.

## AIRUP flow for proposals

| Phase | Action |
|-------|--------|
| **A** | Confirm game, date, track, mode, reviewer (Kricke/ornstein) |
| **I** | Ingest race card → `inbox/race-cards/`; odds → `inbox/odds/` |
| **R** | Generate draft → `pending/proposals/<game>/` status `AWAITING_OPERATOR` |
| **U** | Revise from operator feedback |
| **P** | On APPROVED → `outbox/proposals/<game>/<date>-<track>/` |

## Before starting

1. Read `docs/betting/v85.md` (or relevant game doc).
2. Read `docs/strategies/<mode>.md`.
3. Read `docs/AIRUP.md` if unsure of workflow.

## Generate (R)

### Inputs

| Input | Source |
|-------|--------|
| Race card | `inbox/race-cards/` or user paste (save to inbox first) |
| Mode params | Strategy doc (budget, seed, template, odds) |

Do not invent horse numbers.

### Strategy

- **random** — `docs/strategies/random.md`
- **expert** — `docs/strategies/expert.md`
- **quantitative** — `docs/strategies/quantitative.md` → also `AWAITING_POVL` if odds/model used

### Validate

```
combinations = product of horse counts per leg
cost_sek = combinations × 0.50   # V85
```

### Draft output (`pending/proposals/`)

```
pending/proposals/<game>/<YYYY-MM-DD>-<track>/
  proposal.md      # Status: AWAITING_OPERATOR
  manifest.yaml
```

Use template in `.grok/rules/03-documentation.md`.

## Publish (P)

Only after operator approval (or explicit user "approve and publish"):

```
outbox/proposals/<game>/<YYYY-MM-DD>-<track>/
```

Run `/airup-review` if review is formal.

## Present to user

- Leg-by-leg table, cost, mode, rationale
- Path in `pending/` (draft) or `outbox/` (published)
- Reminder: enter manually at atg.se

## Do not

- Write directly to `outbox/` without approval
- Automate bet placement
- Fabricate race cards