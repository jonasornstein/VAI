# Scope Lock — v1 Random Mode

| Field | Value |
|-------|-------|
| **Version** | 0.1 |
| **Status** | APPROVED |
| **AIRUP phase** | R |
| **Reviewer** | ornstein |
| **Author** | Assistant |
| **Last updated** | 2026-07-07 |
| **Source request** | [inbox/requests/2026-07-07-v1-random-manual-yaml.md](../../inbox/requests/2026-07-07-v1-random-manual-yaml.md) |

---

## 1. Decision summary

**v1 delivers one working path:** operator loads a **manual YAML race card**, marks horse pools per leg, sets **SYSTEMKOSTNAD** (default 500 SEK), and generates a **Random-mode** V85 proposal within budget.

| Decision | v1 choice | Deferred |
|----------|-----------|----------|
| Generation mode | **Random only** (UC-11) | Expert (UC-12), Quantitative (UC-13) |
| Default mode in UX | **Random** | — |
| Race card ingestion | **Manual YAML** (`inbox/race-cards/`) | ATG auto-fetch (UC-09, F-006–F-009) |
| Game | **V85** | V86, V64, DD (V75 discontinued at ATG) |
| Output | Proposal artifact in `pending/` → `outbox/` after operator approval | Web app / ATG integration |

This document **supersedes** conflicting v1 assumptions in [ux-workflow.md](../../docs/requirements/ux-workflow.md) (mode default) and [race-card-schema.md](../../docs/requirements/race-card-schema.md) (primary ingestion) **for implementation planning only**. Canonical requirements docs are updated after **APPROVED** promotion.

---

## 2. v1 in scope

### 2.1 Product

- V85 betting system proposals via **random** selection from operator horse pools.
- Correct **system cost** and **combination count** (ATG formula: ∏(horses per leg) × 0.50 SEK).
- **Reproducible** runs when `seed` is set (F-032).
- **Budget constraint:** computed cost ≤ SYSTEMKOSTNAD, with retry policy per UC-11 (max 10 retries, F-031).
- Human-readable proposal format for Kricke/ornstein manual ATG entry ([AGENTS.md](../../AGENTS.md) proposal template).
- Optional basic hit summary when odds are present (F-052 — best-effort in v1).

### 2.2 Data

- Race cards as YAML per [race-card-schema.md](../../docs/requirements/race-card-schema.md) with `source: manual`.
- File location: `inbox/race-cards/<YYYY-MM-DD>-<track>.yaml`.
- Validation: 8 legs, eligible `horses` per leg, V85 game tag.

### 2.3 UX (mockup alignment)

- **Läge / mode tabs:** Random (active, default), Expert and Quantitative **visible but disabled** — label e.g. *Kommer senare*.
- Horse pool toggles per leg (operator marks candidates before generation).
- SYSTEMKOSTNAD field, default **500 SEK**.
- Slip preview with leg selections and computed cost.

### 2.4 Implementation (`src/`)

Minimum vertical slice (CLI acceptable for v1):

| Module | Responsibility |
|--------|----------------|
| `models` | `RaceCard`, leg, proposal types |
| `cost` | F-061 combination count and SEK cost |
| `io` | Load/validate YAML race card |
| `strategies/random` | UC-11 algorithm |
| `cli` or thin entrypoint | Load card → pools → budget → emit proposal |

### 2.5 Documentation & AIRUP

- Close Povl open items in [random.md](../../docs/strategies/random.md) → `pending/specs/random-v1.md` (step 2).
- Sample race card in `inbox/race-cards/` + golden test with fixed seed (step 5).
- First end-to-end proposal through `pending/proposals/` → operator review (step 7).

---

## 3. v1 out of scope (explicitly deferred)

| Item | Requirement refs | Notes |
|------|------------------|-------|
| Expert mode implementation | UC-12, F-040–F-043 | UX tab only; no generator |
| Quantitative mode implementation | UC-13, F-050–F-054, F-053 optimizer | UX tab only; `quantitative.md` remains approved spec for later |
| ATG schedule fetch | F-006, F-027, F-028, UC-09 | No live DATUM/BANA dropdown from ATG in v1 |
| ATG race card auto-fetch | F-007, F-008, SUP-F-008 | Manual YAML is **primary** for v1; fetch spec → `pending/specs/atg-data-source.md` later |
| ATG odds auto-fetch | F-009 | Optional manual odds file if needed for F-052 |
| Web UI / hosted app | SUP-U-* | Mockup remains reference; v1 may be CLI + static mockup |
| Automated bet placement | NG-001, NG-004 | Permanent non-goal |
| Games beyond V85 | Phase 5 roadmap | — |

**Requirements preservation:** UC-12, UC-13, expert/quant strategy docs, and ATG-fetch functions stay in the requirements catalog. They are **frozen for implementation**, not deleted.

---

## 4. Active use cases and functions (v1)

| ID | Role in v1 |
|----|------------|
| UC-10 | Configure proposal (pools, SYSTEMKOSTNAD) — simplified without live ATG |
| UC-11 | **Primary** generation path |
| UC-14 | Emit proposal artifact |
| UC-20 | Operator review checklist |
| F-001–F-005 | Load/save race card and proposal I/O |
| F-020–F-026 | Operator pools, budget input |
| F-030–F-032 | Random selection, constraints, seed |
| F-060–F-062 | Cost and combination math |
| F-052 | Hit summary (optional) |

**Inactive in v1:** UC-09, UC-12, UC-13, F-006–F-009, F-040–F-043, F-050–F-054.

---

## 5. Open items (resolve before or during step 2)

| ID | Question | Owner | Default if silent |
|----|----------|-------|-----------------|
| SL-001 | Default `max_horses_per_leg` for V85 random | Povl | **Resolved** → [random-v1.md](./random-v1.md): `max = \|pool\|` per leg |
| SL-002 | Budget retry policy when over SYSTEMKOSTNAD | Povl | **Resolved** → greedy shrink, max 10 steps |
| SL-003 | Weight selection by field size? | Povl | **Resolved** → no weighting |
| SL-004 | Mockup: disabled Expert/Quant copy | ornstein | *Kommer senare* + `aria-disabled` |
| SL-005 | v1 interface: CLI only vs minimal local UI | ornstein | CLI first; mockup unchanged until UI sprint |

---

## 6. Implementation sequence (post-approval)

| Step | Deliverable | AIRUP path |
|------|-------------|------------|
| **1** ✓ | This scope lock + TRACE-LOG | `pending/specs/` |
| **2** ✓ | Random v1 spec (resolve SL-001–SL-003) | [random-v1.md](./random-v1.md) → Povl review |
| **3** ✓ | `src/atg/` vertical slice | [src/](../../src/) — 13 tests passing |
| **4** | Sample YAML + golden test | `inbox/race-cards/`, `src/tests/` |
| **5** ✓ | Mockup tweak: Random default; disabled tabs | [v85-proposal-ux-mockup-atg.html](../mockups/v85-proposal-ux-mockup-atg.html) v0.5 |
| **6** ✓ | First proposal on real card | [proposal.md](../proposals/v85/2026-07-05-halmstad/proposal.md) + [review](../reviews/REVIEW_proposal_2026-07-05-halmstad.md) |

---

## 7. Success criteria (v1)

- [x] Scope lock **APPROVED** by ornstein
- [x] Random generator produces valid 8-leg proposal from manual YAML
- [x] Cost matches ATG formula for 3+ golden examples
- [x] Fixed seed reproduces identical selections
- [x] Budget cap enforced per UC-11
- [x] ornstein confirms proposal transcribable to ATG UI

---

## 8. Promotion checklist (when APPROVED)

On **APPROVED**, update canonical docs:

| Document | Change |
|----------|--------|
| [VISION.md](../../docs/VISION.md) | v1 success criteria; roadmap Phase 3 narrowed to random-first |
| [ux-workflow.md](../../docs/requirements/ux-workflow.md) | Default mode → Random; note deferred modes |
| [race-card-schema.md](../../docs/requirements/race-card-schema.md) | v1 primary ingestion = manual YAML |
| [functions.md](../../docs/requirements/functions.md) | Mark v1 Must vs Deferred functions |
| [TRACE-LOG.md](../../docs/TRACE-LOG.md) | Log promotion |

Copy approved scope lock to `outbox/specs/scope-lock-v1-random.md`.

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-07-07 | Initial scope lock — random-only, manual YAML (ornstein direction) |