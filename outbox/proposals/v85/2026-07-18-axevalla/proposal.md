# V85 Proposal — Axevalla — 2026-07-18

| Field | Value |
|-------|-------|
| Mode | random (Hari) |
| AIRUP status | APPROVED |
| Generated | 2026-07-15T19:57:15Z |
| Approved | 2026-07-15 · ornstein |
| SYSTEMKOSTNAD | 500.00 SEK |
| Total cost | 500.00 SEK |
| Combinations | 1000 |
| Cost breakdown | 1×2×5×5×10×1×2×1 |

## Legs

| Leg | Race | Horses | Notes |
|-----|------|--------|-------|
| 1 | V85-5 | 1 | Spik |
| 2 | V85-6 | 5, 12 | Gardering (2) |
| 3 | V85-7 | 1, 2, 3, 5, 6 | Gardering (5) |
| 4 | V85-8 | 2, 9, 10, 11, 12 | Gardering (5) |
| 5 | V85-9 | 1, 2, 4, 5, 7, 9, 11, 12, 13, 14 | Gardering (10) |
| 6 | V85-10 | 12 | Spik |
| 7 | V85-11 | 9, 11 | Gardering (2) |
| 8 | V85-12 | 7 | Spik |

## Operator checklist (UC-20)

- [x] 8 avdelningar ifyllda
- [x] Kostnad verifierad mot ATG-formel
- [x] Inga ogiltiga hästnummer
- [x] Inga strukna hästar valda
- [x] Operator godkänner för ATG-inmatning

## Race-day (Saturday — UC-22)

- [ ] Re-check scratches / reserves before entry
- [ ] Enter system at atg.se
- [ ] Confirm ATG cost matches 500,00 SEK

## Rationale

Hari (random): operator marks locked; slumpen fyller på till exakt SYSTEMKOSTNAD (19 hästar tillagda av slumpen). Seed 42.

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
    3: 6
    4: 15
    5: 15
    6: 12
    7: 12
    8: 12
  max_shrink_steps: 10
  shrink_steps_used: 19
  weight_by_field_size: false
```
