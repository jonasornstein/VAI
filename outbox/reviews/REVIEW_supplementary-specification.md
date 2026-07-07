# Review — Supplementary Specification (FURPS+)

| Field | Value |
|-------|-------|
| **Artifact** | `docs/requirements/supplementary-specification.md` |
| **Reviewer** | Jonte (operator), Povl (constraints), Nisse (compliance) |
| **Date** | 2026-07-07 |
| **Verdict** | **APPROVED** |

---

## Findings

- [x] Cross-cutting SUP-F-* requirements align with approved UCs and [functions.md](../../docs/requirements/functions.md)
- [x] SUP-F-009 corrected — optional operator marks match Hari v1.1 (empty-leg fill)
- [x] Usability requirements match [ux-workflow.md](../../docs/requirements/ux-workflow.md) and shipped mockup
- [x] SUP-U-005 — F-071 checklist wired in local UI
- [x] SUP-R-003 cost formula verified (13 tests + golden proposals)
- [x] SUP-I-001 / SUP-I-005 — read-only ATG; no bet automation (NG-004)
- [x] SUP-C-003 links to APPROVED atg-data-source spec
- [x] Interface table reflects v1.1 ATG inbound fetch + manual outbound entry
- [x] Deferred items (expert catalog, Monte Carlo, disk cache) remain in open items

## Notes

Completes RUP trilogy non-functional layer alongside approved Vision and use-case model. Expert/quant SUP-F-010 hit-probability scope limited to F-052 basic until UC-13 ships.