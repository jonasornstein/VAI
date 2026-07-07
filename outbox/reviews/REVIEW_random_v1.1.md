# Review — Random v1.1 + ATG data source specs

| Field | Value |
|-------|-------|
| **Artifacts** | `outbox/specs/random-v1.1.md`, `outbox/specs/atg-data-source.md` |
| **Reviewer** | Povl (quant) |
| **Date** | 2026-07-07 |
| **Verdict** | **APPROVED** |

---

## Findings

- [x] Exact-budget fill algorithm matches shipped `generate_random_v1` behaviour
- [x] Nearest-stake suggestion on `BUDGET_NOT_MET` is mathematically sound
- [x] F-052 basic uses independent-leg assumption; limitations documented
- [x] ATG `betDistribution / 10000` mapping stated
- [x] Reduced-stake correctly deferred to v1.2

## Notes

Greedy-shrink v1 spec superseded for implementation; v1.1 is canonical for Hari mode.