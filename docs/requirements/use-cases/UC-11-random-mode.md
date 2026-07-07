# UC-11 — Random mode

| Field | Value |
|-------|-------|
| **ID** | UC-11 |
| **Status** | DRAFT |
| **Primary actor** | Operator |
| **Preconditions** | UC-10 in progress; operator horse pools per leg; SYSTEMKOSTNAD from F-025 |

## Brief description

From **operator-marked horse pools**, randomly build a betting slip within **SYSTEMKOSTNAD**.

## Main success scenario

1. Candidate universe per leg = operator pool (**F-026**), not full race card.
2. Optional: `seed` via **F-032** `set_rng_seed`.
3. For each leg 1..8:
   1. Draw `k` horses from operator pool (at least 1).
   2. **F-030** `random_select_horses` — uniform subset from pool.
4. **F-031** `apply_random_constraints` — if **F-061** cost > **SYSTEMKOSTNAD**, reduce gardering width (max 10 retries).
5. **F-052** basic hit summary when odds available (optional).
6. Return leg selections to UC-10; record `seed` in manifest.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 4a | Cannot meet SYSTEMKOSTNAD after retries | Abort; suggest higher budget or narrower pools |
| 3a | Operator pool is single horse | Leg is forced spik |

## Functions invoked

F-026, F-030, F-031, F-032, F-052, F-060, F-061

## Special requirements

- [random.md](../../strategies/random.md), [ux-workflow.md](../ux-workflow.md)
- [SUP-R-002](../supplementary-specification.md#3-reliability)