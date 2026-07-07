# UC-10 — Generate proposal

| Field | Value |
|-------|-------|
| **ID** | UC-10 |
| **Status** | APPROVED |
| **Version** | 1.0 |
| **Reviewer** | Jonte (operator) |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Primary actor** | Operator |
| **Implements** | FR-010–016 |
| **Preconditions** | UC-09 complete; race card loaded; operator horse pools selected; SYSTEMKOSTNAD entered |

## Brief description

Run selected mode on operator-marked horses within budget; produce betting slip, cost, and model probabilities.

## Main success scenario

1. Operator confirms **DATUM**, **BANA**, **SPELFORM** (UC-09).
2. Operator marks horses to include per leg in UX (**F-026** `set_operator_horse_pool`).
3. Operator enters **SYSTEMKOSTNAD** — **F-025** `set_stake_budget`; default **500 SEK**.
4. Operator selects mode tab: **F-022** `select_game_and_mode`.
5. **F-020** `load_race_card` for session context.
6. **F-021** `validate_horse_selection` — pools ⊆ race card horses.
7. **Mode branch** (v1.1: Hari only active; Expert/Kvant tabs disabled):
   - 7a. `random` (Hari) → UC-11
   - 7b. `expert` → UC-12 *(deferred — tab disabled)*
   - 7c. `quantitative` → UC-13 *(deferred — tab disabled)*
8. Mode returns final `leg → horse[]` selections (betting slip).
9. UC-14: **F-060**–**F-062** — computed cost; Hari targets exact SYSTEMKOSTNAD match.
10. **F-052** basic hit summary when ATG leg distributions available (Hari); full F-052 with UC-13 when quant ships.
11. **F-023** / **F-024** write draft; status `AWAITING_OPERATOR`.

## Proposal output format

Includes: mode, DATUM, BANA, SYSTEMKOSTNAD (budget), computed cost, combinations, leg table, probabilities, rationale.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 3a | No exact budget achievable | UC-11 `BUDGET_NOT_MET`; offer nearest `suggested_stake_sek` |
| 6a | No horses marked in a leg | Allowed — Hari fills leg randomly (v1.1) |
| 9a | Frozen leg with no marks | Abort `FROZEN_EMPTY_LEG` (UC-11) |
| 7b–7c | Expert or quant selected | Tab disabled in v1.1 UX; UC-12/13 not invoked |

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
| 1.0 | 2026-07-07 | APPROVED — v1.1 Hari flow; exact budget; empty-leg fill; deferred modes noted |