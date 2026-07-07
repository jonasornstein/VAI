# UC-13 — Quantitative mode

| Field | Value |
|-------|-------|
| **ID** | UC-13 |
| **Status** | APPROVED |
| **Version** | 1.0 |
| **Reviewer** | Povl (math), Jonte (operator) |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Primary actor** | Operator, Quant analyst |
| **Implements** | FR-040–043 |
| **Implementation** | Deferred — UX tab disabled (*Kommer senare*) |
| **Preconditions** | UC-10 in progress; operator pools set; SYSTEMKOSTNAD from F-025; odds from ATG or inbox |

## Brief description

Optimize betting slip within **operator pools** and **SYSTEMKOSTNAD**; output hit probabilities.

## Main success scenario

1. **F-050** `load_odds_input` — prefer **F-009** ATG fetch; fallback `inbox/odds/`.
2. **F-051** `compute_leg_probabilities` on operator pool per leg.
3. Objective (v1 default): **maximize P(≥7 correct)** subject to **SYSTEMKOSTNAD** (default **500 SEK**).
4. **F-053** `optimize_under_budget` — search subsets of operator pools; **F-061** cost ≤ SYSTEMKOSTNAD.
5. **F-052** `compute_hit_probabilities` — display in UX (8 / ≥7 / ≥6 rätt bars).
6. Optional: **F-054** `run_monte_carlo` (Could v1.1).
7. Rationale per [quantitative.md](../../strategies/quantitative.md); odds source documented.
8. Return betting slip to UC-10.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 1a | Odds missing for horse in pool | Exclude horse or prompt operator |
| 4a | No feasible system under SYSTEMKOSTNAD | Best-effort + warn |
| 5a | Pre-2026-07-02 round | Historical pool split in manifest |

## Functions invoked

F-009, F-026, F-050, F-051, F-052, F-053, F-054 (optional), F-060, F-061

## Special requirements

- [quantitative.md](../../strategies/quantitative.md) v0.3, [ux-workflow.md](../ux-workflow.md)

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | APPROVED — requirements spec; generator not yet implemented |