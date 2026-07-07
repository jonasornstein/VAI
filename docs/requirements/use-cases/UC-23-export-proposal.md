# UC-23 — Export proposal

| Field | Value |
|-------|-------|
| **ID** | UC-23 |
| **Status** | DRAFT |
| **Primary actor** | Operator |
| **Preconditions** | Proposal in `pending/` or `outbox/` |

## Brief description

Export printable PDF or open web view for race-day reference alongside ATG entry.

## Main success scenario

1. Operator selects proposal (date, track).
2. Operator chooses export: **PDF** or **open HTML view**.
3. **PDF:** **F-090** `export_pdf` — layout per `outbox/mockups/v85-proposal-ux-mockup-atg.html`.
4. **HTML:** Open mockup-style page populated from proposal data (offline-capable static render).
5. Operator optionally **F-092** `toggle_display_theme` (light / mörk).
6. Operator uses export during UC-22 entry.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 3a | Export from pending (unapproved) | Watermark `DRAFT — ej godkänd` |
| 4a | Quant mode | Include hit-probability bars in export |

## Functions invoked

F-090, F-091, F-092

## Special requirements

- [SUP-U-004](../supplementary-specification.md#2-usability)
- Reference: `outbox/mockups/`