# Review — V85 Proposal Halmstad 2026-07-05

| Field | Value |
|-------|-------|
| **Artifact** | `pending/proposals/v85/2026-07-05-halmstad/proposal.md` |
| **Race card** | `inbox/race-cards/2026-07-05-halmstad.yaml` |
| **Mode** | random (seed 42) |
| **Reviewer** | ornstein (operator) |
| **Review type** | UC-20 / F-071 operator checklist |
| **Date** | 2026-07-07 |
| **Verdict** | **APPROVED** |
| **Published** | `outbox/proposals/v85/2026-07-05-halmstad/proposal.md` |

---

## Automated verification (passed)

| Check | Result | Detail |
|-------|--------|--------|
| 8 avdelningar | ✓ | Legs 1–8 present |
| ATG cost formula | ✓ | `5×1×4×5×5×2×1×1` = **1 000** rader × 0,50 = **500,00 SEK** |
| Budget | ✓ | Computed cost = SYSTEMKOSTNAD (500 SEK) |
| Horse validity | ✓ | All selections ⊆ race card `horses` per leg |
| Scratches | ✓ | No strukna hästar selected (leg 1 scratch #5 not in slip) |
| System limit | ✓ | 1 000 rows &lt; 5 000 max ([v85.md](../../docs/betting/v85.md) §5) |

---

## Operator checklist (F-071)

- [x] 8 avdelningar ifyllda
- [x] Kostnad verifierad mot ATG-formel
- [x] Inga ogiltiga hästnummer
- [x] Strukna hästar kontrollerade mot race card
- [x] Reserver noterade där relevant (leg 1: 7, 12)
- [x] **ATG UI transcribability confirmed by ornstein**
- [ ] **Scratch/reserve status still current on race day**

---

## Transcription guide (atg.se)

| Leg | Race | Mark on coupon | Type |
|-----|------|----------------|------|
| 1 | V85-1 | 2, 3, 4, 8, 11 | Gardering (5) |
| 2 | V85-2 | 1 | Spik |
| 3 | V85-3 | 2, 6, 7, 10 | Gardering (4) |
| 4 | V85-4 | 1, 2, 4, 5, 9 | Gardering (5) |
| 5 | V85-5 | 3, 6, 8, 11, 12 | Gardering (5) |
| 6 | V85-6 | 2, 5 | Gardering (2) |
| 7 | V85-7 | 7 | Spik |
| 8 | V85-8 | 4 | Spik |

**Coupon summary:** 1 000 systemrader · 500,00 SEK · radpris 0,50 SEK

---

## Povl lens (math — agent)

- [x] Cost math matches F-060–F-061
- [x] Greedy shrink documented (8 steps used)
- [x] Seed recorded for reproducibility
- [x] Full race-card pools used (CLI default — no separate `pools.yaml`)

No quant review required (random mode).

---

## Nisse lens (rules — agent)

- [x] V85 ordinary stake 0,50 SEK
- [x] Selections are valid start numbers per manual race card
- [ ] **Race day:** re-verify scratches/reserves before play (manual card may be stale)

---

## Usability findings (addressed in revision)

| ID | Finding | Resolution |
|----|---------|------------|
| OR-001 | Leg table lacked race labels (V85-n) | Added `Race` column in proposal template |
| OR-002 | Spik/gardering not visible | Added to `Notes` column |
| OR-003 | Reserves only on leg 1 in card | Noted in leg 1 Notes |
| OR-004 | No embedded UC-20 checklist | Added auto-checked checklist in proposal |

---

## Required for APPROVE (operator)

1. ornstein or Kricke confirms slip is enterable on [atg.se/v85](https://www.atg.se/v85) without rework.
2. Reply **APPROVED** (or list revisions).

On **APPROVED**:

- Copy proposal → `outbox/proposals/v85/2026-07-05-halmstad/`
- Copy this review → `outbox/reviews/`
- Log in `docs/TRACE-LOG.md`

---

## Verdict summary

**APPROVED** by ornstein 2026-07-07 — published to `outbox/`.