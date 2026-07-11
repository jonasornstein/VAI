# V85 Proposal — Årjäng — 2026-07-11

| Field | Value |
|-------|-------|
| Mode | random (Hari) |
| AIRUP status | APPROVED |
| Generated | 2026-07-07T10:37:58Z |
| Approved | 2026-07-07 · ornstein |
| SYSTEMKOSTNAD | 500.00 SEK |
| Total cost | 500.00 SEK |
| Combinations | 1000 |
| Cost breakdown | 1×2×10×1×10×1×1×5 |

## Legs

| Leg | Race | Horses | Notes |
|-----|------|--------|-------|
| 1 | V85-5 | 1 | Spik |
| 2 | V85-6 | 5, 12 | Gardering (2) |
| 3 | V85-7 | 1, 2, 3, 4, 5, 6, 7, 9, 11, 12 | Gardering (10) |
| 4 | V85-8 | 4 | Spik |
| 5 | V85-9 | 1, 4, 5, 6, 7, 8, 9, 10, 11, 12 | Gardering (10) |
| 6 | V85-10 | 8 | Spik |
| 7 | V85-11 | 10 | Spik |
| 8 | V85-12 | 1, 3, 5, 7, 13 | Gardering (5) |

## Operator checklist (UC-20)

- [x] 8 avdelningar ifyllda
- [x] Kostnad verifierad mot ATG-formel
- [x] Inga ogiltiga hästnummer
- [x] Inga strukna hästar valda
- [x] Operator godkänner för ATG-inmatning

## Rationale

Hari (random): operator marks locked; slumpen fyller på till exakt SYSTEMKOSTNAD (23 hästar tillagda av slumpen).

## Manifest

```yaml
mode: random
seed: 42
constraints:
  stake_budget_sek: 500.0
  min_horses_per_leg: 1
  max_horses_per_leg:
    1: 15
    2: 12
    3: 12
    4: 15
    5: 12
    6: 9
    7: 12
    8: 15
  max_shrink_steps: 10
  shrink_steps_used: 23
  weight_by_field_size: false
```
