# Race info v1 — leg header metadata

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Status** | APPROVED |
| **Reviewer** | Nisse, ornstein |
| **Approved** | 2026-07-08 |
| **AIRUP phase** | P |
| **Last updated** | 2026-07-08 |
| **Implements** | F-029, UC-15 |
| **Extends** | [atg-data-source.md](./atg-data-source.md), [local-ui-v1.1.md](./local-ui-v1.1.md) |

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
| `status` | `status` | Stored; not shown in v1 UI when `upcoming` |

---

## 3. UI layout

```
V85-5 · 16:10 · 2140 m · Volt          ← .race-info-primary
STL Stodivisionen (Försök 7…)         ← .race-info-secondary
3-åriga och äldre svenska ston…       ← .race-info-class
```

When `race_info` absent (manual YAML): `V85-N · HH:MM` only.

---

## 4. YAML fallback

Optional per leg in [race-card-schema.md](../../docs/requirements/race-card-schema.md).

---

## 5. Parser fix (v1)

ATG `starts[].scratched` horses excluded from `legs[].horses` (schema rule 5).

---

## 6. Deferred (v1.2+)

- `prize`, full `terms[]`, pool turnover
- Per-horse names/drivers/odds in grid
- Race info on printed slip

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-08 | APPROVED — F-029, leg header UI, scratches fix |