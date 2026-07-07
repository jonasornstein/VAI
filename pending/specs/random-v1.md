# Random mode — v1 implementation spec

| Field | Value |
|-------|-------|
| **Version** | 0.1 |
| **Status** | AWAITING_POVL |
| **AIRUP phase** | R |
| **Reviewer** | Povl |
| **Author** | Assistant (Jonte decisions 2026-07-07) |
| **Last updated** | 2026-07-07 |
| **Parent scope** | [scope-lock-v1-random.md](./scope-lock-v1-random.md) |
| **Implements** | UC-11, F-030, F-031, F-032, F-060, F-061, F-062 |
| **Strategy doc** | [random.md](../../docs/strategies/random.md) |

---

## 1. Purpose

Define the **code-ready** algorithm for V85 **random-mode** generation in v1: uniform random subsets from operator horse pools, capped by **SYSTEMKOSTNAD**, with reproducible RNG when seeded.

This spec **resolves** Povl open items SL-001–SL-003 from the scope lock.

---

## 2. Resolved decisions (Povl)

| ID | Question | **v1 decision** |
|----|----------|-----------------|
| SL-001 | Default `max_horses_per_leg` | **Dynamic per leg:** `max_horses_per_leg(i) = \|operator_pool[i]\|` — draw `k` uniformly from `[1, \|pool\|]`. No global cap below pool size. |
| SL-002 | Budget retry policy | **Greedy shrink** — remove one horse from the widest multi-horse leg; repeat until cost ≤ budget or **10 shrink steps** exhausted. |
| SL-003 | Weight by field size? | **No.** Uniform choice of `k` and uniform choice of horses within the operator pool (F-030). |

| Parameter | Default | Notes |
|-----------|---------|-------|
| `min_horses_per_leg` | `1` | Single-horse pool ⇒ forced spik (UC-11 §3a) |
| `row_price_sek` | `0.50` | V85 ordinary stake ([v85.md](../../docs/betting/v85.md) §2.1) |
| `max_shrink_steps` | `10` | Matches UC-11 / F-031 retry ceiling |
| `stake_budget_sek` | `500` | SYSTEMKOSTNAD default (F-025) |

---

## 3. Inputs and outputs

### 3.1 Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `race_card` | `RaceCard` | Yes | Loaded YAML; 8 legs with eligible horses |
| `operator_pools` | `dict[int, list[int]]` | Yes | Leg → marked start numbers; ⊆ `race_card` horses |
| `stake_budget_sek` | `float` | Yes | SYSTEMKOSTNAD; target max cost |
| `seed` | `int \| None` | No | F-032; `None` = non-reproducible run |
| `max_horses_per_leg` | `dict[int, int] \| None` | No | Optional override per leg; v1 default derived from pool size |

### 3.2 Outputs

| Name | Type | Description |
|------|------|-------------|
| `selections` | `dict[int, list[int]]` | Leg → sorted start numbers (ascending) |
| `combinations` | `int` | F-060: \(N = \prod n_i\) |
| `cost_sek` | `float` | F-061: \(N \times 0.50\) |
| `cost_breakdown` | `str` | F-062: e.g. `1×3×1×2×1×4×1×2` |
| `manifest` | `RandomManifest` | Mode metadata for proposal footer |

```yaml
# RandomManifest (embedded in proposal)
mode: random
seed: <int or null>
constraints:
  stake_budget_sek: <float>
  min_horses_per_leg: 1
  max_horses_per_leg: per-leg |pool|   # computed at run time
  max_shrink_steps: 10
  shrink_steps_used: <int>
  weight_by_field_size: false
```

### 3.3 Result type

```python
@dataclass
class RandomResult:
    selections: dict[int, list[int]]
    combinations: int
    cost_sek: float
    cost_breakdown: str
    manifest: RandomManifest
    shrink_steps_used: int

@dataclass
class RandomError:
    code: str
    message: str
    hint: str | None = None
```

**Success:** `cost_sek <= stake_budget_sek` (within float tolerance ε = 0.001 SEK).

---

## 4. Preconditions and validation

Run **before** RNG (F-021):

| Rule | Error code | Action |
|------|------------|--------|
| Exactly 8 legs in `race_card` | `INVALID_RACE_CARD` | Abort |
| `operator_pools` has keys 1..8 | `INCOMPLETE_POOLS` | Abort |
| Each pool non-empty | `EMPTY_POOL` | Abort; leg number in message |
| Each pool ⊆ race card horses for that leg | `POOL_NOT_SUBSET` | Abort |
| `stake_budget_sek` > 0 | `INVALID_BUDGET` | Abort |
| `stake_budget_sek` ≥ 0.50 | `BUDGET_BELOW_MINIMUM` | Abort; min cost is one spik per leg |
| `stake_budget_sek` ≥ min_possible_cost under **all spiks** | — | Always 0.50 SEK for V85; satisfied if budget ≥ 0.50 |

**Minimum cost** for any valid system: **0.50 SEK** (8 spiks).

**Maximum cost** without budget (full pools selected): \(\prod_i \|pool_i\|\) — may exceed budget; greedy shrink handles post-draw.

---

## 5. Algorithm

### 5.1 RNG (F-032)

```python
rng = random.Random(seed)  # seed=None → system entropy
```

All random choices in §5.2–5.3 use this single `rng` instance so a fixed `seed` reproduces the full run including shrink removals.

### 5.2 Initial draw (F-030)

For each leg `i` in `1..8`:

1. `pool = operator_pools[i]` (already validated non-empty).
2. `cap = len(pool)` — this is `max_horses_per_leg(i)` for v1.
3. If optional override `max_horses_per_leg` is provided: `cap = min(cap, override[i])`.
4. Draw `k = rng.randint(1, cap)` — uniform inclusive.
5. `selections[i] = sorted(rng.sample(pool, k))` — distinct horses, ascending display order.

### 5.3 Cost (F-060, F-061, F-062)

```
counts[i] = len(selections[i])
N = product(counts[i] for i in 1..8)
cost_sek = N * 0.50
breakdown = "×".join(str(counts[i]) for i in 1..8)
```

### 5.4 Greedy shrink (F-031)

While `cost_sek > stake_budget_sek` **and** `shrink_steps < max_shrink_steps` (10):

1. **Eligible legs:** those with `len(selections[i]) > 1`.
2. If none eligible → **break** (cannot shrink further; go to §5.5 failure).
3. **Pick leg:** maximum `len(selections[i])`; tie-break → **lowest leg number**.
4. **Remove horse:** `rng.choice(selections[i])` — uniform among currently selected horses.
5. Re-sort `selections[i]` ascending.
6. Recompute cost (§5.3).
7. `shrink_steps += 1`.

After loop:

- If `cost_sek <= stake_budget_sek` → **success** (§6).
- Else → **failure** `BUDGET_NOT_MET` (§5.5).

### 5.5 Failure — budget not met (UC-11 §4a)

| Field | Value |
|-------|-------|
| Code | `BUDGET_NOT_MET` |
| Message | `Cannot meet SYSTEMKOSTNAD after {shrink_steps} shrink steps` |
| Hint | `Raise stake budget, narrow horse pools, or run again with a different seed` |

Include in error payload: `cost_sek`, `stake_budget_sek`, `combinations`, `selections` (last state), `shrink_steps_used`.

---

## 6. Pseudocode (full)

```
function generate_random_v1(race_card, operator_pools, stake_budget_sek, seed=None):
    validate(§4)
    rng = Random(seed)
    selections = {}
    for i in 1..8:
        pool = operator_pools[i]
        cap = len(pool)
        k = rng.randint(1, cap)
        selections[i] = sorted(rng.sample(pool, k))

    shrink_steps = 0
    (N, cost, breakdown) = compute_cost(selections)

    while cost > stake_budget_sek and shrink_steps < 10:
        eligible = [i for i in 1..8 if len(selections[i]) > 1]
        if eligible is empty:
            break
        leg = min(i for i in eligible if len(selections[i]) == max(len(selections[j]) for j in eligible))
        horse = rng.choice(selections[leg])
        selections[leg].remove(horse)
        shrink_steps += 1
        (N, cost, breakdown) = compute_cost(selections)

    if cost > stake_budget_sek:
        return Error(BUDGET_NOT_MET, ...)

    return RandomResult(selections, N, cost, breakdown, manifest, shrink_steps)
```

---

## 7. Worked examples

### 7.1 All spiks — minimum cost

| Leg | Pool | Draw k | Selected |
|-----|------|--------|----------|
| 1–8 | any non-empty | 1 each | one horse each |

`N = 1`, `cost = 0.50 SEK`. Greedy shrink never runs.

### 7.2 Greedy shrink

Pools and draw (before shrink):

| Leg | Pool size | k drawn |
|-----|-----------|---------|
| 1 | 5 | 3 |
| 2 | 4 | 4 |
| 3 | 6 | 2 |
| 4–8 | ≥1 | 1 each |

`N = 3×4×2×1×1×1×1×1 = 24` → `cost = 12.00 SEK`. Budget = `10.00 SEK`.

| Step | Widest leg | Action | New counts | N | Cost |
|------|------------|--------|------------|---|------|
| — | — | initial | 3×4×2×1×1×1×1×1 | 24 | 12.00 |
| 1 | 2 (k=4) | remove 1 horse | 3×3×2×1×1×1×1×1 | 18 | 9.00 ✓ |

Success; `shrink_steps_used = 1`.

### 7.3 Tie-break on widest leg

Legs 3 and 5 both have `k = 4`; leg 6 has `k = 3`. Shrink **leg 3** first (lowest leg number among max width).

### 7.4 Golden test (implementation)

Provide fixed `seed`, pools, and budget in `src/tests/test_random_v1.py`; assert exact `selections`, `N`, `cost`, `shrink_steps_used`. See §9.

---

## 8. Module mapping (`src/`)

| Path | Responsibility |
|------|----------------|
| `atg/models/race_card.py` | `RaceCard`, leg types |
| `atg/models/proposal.py` | `RandomResult`, `RandomManifest`, proposal envelope |
| `atg/cost.py` | F-060, F-061, F-062 |
| `atg/strategies/random.py` | `generate_random_v1(...)` — this spec |
| `atg/io/race_card.py` | YAML load + validate |
| `atg/cli.py` | CLI wrapper for manual YAML path |

### 8.1 Public API

```python
def generate_random_v1(
    race_card: RaceCard,
    operator_pools: Mapping[int, Sequence[int]],
    stake_budget_sek: float,
    *,
    seed: int | None = None,
    max_horses_per_leg: Mapping[int, int] | None = None,
) -> RandomResult | RandomError:
    ...
```

### 8.2 CLI sketch (v1)

```
python -m atg.cli random \
  --race-card inbox/race-cards/2026-07-05-halmstad.yaml \
  --pools pools.yaml \
  --budget 500 \
  --seed 42 \
  --out pending/proposals/v85/2026-07-05-halmstad/proposal.md
```

`pools.yaml` optional when CLI marks all race-card horses (full-pool default for testing).

---

## 9. Test requirements

| Test | Assert |
|------|--------|
| `test_minimum_cost_all_spiks` | Budget 500; pools size 1 each → cost 0.50 |
| `test_reproducible_seed` | Same seed + inputs → identical selections and manifest |
| `test_greedy_shrink_reduces_cost` | §7.2 numeric example |
| `test_budget_not_met_abort` | Tiny budget + wide draw → `BUDGET_NOT_MET` after ≤10 steps |
| `test_empty_pool_rejected` | `EMPTY_POOL` before RNG |
| `test_forced_spik` | Pool size 1 → always that horse |
| `test_cost_formula` | Matches [v85.md](../../docs/betting/v85.md) §2.1 for 3+ fixtures |

---

## 10. Proposal artifact binding

On success, UC-14 + UC-10 write proposal header:

| Field | Source |
|-------|--------|
| Mode | `random` |
| Total cost | `cost_sek` |
| Combinations | `N` |
| SYSTEMKOSTNAD | `stake_budget_sek` |
| Legs table | `selections` per leg |
| Rationale | `Random draw from operator pools; greedy shrink if over budget` |
| Manifest | §3.2 YAML block |

Format: [AGENTS.md](../../AGENTS.md) proposal template → `pending/proposals/v85/<date>-<track>/`.

---

## 11. Out of scope (v1)

- F-052 hit probabilities (optional stub returning `null`)
- Expert / quantitative modes
- ATG fetch
- Reduced-stake cost variants (UC-14 §3a — v1.1)
- Weighting by field size or odds

---

## 12. Promotion checklist (on APPROVED)

| Artifact | Action |
|----------|--------|
| [random.md](../../docs/strategies/random.md) | Close §5 open items; bump to v0.2 APPROVED |
| [scope-lock-v1-random.md](./scope-lock-v1-random.md) | Mark SL-001–SL-003 resolved |
| [TRACE-LOG.md](../../docs/TRACE-LOG.md) | Log Povl approval |
| `outbox/specs/random-v1.md` | Copy on publish |

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-07-07 | Initial spec — dynamic max per pool, greedy shrink, uniform draw (Jonte + Povl defaults) |