# Review — Expert STATS v1

| Field | Value |
|-------|-------|
| **Artifact** | [expert-stats-v1.md](../specs/expert-stats-v1.md) |
| **Reviewer** | ornstein (operator UX), Povl (count / percentage) |
| **Date** | 2026-09-11 |
| **Verdict** | **APPROVED** |
| **Version** | 0.1 |

---

## Findings

- [x] Expert-only **STATS** toggle (not a blocking modal); slip unchanged
- [x] Count `k/N` and percentage `100 × k / N` on horse buttons and consensus strip
- [x] Population = tips for date+track in the currently shown roster (visible; gratis filter; each tip one vote; fixture excluded)
- [x] `N = 0` → empty payload, no division (Povl)
- [x] Grid stays start-number order; heat by %; selected horses keep pool-selected fill
- [x] API `GET /api/v1/expert-stats`; CLI `python -m vai expert stats`
- [x] Implemented: `src/vai/expert_stats.py`, server, mockup, tests (Bollnäs 5-tip fixture)

## Notes

Canonical published path: `outbox/specs/expert-stats-v1.md`. Function **F-049** in [functions.md](../../docs/requirements/functions.md). UC-12 v1.6.
