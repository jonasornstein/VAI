	# ATG — Software Requirements Specification

| Field | Value |
|-------|-------|
| **Version** | 0.2 |
| **Status** | DRAFT |
| **Last updated** | 2026-07-06 |
| **Methodology** | [AIRUP](./AIRUP.md) |
| **Author** | Jonte (owner), M-005 (draft) |

---

## 1. Introduction

### 1.1 Purpose

Specify requirements for software that **generates betting system proposals** for Swedish trotting at ATG, starting with **V85**.

### 1.2 Scope

**In scope:**

- Documentation of trotting and ATG betting rules
- Three proposal generation modes: random, expert, quantitative
- V85 as first supported game
- Human-readable proposal output for manual ATG entry
- System cost and combination count calculation

**Out of scope:** See [VISION.md](./VISION.md) non-goals (NG-001–NG-004).

### 1.3 Definitions

| Term | Definition |
|------|------------|
| **Proposal** | A complete multi-leg horse selection with metadata and cost |
| **Leg / avdelning** | One race within a pool (V85: 8 legs) |
| **System** | Product of selections across legs; each combination is one row |
| **Mode** | `random`, `expert`, or `quantitative` generation strategy |
| **AIRUP** | Analyze → Inbox → Review → Update → Publish workflow |
| **inbox/** | Raw inputs awaiting processing |
| **pending/** | Draft artifacts awaiting review |
| **outbox/** | Approved, published artifacts |

---

## 2. Stakeholders

See [ROSTER.md](./ROSTER.md).

---

## 3. Functional requirements

### 3.0 AIRUP workflow

| ID      | Requirement                                                             | Priority | Owner |
| ------- | ----------------------------------------------------------------------- | -------- | ----- |
| FR-000  | All artifacts SHALL follow AIRUP per [AIRUP.md](./AIRUP.md)             | Must     | Jonte |
| FR-001a | Raw inputs SHALL be stored under `inbox/` before processing             | Must     | M-005 |
| FR-001b | Drafts SHALL be written to `pending/` with explicit review status       | Must     | M-005 |
| FR-001c | Only `APPROVED` artifacts SHALL be published to `outbox/`               | Must     | Jonte |
| FR-001d | Significant decisions SHALL be logged in [TRACE-LOG.md](./TRACE-LOG.md) | Should   | Jonte |

### 3.1 Documentation

| ID | Requirement | Priority | Owner |
|----|-------------|----------|-------|
| FR-001 | Maintain `docs/betting/v85.md` with ATG-aligned V85 rules | Must | Nisse |
| FR-002 | Maintain strategy specs under `docs/strategies/` | Must | Povl / Nisse |
| FR-003 | Version and change-log major docs | Should | Jonte |

### 3.2 Proposal generation — common

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-010 | Support game parameter (default `v85`) | Must |
| FR-011 | Accept race card input (leg → list of horse numbers) | Must |
| FR-012 | Draft proposals under `pending/proposals/`; published under `outbox/proposals/<game>/<date>/` | Must |
| FR-013 | Compute combination count = ∏(horses per leg) | Must |
| FR-014 | Compute cost = combinations × min stake (0.50 SEK for V85) | Must |
| FR-015 | Record mode, timestamp, and inputs in proposal manifest | Must |
| FR-016 | Reject invalid horse numbers not on race card | Must |

### 3.3 Random mode

| ID | Requirement | Priority | Owner |
|----|-------------|----------|-------|
| FR-020 | Select horses per leg using configurable random policy | Must | Povl |
| FR-021 | Support constraints: max horses per leg, max total cost | Should | Povl |
| FR-022 | Seedable RNG for reproducibility | Should | Povl |

### 3.4 Expert mode

| ID | Requirement | Priority | Owner |
|----|-------------|----------|-------|
| FR-030 | Apply expert-system templates (e.g. spik + gardering patterns) | Must | Nisse |
| FR-031 | Document expert rules in `docs/strategies/expert.md` | Must | Nisse |
| FR-032 | Allow manual override of expert picks per leg | Should | Kricke/Jonte |

### 3.5 Quantitative mode

| ID | Requirement | Priority | Owner |
|----|-------------|----------|-------|
| FR-040 | Accept probability or odds inputs per horse | Must | Povl |
| FR-041 | Support Monte Carlo or equivalent simulation for leg outcomes | Should | Povl |
| FR-042 | Document model assumptions and limitations | Must | Povl |
| FR-043 | Optional: optimize selections under cost budget | Could | Povl |

### 3.6 V85-specific

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-050 | Exactly 8 legs per V85 proposal | Must |
| FR-051 | Consolation payout rules documented (not calculated in v1 unless Povl specifies) | Should |

---

## 4. Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR-001 | Proposals readable in under 2 minutes by Kricke/Jonte |
| NFR-002 | No network calls required for core generation (offline-capable) |
| NFR-003 | Grok agents load project context from `AGENTS.md` and `.grok/rules/` |
| NFR-004 | Code structured for adding games without rewriting core |
| NFR-005 | Agents SHALL follow AIRUP; skills `/airup` and `/airup-review` available |

---

## 5. External interfaces

| Interface | Description |
|-----------|-------------|
| **ATG website** | Manual entry only — no API integration in v1 |
| **Race card** | `inbox/race-cards/` (format TBD) |
| **Grok skills** | `/airup`, `/airup-review`, `/generate-proposal`, `/v85-system`, `/research-trotting` |

---

## 6. Acceptance criteria (v1)

1. Three modes each produce a valid V85 proposal for a sample race card.
2. Nisse signs off on `docs/betting/v85.md` (status → APPROVED).
3. Povl signs off on quantitative requirements in FR-040–FR-043. *(Agent review 2026-07-06 — [quantitative.md](./strategies/quantitative.md) v0.3 APPROVED)*
4. Kricke or Jonte confirms one real Saturday proposal is enterable at ATG.

---

## 7. Open items (TBD)

| Item | Waiting on |
|------|------------|
| Race card file format | Povl / implementation |
| Expert template catalog | Nisse |
| Monte Carlo spec | Povl |
| Reduced-stake V85 rules detail | ~~Nisse~~ → documented in v85.md + quantitative.md |

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.2 | 2026-07-06 | AIRUP workflow requirements (§3.0); path updates |
| 0.1 | 2026-07-06 | Initial SRS from scaffold |