# Expert roster (operator-editable)

Working **expert roster** for Expert mode (UC-12). Shipped defaults live in code; this folder holds the operator’s full editable copy.

## Paths

| Role | Path |
|------|------|
| **Defaults (immutable)** | `src/vai/strategies/experts.yaml` |
| **Working (mutable)** | `inbox/experts/roster.yaml` |

## Behaviour

1. **Cold start** — if `roster.yaml` is missing, the UI/API uses shipped defaults (no file written).
2. **First add/delete** — defaults are copied into `roster.yaml`, then the change is applied.
3. **Delete expert** — removes the person from the roster only. Tip YAML under `inbox/expert-tips/` is **kept**.
4. **Återställ roster** — overwrites `roster.yaml` with the exact shipped defaults (full reset). Tips are not deleted.

## UI

Expert tab:

- **Lägg till expert** — create a new roster entry
- Trash icon on each card — remove from roster
- **Återställ roster** — restore defaults (confirm)

## API

```text
GET    /api/v1/experts
POST   /api/v1/experts
PUT    /api/v1/experts/{expert_id}
DELETE /api/v1/experts/{expert_id}
POST   /api/v1/experts/reset
```

## Schema

Same as defaults (`expert_id`, `display_name`, optional product/outlet/url/notes/`free`/`publishes_full_system`).

See [pending/specs/expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md).

## Do not

- Commit paywalled tip content here (this file is roster metadata only).
- Expect `docs/strategies/expert.md` tables to auto-update when you edit the roster.
