# Review — Expert roster manage v1

| Field | Value |
|-------|-------|
| **Artifact** | [expert-roster-manage-v1.md](../specs/expert-roster-manage-v1.md) |
| **Reviewer** | ornstein (operator UX) |
| **Date** | 2026-07-29 |
| **Verdict** | **APPROVED** |
| **Version** | 0.4 |

---

## Findings

- [x] Working roster path `inbox/experts/roster.yaml` + immutable defaults
- [x] Soft-hide only (`visible`); tip YAML never cascade-deleted
- [x] Main panel = visible experts only; **VISA EXPERTER** for manage
- [x] Count `N synliga av M · K med tip …` + list API `counts`
- [x] Markera/Avmarkera alla (`PUT …/visibility`)
- [x] ↑/↓ display order = YAML array order (`PUT …/reorder`)
- [x] `fixture` reserved; no hard-delete of roster rows
- [x] Shipped and tested on `master` (`879e1e6`, `dd09fc3`, …)

## Notes

Canonical published path: `outbox/specs/expert-roster-manage-v1.md`. Parent: [expert-v1.md](../specs/expert-v1.md).
