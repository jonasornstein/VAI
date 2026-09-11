# Expert STATS — v1 (horse selection frequency)

| Field | Value |
|-------|-------|
| **Version** | 0.1 |
| **Status** | APPROVED |
| **AIRUP phase** | P |
| **Reviewer** | ornstein (UX), Povl (count / percentage rules) |
| **Author** | Assistant |
| **Last updated** | 2026-09-11 |
| **Approved** | 2026-09-11 — ornstein (operator), Povl (math) |
| **Implements** | **F-049** `compute_expert_horse_stats`; UC-12 alternate |
| **Parent** | [expert-v1.md](./expert-v1.md), [expert-roster-manage-v1.md](./expert-roster-manage-v1.md) |
| **Review** | [REVIEW_expert-stats-v1.md](../reviews/REVIEW_expert-stats-v1.md) |

---

## 1. Purpose

In **Expert** mode, show how often each start number appears in transcribed tips for the current race day — **count** `k/N` and **percentage** `100 × k / N` — so the operator can see consensus before building or loading a slip.

Observation only: STATS does not mark horses, change the slip, or invent picks.

---

## 2. Resolved decisions

| ID | Topic | Decision |
|----|-------|----------|
| ES-001 | Control | Toolbar button **STATS** (next to **VISA EXPERTER**); Expert-only |
| ES-002 | Interaction | Toggle (`aria-pressed`); not a blocking modal |
| ES-003 | Grid | When on, horse meta lines show `k/N` and `%` instead of V85 pool % / odds |
| ES-004 | Heat | Background tint by percentage; selected horses keep pool-selected yellow |
| ES-005 | Order | Grid stays start-number order (ATG transcription) |
| ES-006 | Strip | Consensus strip above the legs grid: per-leg horses with `k ≥ 1`, sorted count desc |
| ES-007 | Population `N` | Tips for **date + track** whose `expert_id` is in the **currently shown roster** |
| ES-008 | Visibility | Respect **VISA EXPERTER** (`visible_only`, default true) |
| ES-009 | Free filter | **Visa bara gratis** also filters the population when checked |
| ES-010 | Multi-tip | Each tip is one vote (v1.3.1: two systems from one expert → two votes) |
| ES-011 | Fixture | Excluded (same as roster list) |
| ES-012 | Percentage | `pct = 100.0 * count / N`; `N = 0` → empty payload, no division |
| ES-013 | Unpicked | Horse with no tips: omitted from API `legs[]`; UI shows `0/N` `0%` |
| ES-014 | Scratches | Still show count/%; horse stays disabled |
| ES-015 | Click strip | Focus/scroll to horse on grid; do **not** auto-select |

---

## 3. Function F-049

`compute_expert_horse_stats(tips, date, track) → ExpertHorseStats`

Per leg 1–8, for each horse that appears in at least one tip: `count`, `pct`, `expert_ids`, `expert_names`. Sort: count descending, horse number ascending.

---

## 4. API

`GET /api/v1/expert-stats?date=YYYY-MM-DD&track=TRACK&visible_only=1&free_only=0`

| Query | Default | Notes |
|-------|---------|-------|
| `date` | required | ISO date |
| `track` | required | Track name (normalized match) |
| `visible_only` | `1` | Roster `visible: true` |
| `free_only` | `0` | Roster `free: true` when `1` |

**200** even when `tip_count` is 0:

```json
{
  "date": "2026-07-25",
  "track": "Bollnäs",
  "tip_count": 5,
  "expert_count": 5,
  "tips": [
    {"tip_id": "bjorn-goop-2026-07-25", "expert_id": "bjorn-goop", "expert_name": "Björn Goop"}
  ],
  "legs": {
    "1": [
      {"horse": 3, "count": 5, "pct": 100.0, "expert_ids": ["…"], "expert_names": ["…"]}
    ]
  }
}
```

**400** `MISSING_FIELD` if date or track absent.

Activity log: operation `expert_stats`, type `access`.

---

## 5. CLI

```text
python -m vai expert stats --date YYYY-MM-DD --track TRACK [--free-only] [--all-visible]
```

Default: visible-only, not free-only. `--all-visible` sets `visible_only=false`.

---

## 6. Operator UX

1. Expert tab → **STATS**.
2. Horse buttons: number, `k/N`, `%`; heat by `%`.
3. Strip: `Avd n` then chips `num k/N pct%`; max (and ties) highlighted.
4. Header: `N tips · M experter · {track} {date}`.
5. Empty: `Inga tips att räkna` (suggest **VISA EXPERTER** if roster hidden).
6. Recalc when DATUM / BANA / visibility / gratis-filter / tip save-delete changes while STATS is on.
7. Hari: Expert panel (and STATS) hidden; horse meta back to pool % / odds.

---

## 7. Non-goals

- Auto-build consensus rad from STATS
- Expert weights or one-vote-per-expert collapse
- Modal table / print / CSV
- Hari overlay
- Scraping tips

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-09-11 | APPROVED — numeric `k/N` + percentage overlay; F-049 |
