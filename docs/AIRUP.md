# AIRUP — Project Methodology

| Field | Value |
|-------|-------|
| **Version** | 1.1 |
| **Status** | APPROVED (project standard) |
| **Last updated** | 2026-07-06 |
| **Requirements model** | IBM RUP — see [requirements/README.md](./requirements/README.md) |
| **Owner** | ornstein |

**AIRUP** is the mandatory workflow for all VAI project work — documentation, research, proposals, and implementation. Every artifact moves through five phases in order. Do not skip phases.

---

## The five phases

| Phase | Name | Purpose | Primary location |
|-------|------|---------|------------------|
| **A** | **Analyze** | Scope the task, identify game/date/mode, check existing docs and prior artifacts, assign reviewer | Analysis in task or `pending/reviews/` |
| **I** | **Inbox** | Capture raw, unprocessed inputs — no generation yet | `inbox/` |
| **R** | **Review** | Produce drafts; hold for expert/operator approval | `pending/` |
| **U** | **Update** | Revise from feedback; log changes | `pending/` → loop back to **R** |
| **P** | **Publish** | Release approved artifacts for use on race day | `outbox/` |

```
Analyze → Inbox → Review ⇄ Update → Publish
                      ↑_______|
```

---

## Phase details

### A — Analyze

Before creating or changing anything:

1. What **game** (default V85), **date**, **track**, and **mode** (random / expert / quantitative)?
2. Who **reviews**? Nisse (rules), Povl (math), Kricke/ornstein (usability)
3. What already exists in `docs/`, `outbox/`, or `inbox/` for this topic?
4. Is this new work, a revision, or a race-day run?

Output: clear scope statement. Complex tasks get a short analysis header in the pending artifact.

### I — Inbox

All **raw inputs** land in `inbox/` — never edit in place; copy/process into pending.

| Subfolder | Contents |
|-----------|----------|
| `inbox/race-cards/` | Start lists, leg assignments (CSV, YAML, paste) |
| `inbox/odds/` | Odds exports, probability sheets |
| `inbox/research/` | Links, PDFs, notes for Nisse |
| `inbox/requests/` | Task requests, user briefs |

Large or sensitive files: use `inbox/` subfolders listed in `.gitignore`.

### R — Review

Draft artifacts go to `pending/` with status **AWAITING_REVIEW**.

| Subfolder | Contents | Default reviewer |
|-----------|----------|------------------|
| `pending/proposals/` | Draft betting systems | Kricke / ornstein |
| `pending/research/` | Draft rules / trotting docs | Nisse |
| `pending/requirements/` | Draft use cases, vision, supplementary spec (RUP) | ornstein / per UC |
| `pending/specs/` | Draft implementation / quant specs | Povl |
| `pending/reviews/` | Review packets (like Titan INBOX-REVIEW) | Per packet |

**Naming:** `PENDING-<TYPE>_<game>_<date>_<track>.md` or folder equivalent.

**Status values:** `AWAITING_NISSE` | `AWAITING_POVL` | `AWAITING_OPERATOR` | `APPROVED`

### U — Update

When a reviewer requests changes:

1. Edit the artifact in `pending/`
2. Increment version or add revision note in the file
3. Log significant decisions in [TRACE-LOG.md](./TRACE-LOG.md)
4. Return to **R** until status is `APPROVED`

### P — Publish

On approval:

1. Copy (or move) artifact to `outbox/` with publish timestamp
2. Write review record to `outbox/reviews/` if applicable
3. **Promote** stable rules to `docs/` when research is finalized (Nisse for betting, Povl for strategies)
4. **Promote** approved RUP requirements to `docs/requirements/`, `docs/VISION.md` (ornstein / per-UC reviewers)
5. Operators (Kricke/ornstein) use **`outbox/proposals/`** on race day

**Never** place unreviewed drafts in `outbox/`.

---

## AIRUP mapping for ATG roles

| Role | AIRUP involvement |
|------|-------------------|
| **Nisse** | Reviews `pending/research/`; approves betting rule changes before **P** → `docs/betting/` |
| **Povl** | Reviews `pending/specs/` and quantitative proposals; approves math |
| **Kricke / ornstein** | Review `pending/proposals/`; accept before **P** |
| **Agents** | Execute A→I→R; facilitate U; **P** only after explicit or documented approval |

---

## Canonical vs. workflow directories

| Directory | Role in AIRUP |
|-----------|---------------|
| `inbox/` | **I** — raw inputs |
| `pending/` | **R**, **U** — drafts and revisions |
| `outbox/` | **P** — approved artifacts |
| `docs/` | Long-lived **published** baseline (RUP requirements, VISION, approved rules) |
| `src/` | Implementation (follows same AIRUP for specs → code) |

---

## Gates

| Gate | Condition |
|------|-----------|
| **Review gate** | No move to `outbox/` while status ≠ `APPROVED` |
| **Rules gate** | No `docs/betting/*.md` promotion without Nisse |
| **Quant gate** | No quantitative proposal **P** without Povl review if odds/model used |
| **Operator gate** | V85 proposals for race day require Kricke or ornstein **P** approval |
| **Requirements gate** | New `UC-*` / `SUP-*` IDs promoted from `pending/requirements/` only when APPROVED |

---

## RUP requirements workflow

Requirements follow IBM RUP, integrated with AIRUP:

```
Vision ────────────── docs/VISION.md
Use cases ─────────── docs/requirements/use-cases/   (draft: pending/requirements/)
Supplementary (FURPS+) docs/requirements/supplementary-specification.md
Index / traceability ─ docs/SRS.md
```

| RUP artifact | AIRUP path | Reviewer |
|--------------|------------|----------|
| Vision | `pending/requirements/` → `docs/VISION.md` | ornstein |
| Use-case spec | `pending/requirements/use-cases/` → `docs/requirements/use-cases/` | Per actor (operator / Nisse / Povl) |
| Supplementary | `pending/requirements/` → `docs/requirements/supplementary-specification.md` | ornstein + domain expert as needed |
| Implementation | `pending/specs/` → `src/` | Povl |

Use cases replace monolithic `FR-*` statements. Cross-cutting quality attributes live in the supplementary spec (`SUP-*`).

---

## Related skills

| Skill | AIRUP coverage |
|-------|----------------|
| `/airup` | Full cycle orchestration |
| `/airup-review` | **R** and **U** for pending items |
| `/generate-proposal` | **I**→**R** for proposals (→ **P** after approval) |
| `/v85-system` | V85-specific proposal path |
| `/research-trotting` | **I**→**R** for Nisse research |

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.1 | 2026-07-06 | RUP requirements workflow; `pending/requirements/` |
| 1.0 | 2026-07-06 | AIRUP adopted as project methodology |