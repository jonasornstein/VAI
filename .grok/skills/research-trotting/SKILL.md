---
name: research-trotting
description: Research and document Swedish trotting rules using AIRUP. Inbox sources, draft in pending/research, publish to outbox and docs after Nisse approval. Use for trav rules, ATG regulations, or /research-trotting.
argument-hint: "<topic or game>"
---

# Research Trotting (Nisse + AIRUP)

Research workflow for **Nisse's** domain, following **AIRUP**.

## AIRUP for research

| Phase | Action |
|-------|--------|
| **A** | Topic, game, target doc (`docs/betting/<game>.md`) |
| **I** | Sources → `inbox/research/` |
| **R** | Draft → `pending/research/` status `AWAITING_NISSE` |
| **U** | Nisse feedback incorporated |
| **P** | Approved → `outbox/research/` + promote to `docs/betting/` |

## Persona

**Nisse** — precise, official sources over folklore. Mark unverified `DRAFT`.

## Research sources (priority)

1. ATG betting regulations (official PDF)
2. [atg.se](https://www.atg.se) game pages
3. [travsport.se](https://www.travsport.se)
4. Existing `docs/betting/`

## Draft (R)

Update or create in `pending/research/` first. Header:

```markdown
| Status | AWAITING_NISSE |
| Target doc | docs/betting/v85.md |
```

## Publish (P)

On Nisse approval:

1. Copy to `outbox/research/`
2. Merge into canonical `docs/betting/` or `docs/strategies/expert.md`
3. Set status `APPROVED` in target doc
4. Log in `docs/TRACE-LOG.md`

## Handoff to Povl

Odds/payout math → open item in `docs/strategies/quantitative.md` for Povl.