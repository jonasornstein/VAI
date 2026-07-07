# UC-14 — Compute system cost

| Field | Value |
|-------|-------|
| **ID** | UC-14 |
| **Status** | APPROVED |
| **Version** | 1.0 |
| **Reviewer** | Povl (math) |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Primary actor** | Agent (included by UC-10) |
| **Implements** | FR-013–014 |
| **Preconditions** | Leg selections defined (horse count per leg) |

## Brief description

Calculate combination count and total SEK cost; produce operator-visible breakdown.

## Main success scenario

1. System reads horse count \(n_i\) for each leg \(i = 1..8\).
2. **F-060** `count_combinations` — \(N = \prod_{i=1}^{8} n_i\).
3. **F-061** `compute_cost_sek` — \(C = N \times 0.50\) SEK (V85 ordinary stake).
4. **F-062** `format_cost_breakdown` — e.g. `1×3×1×2×1×4×1×2`.
5. System presents: **N** rader, **C** SEK, breakdown string.
6. Values written to proposal header and manifest.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 1a | Any \(n_i = 0\) | Error — invalid system; UC-10 abort |
| 3a | Reduced stake requested | \(C_\alpha = N \times 0.50 \times \alpha\) — deferred v1.2 (UC-14 §3a) |
| 3b | N > 5000 systems limit | Warn per [quantitative.md](../../strategies/quantitative.md) §2.3 |

## Functions invoked

F-060, F-061, F-062

## Special requirements

- [v85.md](../../betting/v85.md) §2.1
- [SUP-R-003](../supplementary-specification.md#3-reliability)

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | APPROVED — V85 cost formula shipped; reduced-stake deferred v1.2 |