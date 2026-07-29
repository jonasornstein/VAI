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
3. **Soft-hide** — experts are **never hard-deleted** from the working roster. Set `visible: false` (VISA EXPERTER popup, or `DELETE` / PUT). Tip YAML under `inbox/expert-tips/` is **kept**.
4. **Main Expert panel** — shows only `visible: true` experts.
5. **Full reset** — `POST /api/v1/experts/reset` overwrites `roster.yaml` with shipped defaults (API only; not on the toolbar). Tips are not deleted.

## UI

Expert tab:

- **Lägg till expert** — create a new roster entry
- **VISA EXPERTER** — popup: tick-boxes, **Markera/Avmarkera alla**, **↑/↓** display order
- Main list — **visible experts only** in roster order; count shows `N synliga av M · K med tip …`
- Tip form icon on each card

## API

```text
GET    /api/v1/experts              # all (incl. hidden) + counts — VISA EXPERTER popup
GET    /api/v1/experts?visible=1    # visible only — main Expert panel
GET    /api/v1/experts?visible=0    # hidden only
POST   /api/v1/experts
PUT    /api/v1/experts/{expert_id}  # incl. { "visible": true|false }
PUT    /api/v1/experts/visibility   # { "visible": true|false } — all non-fixture
PUT    /api/v1/experts/reorder      # { "order": ["id-a", "id-b", ...] }
DELETE /api/v1/experts/{expert_id}  # soft-hide (visible=false)
POST   /api/v1/experts/reset        # full overwrite with defaults (API)
```

Display order is the order of entries in `roster.yaml` (and the defaults file).

## Schema

Same as defaults (`expert_id`, `display_name`, optional product/outlet/url/notes/`free`/`publishes_full_system`) plus:

| Field | Notes |
|-------|--------|
| `visible` | bool; default **true** when missing |

See [outbox/specs/expert-roster-manage-v1.md](../../outbox/specs/expert-roster-manage-v1.md) (**APPROVED**).

## Do not

- Commit paywalled tip content here (this file is roster metadata only).
- Expect `docs/strategies/expert.md` tables to auto-update when you edit the roster.
