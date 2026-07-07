# Review — Race card data schema

| Field | Value |
|-------|-------|
| **Artifact** | `docs/requirements/race-card-schema.md` |
| **Reviewer** | Povl (format), Nisse (scratches/reserves) |
| **Date** | 2026-07-07 |
| **Verdict** | **APPROVED** |

---

## Findings

- [x] Required fields and leg object match `RaceCard` model in `src/atg/models/race_card.py`
- [x] Validation rules (F-005) align with generator and UI constraints
- [x] `source` enum includes shipped value `atg` per [atg-data-source.md](../specs/atg-data-source.md)
- [x] Scratches/reserves semantics consistent with [v85.md](../../docs/betting/v85.md) §5
- [x] Example YAML matches `inbox/race-cards/2026-07-05-halmstad.yaml` pattern
- [x] ATG-fetched cards (e.g. Årjäng 2026-07-11) validate against schema

## Notes

ATG mapping does not populate `reserves` in v1.1 — manual YAML only. Documented in atg-data-source §5.