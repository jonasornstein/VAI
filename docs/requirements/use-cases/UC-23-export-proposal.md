# UC-23 — Export proposal

| Field | Value |
|-------|-------|
| **ID** | UC-23 |
| **Status** | APPROVED |
| **Version** | 1.0 |
| **Reviewer** | ornstein (operator) |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Primary actor** | Operator |
| **Preconditions** | Proposal in `pending/` or `outbox/` |

## Brief description

Export printable PDF or open web view for race-day reference alongside ATG entry.

## Main success scenario

1. Operator generates system in local UI (or opens published proposal).
2. Operator triggers **print slip** — browser print of betting slip panel only (`print-slip-only` CSS).
3. Printed layout matches `outbox/mockups/v85-proposal-ux-mockup-atg.html` slip section.
4. Operator optionally **F-092** `toggle_display_theme` (light / mörk) before print.
5. Operator uses printout alongside UC-22 manual ATG entry.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 2a | PDF export requested | **F-090** deferred v1.2; use browser print in v1.1 |
| 3a | Unapproved pending proposal | Operator discretion — prefer approved `outbox/` copy |

## Functions invoked

F-090, F-091, F-092

## Special requirements

- [SUP-U-004](../supplementary-specification.md#2-usability)
- Reference: `outbox/mockups/`

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | APPROVED — v1.1 print-slip export; PDF (F-090) deferred v1.2 |