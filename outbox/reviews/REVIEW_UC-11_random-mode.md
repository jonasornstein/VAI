# Review — UC-11 Random mode (Hari)

| Field | Value |
|-------|-------|
| **Artifact** | `docs/requirements/use-cases/UC-11-random-mode.md` |
| **Reviewer** | Povl (algorithm), Jonte (operator) |
| **Date** | 2026-07-07 |
| **Verdict** | **APPROVED** |

---

## Findings

- [x] Main scenario matches [random-v1.1.md](../specs/random-v1.1.md) exact-budget fill algorithm
- [x] Extensions cover `BUDGET_NOT_MET`, frozen legs, and locked picks
- [x] Function trace (F-026, F-030–F-032, F-052 basic, F-060–F-061) matches implementation
- [x] Reduced-stake deferred to v1.2 (extension 3b)
- [x] Operator acceptance: Årjäng 2026-07-11 proposal transcribable; UI try-outs pass

## Notes

Canonical use case for Hari mode. Greedy-shrink v1 narrative superseded by exact-fill v1.1.