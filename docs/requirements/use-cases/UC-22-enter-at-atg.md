# UC-22 — Enter at ATG

| Field | Value |
|-------|-------|
| **ID** | UC-22 |
| **Status** | APPROVED |
| **Version** | 1.0 |
| **Reviewer** | ornstein (operator) |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Primary actor** | Operator |
| **Preconditions** | Published proposal in `outbox/proposals/` |

## Brief description

Operator manually enters the approved system on atg.se. **No software automation.**

## Main success scenario

1. Operator opens published proposal (or UC-23 export).
2. **F-071** `run_operator_checklist` — final pre-spel check.
3. Operator opens [atg.se/v85](https://www.atg.se/v85) (**F-091** `open_atg_link` — browser only).
4. For each leg 1..8: operator marks same horse numbers as proposal.
5. Operator verifies ATG system cost matches proposal **F-061** total.
6. Operator places bet under own ATG account and T&C.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 4a | Late scratch | Apply reserves per [v85.md](../../betting/v85.md); may deviate from proposal — operator judgment |
| 5a | Cost mismatch | Stop; reconcile race card vs proposal before betting |
| 6a | Spelstopp passed | No bet; note in TRACE-LOG if system unused |

## Functions invoked

F-071, F-091 (human browser action only)

## Special requirements

- [SUP-I-001](../supplementary-specification.md#7-implementation-constraints)
- Acceptance criterion SRS §4 item 4
- v1.1: **ÖPPNA ATG/V85** button in UI opens atg.se; entry remains manual

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | APPROVED — manual ATG entry; no automation (NG-004) |