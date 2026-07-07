---
name: airup
description: Orchestrate the AIRUP methodology (Analyze, Inbox, Review, Update, Publish) for ATG project work. Use when starting tasks, processing inputs, or when the user mentions AIRUP, workflow, or /airup.
argument-hint: "<task description>"
---

# AIRUP Orchestrator

Run the **AIRUP** cycle for any ATG task. Full spec: `docs/AIRUP.md`.

## Phases

| Phase | Action |
|-------|--------|
| **A** Analyze | Scope game/date/mode; identify reviewer; check `docs/`, `inbox/`, `outbox/` |
| **I** Inbox | Save raw inputs to `inbox/<type>/` |
| **R** Review | Create draft in `pending/<type>/` with status `AWAITING_*` |
| **U** Update | Revise from feedback; loop to R until `APPROVED` |
| **P** Publish | Copy to `outbox/`; promote stable rules to `docs/`; log in `docs/TRACE-LOG.md` |

## Steps

### 1. Analyze (A)

Answer:

- Game? (default V85)
- Date / track?
- Mode? (random / expert / quantitative)
- Artifact type? (proposal / research / spec)
- Who reviews? (Nisse / Povl / Kricke / Jonte)

### 2. Inbox (I)

If user provides raw files or paste:

- Race card → `inbox/race-cards/`
- Odds → `inbox/odds/`
- Research sources → `inbox/research/`
- Task brief → `inbox/requests/`

### 3. Review draft (R)

Create in `pending/`:

- Proposals → `pending/proposals/`
- Rules research → `pending/research/`
- Quant specs → `pending/specs/`

Header must include:

```markdown
| Status | AWAITING_NISSE | (or POVL / OPERATOR)
| AIRUP phase | R |
| Reviewer | <name> |
```

### 4. Update (U)

On feedback: edit in `pending/`, add revision note, set status back to awaiting review.

### 5. Publish (P)

Only when `APPROVED`:

- Proposals → `outbox/proposals/<game>/<date>-<track>/`
- Research → `outbox/research/` + update `docs/betting/` if canonical
- Write `outbox/reviews/<review-id>.md`

Tell user what was published and where.

## Delegate to specialized skills

| Task | Skill |
|------|-------|
| Betting proposal | `/generate-proposal` or `/v85-system` |
| Trotting rules | `/research-trotting` |
| Review pending item | `/airup-review` |

## Do not

- Skip to `outbox/` without approval
- Skip `inbox/` when raw inputs exist