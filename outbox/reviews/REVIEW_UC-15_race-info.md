# Review — UC-15 Race info

| Field | Value |
|-------|-------|
| **Artifact** | UC-15, race-info-v1.md |
| **Reviewer** | Nisse (terminology), Jonte (operator) |
| **Date** | 2026-07-08 |
| **Verdict** | **APPROVED** |

---

## Findings

- [x] F-029 extracts race name, distance, start method, class from ATG `races[]`
- [x] No extra ATG fetch — same `games/{game_id}` payload
- [x] Multi-line leg header in local UI; YAML fallback when `race_info` absent
- [x] Scratches excluded from `horses` (schema rule 5)
- [x] 34 tests pass including new parser/serialization tests

## Notes

Race-level only per scope. Per-horse grid enrichment deferred.