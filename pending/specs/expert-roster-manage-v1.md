# Expert roster manage — v1 implementation spec

| Field | Value |
|-------|-------|
| **Version** | 0.1 |
| **Status** | AWAITING_OPERATOR |
| **AIRUP phase** | R |
| **Reviewer** | ornstein (UX), Nisse (default roster fidelity) |
| **Author** | Assistant |
| **Last updated** | 2026-07-28 |
| **Implements** | F-044–F-048; UC-12 extension (manage roster) |
| **Parent** | [expert-v1.md](../../outbox/specs/expert-v1.md) |

---

## 1. Purpose

Let the operator **add**, **edit**, **delete**, and **fully restore** the expert roster used by Expert mode. Shipped defaults stay immutable; the working copy is operator-editable.

Tip YAML under `inbox/expert-tips/` is unchanged (enter/edit/delete tips already shipped).

---

## 2. Resolved decisions

| ID | Topic | Decision |
|----|-------|----------|
| ER-001 | Storage | Editable **full copy** at `inbox/experts/roster.yaml`; defaults at `src/vai/strategies/experts.yaml` |
| ER-002 | Cold start | Missing working file → load defaults (no write until first mutation) |
| ER-003 | First mutation | Materialize full default copy into working path, then apply change |
| ER-004 | Delete | Remove from roster only; **do not** delete tip YAML |
| ER-005 | Reset | Full reset: overwrite working roster with shipped defaults |
| ER-006 | Edit | PUT updates metadata; `expert_id` immutable |
| ER-007 | Fixture | UI excludes `fixture`; cannot delete via API (`FORBIDDEN_ID`) |

---

## 3. Paths

| Role | Path |
|------|------|
| Defaults (immutable) | `src/vai/strategies/experts.yaml` |
| Working (mutable) | `inbox/experts/roster.yaml` |

---

## 4. Schema

Same fields as defaults:

| Field | Required |
|-------|----------|
| `expert_id` | Yes — slug `[a-z0-9]+(-[a-z0-9]+)*` |
| `display_name` | Yes |
| `product_name`, `outlet`, `source_url`, `notes` | No |
| `publishes_full_system` | No — bool or string (`partial`, etc.) |
| `free` | No — bool |

---

## 5. API

| Method | Path | Result |
|--------|------|--------|
| GET | `/api/v1/experts` | Effective roster + tip annotations (unchanged shape) |
| POST | `/api/v1/experts` | Add → `201` + entry |
| PUT | `/api/v1/experts/{expert_id}` | Update → `200` + entry |
| DELETE | `/api/v1/experts/{expert_id}` | Remove → `200` + deleted entry |
| POST | `/api/v1/experts/reset` | Full reset → `200` + `{ experts, restored: true }` |

### Error codes

| Code | HTTP | When |
|------|------|------|
| `INVALID_EXPERT` | 400 | Schema / missing fields / bad id |
| `EXPERT_EXISTS` | 409 | POST duplicate id |
| `EXPERT_NOT_FOUND` | 404 | PUT/DELETE unknown |
| `FORBIDDEN_ID` | 400 | Delete/mutate reserved `fixture` |
| `WRITE_FAILED` | 500 | IO error |

---

## 6. Operator UX

Expert tab toolbar:

- **Lägg till expert** — modal (name, id slug, optional metadata, free checkbox)
- **Återställ roster** — confirm full reset (tips not deleted)

Per card: remove control with confirm (tips kept). Tip form icon unchanged.

---

## 7. Non-goals

- Cascade-delete tips
- Scraping / auto roster sync from research
- Auth on write endpoints
- Auto-update of `docs/strategies/expert.md` tables

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-07-28 | Initial spec from approved plan |
