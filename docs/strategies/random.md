# Random strategy (Hari)

| Field | Value |
|-------|-------|
| **Mode** | `random` (UX label: **Hari**) |
| **Owner** | Povl |
| **Status** | APPROVED |
| **Version** | 0.3 |
| **Last updated** | 2026-07-07 |
| **Spec** | [random-v1.1.md](../../outbox/specs/random-v1.1.md) (v1: [random-v1.md](../../outbox/specs/random-v1.md)) |

---

## 1. Purpose

Generate betting systems by **random selection** of horses per leg. The operator may mark zero or more horses per leg as **locked** candidates; on generate, Hari fills each leg so total cost matches **SYSTEMKOSTNAD exactly** (V85: ∏(horses per leg) × 0.50 SEK).

## 2. Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Race card | Yes | 8 legs with eligible start numbers |
| Operator pools | Yes | Marked horses per leg (F-026); may be empty |
| `stake_budget_sek` | Yes | SYSTEMKOSTNAD; default **500 SEK**; must be multiple of 0.50 |
| `frozen_legs` | No | Legs where only marked horses are used (no random fill) |
| `seed` | No | RNG seed for reproducibility (F-032) |
| `max_horses_per_leg` | No | Default: eligible field size per leg |

## 3. Algorithm (v1.1)

1. Operator marks lock horses per leg (optional). Marked horses are always in the final slip.
2. Per leg: `min` = marked count (or 1 if unmarked and not frozen); `max` = eligible horses (or marked count if frozen).
3. Find leg horse-counts whose product equals `stake_budget_sek / 0.50`.
4. If impossible: return `BUDGET_NOT_MET` with **nearest achievable** `suggested_stake_sek`.
5. Choose a valid count vector at random (seeded); fill unmarked slots uniformly from eligible horses.
6. Optional **F-052 basic**: when ATG V85 bet % available, show P(8), P(≥7), P(≥6), P(≥5) (independent-leg proxy).

Full spec: [random-v1.1.md](../../outbox/specs/random-v1.1.md).

## 4. Outputs

Standard proposal format plus manifest (`mode`, `seed`, `constraints`, fill steps). Local UI may prompt operator to accept suggested stake on `BUDGET_NOT_MET`.

## 5. Resolved requirements

- [x] Exact SYSTEMKOSTNAD match when achievable
- [x] Empty operator marks allowed (random fills all legs)
- [x] Frozen legs and nearest-stake suggestion
- [x] No field-size weighting (SL-003)
- [x] F-052 basic when distributions present
- [ ] Reduced-stake variants (UC-14 — v1.2)

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.3 | 2026-07-07 | v1.1 — exact budget fill, Hari UX, nearest stake, F-052 basic |
| 0.2 | 2026-07-07 | APPROVED v1 — per [random-v1.md](../../outbox/specs/random-v1.md) |
| 0.1 | 2026-07-06 | Initial draft |