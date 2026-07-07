# UC-30 — Maintain betting rules

| Field | Value |
|-------|-------|
| **ID** | UC-30 |
| **Status** | APPROVED |
| **Version** | 1.0 |
| **Reviewer** | Nisse |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Primary actor** | Trotting expert |
| **Implements** | FR-001, FR-050–051 |
| **Preconditions** | Research sources in `inbox/research/` |

## Brief description

Author, review, and publish ATG-aligned betting game rules.

## Main success scenario

1. Expert collects sources (ATG web, S-009a PDF, press releases) via UC-01.
2. **F-100** `draft_betting_rules` → `pending/research/PENDING-RESEARCH_<game>.md`.
3. Expert documents: schedule, legs, stake, payouts, system cost, edge cases, ATG entry notes.
4. Expert sets status `AWAITING_NISSE` → peer self-review → `APPROVED`.
5. **F-101** `promote_betting_rules` → `docs/betting/<game>.md` + archive in `outbox/research/`.
6. **F-081** `write_review_record` → `outbox/reviews/REVIEW_<game>_rules.md`.
7. **F-014** `log_trace_entry`.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 3a | Conflict with official ATG source | Flag discrepancy; Nisse reconciles before **P** |
| 3b | Payout rule change (e.g. 2026-07-02) | Document effective date and historical selector |

## Functions invoked

F-100, F-101, F-081, F-014

## Special requirements

- [SUP-C-001](../supplementary-specification.md#9-regulatory-and-compliance), [SUP-C-004](../supplementary-specification.md#9-regulatory-and-compliance)
- Completed example: [v85.md](../../betting/v85.md) v1.0

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | APPROVED — exemplified by v85.md v1.0 promotion workflow |