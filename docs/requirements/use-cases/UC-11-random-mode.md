# UC-11 — Random mode (Hari)

| Field | Value |
|-------|-------|
| **ID** | UC-11 |
| **Status** | DRAFT |
| **Primary actor** | Operator |
| **Preconditions** | UC-10 in progress; race card loaded; SYSTEMKOSTNAD from F-025 |

## Brief description

From **operator-marked horse pools** (optional per leg), randomly build a betting slip that matches **SYSTEMKOSTNAD exactly** when mathematically possible.

## Main success scenario

1. Candidate universe per leg = eligible race-card horses; operator marks are **locked** (F-026).
2. Optional: `seed` via **F-032**; optional `frozen_legs` (no random fill on those legs).
3. Engine finds per-leg horse counts whose product equals `SYSTEMKOSTNAD / 0.50`.
4. **F-030** — uniform fill of unmarked slots to reach each leg count.
5. **F-061** — computed cost equals SYSTEMKOSTNAD (ε = 0.001 SEK).
6. **F-052** basic hit summary when ATG leg distributions available (optional).
7. Return leg selections to UC-10; record `seed` in manifest.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 3a | No exact count vector exists | Abort `BUDGET_NOT_MET`; offer `suggested_stake_sek` (nearest valid) |
| 2a | Frozen leg with no marks | Abort `FROZEN_EMPTY_LEG` |
| 1a | Operator pool is single horse (frozen or all marked) | Leg count fixed to that set |

## Functions invoked

F-026, F-030, F-031 (exact-budget constraint), F-032, F-052 (basic), F-060, F-061

## Special requirements

- [random.md](../../strategies/random.md), [random-v1.1.md](../../../outbox/specs/random-v1.1.md)
- [ux-workflow.md](../ux-workflow.md)
- [SUP-R-002](../supplementary-specification.md#3-reliability)