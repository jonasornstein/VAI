# Race card — data schema (v1)

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Status** | APPROVED |
| **Reviewer** | Povl (format), Nisse (scratches/reserves) |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Owner** | Povl (format), Nisse (scratches/reserves) |
| **Glossary** | [VISION.md §8 — Race card](../VISION.md#8-glossary) |
| **Spec** | [atg-data-source.md](../../outbox/specs/atg-data-source.md) (ATG mapping) |

Canonical file location: `inbox/race-cards/<YYYY-MM-DD>-<track>.yaml`

**v1.1 ingestion:** ATG `game_id` via F-007 (primary in local UI). **Fallback:** manual YAML in `inbox/race-cards/`.

---

## Required fields

| Field | Type | Description |
|-------|------|-------------|
| `game` | string | `v85` (default in v1) |
| `date` | ISO date | Race day `YYYY-MM-DD` |
| `track` | string | Track name (e.g. `Halmstad`) |
| `legs` | array[8] | Exactly 8 leg objects for V85 |
| `source` | enum | `atg` \| `atg-api` \| `atg-web` \| `manual` |
| `fetched_at` | ISO datetime | When card was collected |
| `settled` | boolean | All legs have official results (drives F-027 default date) |

### Leg object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `leg` | int 1–8 | Yes | Leg number |
| `race_label` | string | Yes | e.g. `V85-1` |
| `start_time` | string | No | Local time `HH:MM` |
| `horses` | int[] | Yes | Eligible start numbers (non-scratched) |
| `scratches` | int[] | No | Strukna hästar (excluded from `horses`) |
| `reserves` | int[] | No | Reserve order if applicable |
| `race_info` | object | No | Race-level metadata (UC-15); see below |

#### `race_info` object (optional)

| Field | Type | Description |
|-------|------|-------------|
| `race_name` | string | Full race title from ATG |
| `distance_m` | int | Distance in metres |
| `start_method` | enum | `volt` \| `auto` |
| `class_summary` | string | First eligibility/terms line |
| `status` | string | e.g. `upcoming`, `results` |

ATG ingestion populates via **F-029**; manual YAML may omit.

---

## Example

```yaml
game: v85
date: 2026-07-05
track: Halmstad
source: manual
fetched_at: 2026-07-05T10:00:00+02:00
settled: false
legs:
  - leg: 1
    race_label: V85-1
    start_time: "15:00"
    horses: [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12]
    scratches: [5]
    reserves: [7, 12]
  - leg: 2
    race_label: V85-2
    start_time: "15:20"
    horses: [1, 3, 4, 6, 8, 9, 11]
  # ... legs 3–8
```

---

## Validation rules (F-005)

1. `legs.length === 8` for V85
2. Each `leg` field unique 1..8
3. Each `horses` array non-empty
4. Horse numbers positive integers, unique within leg
5. `scratches` ∩ `horses` = ∅
6. All selections in proposals must ⊆ `horses` for that leg (F-021)

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.1 | 2026-07-08 | Optional `race_info` per leg (UC-15, F-029) |
| 1.0 | 2026-07-07 | APPROVED — v1.1 ATG primary; `source: atg` aligned with implementation |
| 0.3 | 2026-07-07 | v1 primary ingestion = manual YAML; ATG fetch v1.1+ |
| 0.2 | 2026-07-06 | Primary ingestion via ATG auto-fetch; source enum |
| 0.1 | 2026-07-06 | Initial YAML schema for v1 |