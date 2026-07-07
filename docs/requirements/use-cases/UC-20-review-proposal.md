# UC-20 — Review proposal

| Field | Value |
|-------|-------|
| **ID** | UC-20 |
| **Status** | APPROVED |
| **Version** | 1.0 |
| **Reviewer** | Jonte (operator) |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Primary actor** | Operator, Trotting expert, Quant analyst |
| **Preconditions** | Draft in `pending/proposals/` with `AWAITING_OPERATOR` or expert review |

## Brief description

AIRUP review of a proposal until `APPROVED` or returned for revision.

## Main success scenario

1. **F-070** `display_proposal` — show 8 legs, horses, cost, rationale, hit probs (if quant).
2. Reviewer runs **F-071** `run_operator_checklist`:
   - [ ] 8 avdelningar ifyllda
   - [ ] Kostnad verifierad mot ATG-formel
   - [ ] Inga ogiltiga hästnummer
   - [ ] Strukna hästar kontrollerade mot race card
   - [ ] Reserver noterade där relevant
3. **Quant mode:** Povl verifies model assumptions in rationale.
4. **Expert mode:** Nisse may spot-check template application (optional).
5. If OK: **F-072** `approve_proposal` → status `APPROVED`.
6. If not OK: **F-073** `request_proposal_revision` with notes → **U** Update loop.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 2a | Scratch after ingest | Operator updates race card (UC-01) and regenerates (UC-10) |
| 5a | Cost mismatch | Reject; file bug against F-061 |
| 3a | Povl flags bad odds source | Reject; re-ingest odds (UC-01) |

## Functions invoked

F-070, F-071, F-072, F-073

## Special requirements

- [SUP-U-001](../supplementary-specification.md#2-usability) through [SUP-U-005](../supplementary-specification.md#2-usability)
- Operator gate: Kricke or Jonte for race-day **P**
- v1.1: **Innan spel** checklist wired in local UI (F-071 auto-updates from slip + race card)

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | APPROVED — operator checklist shipped in mockup and local UI |