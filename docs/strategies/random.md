# Random strategy

| Field | Value |
|-------|-------|
| **Mode** | `random` |
| **Owner** | Povl |
| **Status** | DRAFT |
| **Last updated** | 2026-07-06 |

---

## 1. Purpose

Generate betting systems by **random selection** of horses per leg, optionally within constraints. Useful for baseline comparison, exploration, or low-bias coverage.

## 2. Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Race card | Yes | Per leg: eligible start numbers |
| `max_cost_sek` | No | Cap total system cost |
| `max_horses_per_leg` | No | Upper bound on gardering width |
| `min_horses_per_leg` | No | Default 1 |
| `seed` | No | RNG seed for reproducibility |

## 3. Algorithm (draft)

```
for each leg in 1..8:
    k = random integer in [min_horses_per_leg, max_horses_per_leg]
        capped by |race_card[leg]| and budget feasibility
    select k distinct horses uniformly from race_card[leg]
compute combinations and cost
if cost > max_cost_sek: retry or reduce (TBD — Povl)
```

## 4. Outputs

Standard proposal format plus:

```yaml
mode: random
seed: <int or null>
constraints:
  max_cost_sek: <float>
  max_horses_per_leg: <int>
```

## 5. Open requirements (Povl)

- [ ] Default `max_horses_per_leg` for V85
- [ ] Budget retry policy when over cap
- [ ] Whether to weight by field size

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-07-06 | Initial draft |