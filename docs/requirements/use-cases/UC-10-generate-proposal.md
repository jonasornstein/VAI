# UC-10 — Generate proposal

| Field | Value |
|-------|-------|
| **ID** | UC-10 |
| **Status** | DRAFT |
| **Primary actor** | Operator |
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
7. **Mode branch** (each mode uses operator pools as candidate universe):
   - 7a. `random` → UC-11
   - 7b. `expert` → UC-12
   - 7c. `quantitative` → UC-13
8. Mode returns final `leg → horse[]` selections (betting slip).
9. UC-14: **F-060**–**F-062** — computed cost vs SYSTEMKOSTNAD displayed.
10. Model attaches hit probabilities (**F-052** for quant; summary for other modes where applicable).
11. **F-023** / **F-024** write draft; status `AWAITING_OPERATOR`.

## Proposal output format

Includes: mode, DATUM, BANA, SYSTEMKOSTNAD (budget), computed cost, combinations, leg table, probabilities, rationale.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 3a | SYSTEMKOSTNAD &lt; min possible cost | Warn; model may return single-row minimum |
| 6a | No horses marked in a leg | Require at least one per leg or abort |
| 9a | Computed cost &gt; SYSTEMKOSTNAD | Model narrows selections (UC-11 F-031, UC-13 F-053) or warn |
| 7c | Odds unavailable | Degrade to expert/random or abort |

## Functions invoked

F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-052, F-060, F-061, F-062 (+ mode functions)

## Special requirements

- [ux-workflow.md](../ux-workflow.md)
- [SUP-U-006](../supplementary-specification.md#2-usability), [SUP-U-007](../supplementary-specification.md#2-usability)
- UX mockup: `outbox/mockups/v85-proposal-ux-mockup-atg.html`