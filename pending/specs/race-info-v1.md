# Race info v1 — leg header metadata

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Status** | APPROVED |
| **Approved** | 2026-07-08 |
| **AIRUP phase** | R |
| **Author** | Assistant |
| **Last updated** | 2026-07-08 |
| **Implements** | F-029, UC-15 |
| **Extends** | [atg-data-source.md](../../outbox/specs/atg-data-source.md), [local-ui-v1.1.md](../../outbox/specs/local-ui-v1.1.md) |

---

## 1. Purpose

Show **race-level** metadata beside start time in each V85 avdelning header. Data parsed from existing ATG `games/{game_id}` JSON (no extra fetch).

---

## 2. Fields (v1)

| `race_info` field | ATG `races[]` source | UI (SV) |
|-------------------|----------------------|---------|
| `race_name` | `name` | Line 2, truncated, full in `title` |
| `distance_m` | `distance` | e.g. `2140 m` on primary line |
| `start_method` | `startMethod` | `volte`→Volt, `auto`→Autostart |
| `class_summary` | `terms[0]` | Line 3, truncated |
| `status` | `status` | Optional; omitted when `upcoming` |

---

## 3. UI layout

```
V85-5 · 16:10 · 2140 m · Volt          ← .race-info-primary
STL Stodivisionen (Försök 7…)         ← .race-info-secondary
3-åriga och äldre svenska ston…       ← .race-info-class
```

When `race_info` absent (manual YAML): `V85-N · HH:MM` only (current behavior).

---

## 4. YAML fallback

Optional per leg in [race-card-schema.md](../../docs/requirements/race-card-schema.md):

```yaml
race_info:
  race_name: "…"
  distance_m: 2140
  start_method: volt
  class_summary: "…"
```

---

## 5. Deferred (v1.2+)

- `prize`, full `terms[]`, pool turnover
- Per-horse names/drivers/odds in grid
- Race info on printed slip
- HTML scrape (F-008)

---

## 6. Tests

- Parse sample ATG game JSON leg 1
- Scratches excluded from `horses`
- API JSON includes `race_info`
- YAML optional `race_info` load