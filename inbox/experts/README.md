# Expert roster (operator-editable)

Working **expert roster** for Expert mode (UC-12). Shipped defaults live in code; this folder holds the operator’s full editable copy.

## Paths

| Role | Path |
|------|------|
| **Defaults (immutable)** | `src/vai/strategies/experts.yaml` |
| **Working (mutable)** | `inbox/experts/roster.yaml` |

## Behaviour

1. **Cold start** — if `roster.yaml` is missing, the UI/API uses shipped defaults (no file written).
2. **First mutation** — defaults are copied into `roster.yaml`, then the change is applied.
3. **Soft-hide** — experts are **never hard-deleted** from the working roster. Set `visible: false` (Visa tick-box off, or `DELETE` / PUT). Tip YAML under `inbox/expert-tips/` is **kept**.
4. **Återställ roster** — overwrites `roster.yaml` with the exact shipped defaults (full reset). Tips are not deleted; custom experts are removed by overwrite.

## UI

Expert tab:

- **Lägg till expert** — create a new roster entry
- **Visa** tick-box on each card — show/hide (`visible`)
- **Återställ roster** — restore defaults (confirm)

Hidden experts stay in the list (muted) so you can re-check **Visa**.

## API

```text
GET    /api/v1/experts              # all (incl. hidden)
GET    /api/v1/experts?visible=1    # visible only
GET    /api/v1/experts?visible=0    # hidden only
POST   /api/v1/experts
PUT    /api/v1/experts/{expert_id}  # incl. { "visible": true|false }
DELETE /api/v1/experts/{expert_id}  # soft-hide (visible=false)
POST   /api/v1/experts/reset
```

## Schema

Same as defaults (`expert_id`, `display_name`, optional product/outlet/url/notes/`free`/`publishes_full_system`) plus:

| Field | Notes |
|-------|--------|
| `visible` | bool; default **true** when missing |

See [pending/specs/expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md).

## Do not

- Commit paywalled tip content here (this file is roster metadata only).
- Expect `docs/strategies/expert.md` tables to auto-update when you edit the roster.
