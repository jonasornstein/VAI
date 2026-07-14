# AIRUP Methodology (mandatory)

All VAI work follows **AIRUP**: **A**nalyze → **I**nbox → **R**eview ⇄ **U**pdate → **P**ublish.

Full spec: [docs/AIRUP.md](../../docs/AIRUP.md)

## Quick rules for agents

1. **Analyze first** — confirm game, date, mode, reviewer before generating.
2. **Raw inputs → `inbox/`** — race cards, odds, research notes, requests.
3. **Drafts → `pending/`** — never skip to `outbox/` without review.
4. **Update loops** — revise in `pending/` until `APPROVED`; log major changes in `docs/TRACE-LOG.md`.
5. **Publish → `outbox/`** — approved proposals, research, reviews only.

## Directory map

```
inbox/      → raw inputs (I)
pending/    → drafts awaiting review (R, U)
outbox/     → approved artifacts (P)
docs/       → long-lived published baseline
```

## Reviewers

| Artifact type | Reviewer |
|---------------|----------|
| Betting rules, trotting research | Nisse |
| Quant specs, odds-based proposals | Povl |
| V85 proposals for race day | Kricke / ornstein |

## Skills

- `/airup` — orchestrate full cycle
- `/airup-review` — review pending items
- `/generate-proposal`, `/v85-system`, `/research-trotting` — all embed AIRUP paths

## Forbidden

- Writing proposals directly to `outbox/` without approval
- Treating `docs/betting/` as approved when status is DRAFT
- Skipping `inbox/` when user provides raw race-card or odds files