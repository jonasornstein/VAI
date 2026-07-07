# Random strategy

| Field | Value |
|-------|-------|
| **Mode** | `random` |
| **Owner** | Povl |
| **Status** | APPROVED |
| **Version** | 0.2 |
| **Last updated** | 2026-07-07 |
| **Spec** | [outbox/specs/random-v1.md](../../outbox/specs/random-v1.md) |

---

## 1. Purpose

Generate betting systems by **random selection** of horses per leg from the **operator pool**, capped by **SYSTEMKOSTNAD**. Useful for baseline comparison, exploration, or low-bias coverage.

## 2. Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Race card | Yes | Per leg: eligible start numbers |
| Operator pools | Yes | Marked horses per leg (F-026); ⊆ race card |
| `stake_budget_sek` | Yes | SYSTEMKOSTNAD; default **500 SEK** |
| `max_horses_per_leg` | No | Default: **\|operator pool\|** per leg |
| `min_horses_per_leg` | No | Default **1** |
| `seed` | No | RNG seed for reproducibility (F-032) |

## 3. Algorithm (v1)

1. For each leg 1..8: draw `k` uniformly from `[1, |pool|]`; select `k` horses uniformly from operator pool.
2. Compute cost: ∏(horses per leg) × 0.50 SEK.
3. If cost > SYSTEMKOSTNAD: **greedy shrink** — remove one random horse from widest leg (tie → lowest leg #); max **10** steps.
4. No weighting by field size.

Full pseudocode: [random-v1.md](../../outbox/specs/random-v1.md) §5–6.

## 4. Outputs

Standard proposal format plus manifest (`mode`, `seed`, `constraints`, `shrink_steps_used`).

## 5. Resolved requirements (v1)

- [x] Default `max_horses_per_leg` = pool size per leg
- [x] Budget policy: greedy shrink, max 10 steps
- [x] No field-size weighting

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.2 | 2026-07-07 | APPROVED v1 — per [random-v1.md](../../outbox/specs/random-v1.md) |
| 0.1 | 2026-07-06 | Initial draft |