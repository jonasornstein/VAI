# UC-21 — Publish proposal

| Field | Value |
|-------|-------|
| **ID** | UC-21 |
| **Status** | APPROVED |
| **Version** | 1.0 |
| **Reviewer** | ornstein |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Primary actor** | Agent |
| **Preconditions** | Proposal status = `APPROVED` |

## Brief description

Publish approved proposal to `outbox/proposals/` for race-day use.

## Main success scenario

1. Agent verifies manifest status = `APPROVED`.
2. **F-080** `copy_to_outbox` → `outbox/proposals/v85/<date>-<track>/` (proposal.md + manifest.yaml).
3. **F-081** `write_review_record` if formal review packet exists.
4. **F-014** `log_trace_entry` — publish event with path link.
5. Operator notified proposal ready for UC-22 / UC-23.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 1a | Status ≠ APPROVED | Block — AIRUP gate |
| 2a | Outbox path exists | Version with timestamp suffix |

## Functions invoked

F-080, F-081, F-014

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | APPROVED — AIRUP publish gate; exemplified by outbox proposals |