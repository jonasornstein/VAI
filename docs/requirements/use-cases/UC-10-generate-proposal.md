# UC-10 — Generate proposal

| Field | Value |
|-------|-------|
| **ID** | UC-10 |
| **Status** | APPROVED |
| **Version** | 1.0 |
| **Reviewer** | ornstein (operator) |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-15 |
| **Primary actor** | Operator |
| **Implements** | FR-010–016 |
| **Preconditions** | UC-09 complete; race card loaded; mode-specific inputs ready |

## Brief description

Run selected mode; produce betting slip, cost, and model probabilities.

## Main success scenario

1. Operator confirms **DATUM**, **BANA**, **SPELFORM** (UC-09).
2. Operator selects mode tab: **F-022** `select_game_and_mode` (**Hari** or **Expert**; Kvant disabled).
3. **F-020** `load_race_card` for session context.
4. **Mode branch** (v1.3):
   - 4a. `random` (Hari) → marks (F-026) + SYSTEMKOSTNAD (F-025) → UC-11
   - 4b. `expert` → list/select tip (UC-12); no pool required
   - 4c. `quantitative` → UC-13 *(deferred — tab disabled)*
5. Mode returns final `leg → horse[]` selections (betting slip).
6. UC-14: **F-060**–**F-062** — computed cost; Hari targets exact SYSTEMKOSTNAD match; Expert uses tip cost.
7. **F-052** basic hit summary when ATG leg distributions available.
8. **F-023** / **F-024** write draft; status `AWAITING_OPERATOR`.

## Proposal output format

Includes: mode, DATUM, BANA, SYSTEMKOSTNAD (budget), computed cost, combinations, leg table, probabilities, rationale.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 4a | No exact budget achievable (Hari) | UC-11 `BUDGET_NOT_MET`; offer nearest `suggested_stake_sek` |
| 4a | No horses marked in a leg (Hari) | Allowed — Hari fills leg randomly |
| 4a | Frozen leg with no marks (Hari) | Abort `FROZEN_EMPTY_LEG` |
| 4b | No tips for day (Expert) | Empty state; operator adds YAML to inbox |
| 4c | Quant selected | Tab disabled; UC-13 not invoked |

## Functions invoked

F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-052, F-060, F-061, F-062 (+ mode functions)

## Special requirements

- [ux-workflow.md](../ux-workflow.md)
- [SUP-U-006](../supplementary-specification.md#2-usability), [SUP-U-007](../supplementary-specification.md#2-usability)
- UX mockup: `outbox/mockups/v85-proposal-ux-mockup-atg.html`

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.1 | 2026-07-15 | Expert mode active (UC-12 betslips); quant still deferred |
| 1.0 | 2026-07-07 | APPROVED — v1.1 Hari flow; exact budget; empty-leg fill; deferred modes noted |