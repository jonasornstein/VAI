# UC-12 — Expert mode

| Field | Value |
|-------|-------|
| **ID** | UC-12 |
| **Status** | APPROVED |
| **Version** | 1.0 |
| **Reviewer** | Nisse (patterns), Jonte (operator) |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Primary actor** | Operator, Trotting expert |
| **Implements** | FR-030–032 |
| **Implementation** | Deferred — UX tab disabled (*Kommer senare*) |
| **Preconditions** | UC-10 in progress; operator horse pools set; SYSTEMKOSTNAD from F-025 |

## Brief description

Apply expert spik/gardering patterns within **operator pools** and **SYSTEMKOSTNAD**.

## Main success scenario

1. Actor selects optional `template_id` (e.g. `T-001`) or manual mode.
2. If template: **F-040** `load_expert_template` from catalog in [expert.md](../../strategies/expert.md).
3. **F-041** `classify_legs` — label each leg: `spik` (1 horse), `halvleg` (2–3), `öppen` (4+).
4. **F-042** `apply_expert_pattern` — picks only from **operator pool** per leg:
   - `spik`: 1 horse from pool
   - `halvleg`: 2–3 from pool
   - `öppen`: subset of pool until budget binds
5. Actor may **F-043** `apply_manual_override` on any leg before finalize.
6. Trim until **F-061** computed cost ≤ **SYSTEMKOSTNAD**.
7. Return selections with `leg_classification` and rationale to UC-10.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 2a | Unknown template_id | List templates; abort or manual |
| 4a | Pool smaller than pattern needs | Narrow pattern or warn operator |
| 5a | Override spik with 2+ horses | Reclassify as halvleg in manifest |

## Functions invoked

F-026, F-040, F-041, F-042, F-043, F-060, F-061

## Special requirements

- [expert.md](../../strategies/expert.md), [ux-workflow.md](../ux-workflow.md)

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | APPROVED — requirements spec; generator not yet implemented |