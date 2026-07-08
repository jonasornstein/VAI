# UC-15 — Display race info

| Field | Value |
|-------|-------|
| **ID** | UC-15 |
| **Status** | APPROVED |
| **Version** | 1.0 |
| **Reviewer** | Nisse (terminology), Jonte (operator) |
| **Approved** | 2026-07-08 |
| **Last updated** | 2026-07-08 |
| **Primary actor** | Operator |
| **Preconditions** | UC-09 complete; race card loaded (ATG `game_id` or YAML) |
| **Spec** | [race-info-v1.md](../../../outbox/specs/race-info-v1.md) |

## Brief description

Extract and display race-level metadata (name, distance, start method, class) beside start time in each avdelning leg header.

## Main success scenario

1. UC-09 loads race card via **F-007** `fetch_race_card_from_atg` (or YAML fallback).
2. **F-029** `extract_race_info` parses per-leg metadata from ATG `races[]` (or YAML `race_info`).
3. `GET /api/v1/race-cards/{id}` returns `legs[].race_info` when available.
4. Local UI **renderLegs** shows multi-line `.race-info` header per avdelning.
5. Operator uses race context when marking horses; generation (UC-10/11) unchanged.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 2a | Manual YAML without `race_info` | Header shows `race_label · start_time` only |
| 2b | ATG field missing | Omit that sub-field; render remaining |

## Functions invoked

F-007, F-029

## Special requirements

- [race-info-v1.md](../../../outbox/specs/race-info-v1.md)
- [ux-workflow.md](../ux-workflow.md) Step 2
- [SUP-F-008](../supplementary-specification.md#1-functionality-cross-cutting) — read-only ATG

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-08 | APPROVED — race-level leg headers from ATG; YAML optional |