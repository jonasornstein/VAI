---
name: airup-review
description: Review pending VAI artifacts in the AIRUP Review and Update phases. Use for expert sign-off, operator acceptance, pending items, or /airup-review.
argument-hint: "<pending artifact path or ID>"
---

# AIRUP Review

Handle **R** (Review) and **U** (Update) for items in `pending/`.

## Steps

### 1. Locate artifact

- User path, or scan `pending/proposals/`, `pending/research/`, `pending/specs/`
- Read status header: `AWAITING_NISSE` | `AWAITING_POVL` | `AWAITING_OPERATOR`

### 2. Apply reviewer lens

| Reviewer | Check |
|----------|-------|
| **Nisse** | ATG rules correct? Edge cases? Terminology? |
| **Povl** | Math correct? Cost formula? Model assumptions stated? |
| **Kricke / ornstein** | Enterable at atg.se? All 8 legs? Cost matches? |

### 3. Produce review packet

Write to `pending/reviews/` or inline in artifact:

```markdown
# Review — <artifact name>

| Field | Value |
|-------|-------|
| Reviewer | Nisse / Povl / Operator |
| Date | <ISO> |
| Verdict | APPROVE \| REVISE \| REJECT |

## Findings

- [ ] …

## Required changes (if REVISE)

1. …
```

### 4. Update (U) or Publish (P)

| Verdict | Action |
|---------|--------|
| **REVISE** | Edit artifact in `pending/`; status → awaiting same reviewer |
| **APPROVE** | Status → `APPROVED`; run **P**: copy to `outbox/` |
| **REJECT** | Status → `REJECTED`; note in TRACE-LOG; do not publish |

### 5. Publish on APPROVE

- Proposal → `outbox/proposals/`
- Research → `outbox/research/` (+ promote to `docs/` if canonical)
- Review record → `outbox/reviews/`
- Log in `docs/TRACE-LOG.md` if significant

## Simulate reviewer

If user says "review as Nisse" or "review as Povl", adopt that persona from `.grok/rules/02-personas.md` and produce findings — but mark as **agent review** unless user is the named expert.