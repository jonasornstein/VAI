# V85 Proposal — Halmstad — 2026-07-05

| Field | Value |
|-------|-------|
| Mode | random |
| AIRUP status | APPROVED |
| Approved | 2026-07-07 · ornstein |
| Generated | 2026-07-07T07:17:11Z |
| SYSTEMKOSTNAD | 500.00 SEK |
| Total cost | 500.00 SEK |
| Combinations | 1000 |
| Cost breakdown | 5×1×4×5×5×2×1×1 |

## Legs

| Leg | Race | Horses | Notes |
|-----|------|--------|-------|
| 1 | V85-1 | 2, 3, 4, 8, 11 | Gardering (5); Reserver: 7, 12; Strukna: 5 |
| 2 | V85-2 | 1 | Spik |
| 3 | V85-3 | 2, 6, 7, 10 | Gardering (4) |
| 4 | V85-4 | 1, 2, 4, 5, 9 | Gardering (5) |
| 5 | V85-5 | 3, 6, 8, 11, 12 | Gardering (5) |
| 6 | V85-6 | 2, 5 | Gardering (2) |
| 7 | V85-7 | 7 | Spik |
| 8 | V85-8 | 4 | Spik |

## Operator checklist (UC-20)

- [x] 8 avdelningar ifyllda
- [x] Kostnad verifierad mot ATG-formel
- [x] Inga ogiltiga hästnummer
- [x] Inga strukna hästar valda
- [x] Operator godkänner för ATG-inmatning

## Rationale

Random draw from operator pools; greedy shrink if over SYSTEMKOSTNAD (8 shrink step(s) used).

## Manifest

```yaml
mode: random
seed: 42
constraints:
  stake_budget_sek: 500.0
  min_horses_per_leg: 1
  max_horses_per_leg:
    1: 11
    2: 7
    3: 8
    4: 5
    5: 7
    6: 6
    7: 7
    8: 7
  max_shrink_steps: 10
  shrink_steps_used: 8
  weight_by_field_size: false
```
