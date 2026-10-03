# Fundamental mode v1 — sortable start-info tables

| Field | Value |
|-------|-------|
| **Version** | 1.1 |
| **Status** | APPROVED (published `outbox/specs/fundamental-v1.md`) |
| **AIRUP phase** | P |
| **Reviewer** | ornstein (operator, 2026-09-19) |
| **Last updated** | 2026-10-03 |
| **Live UI** | `outbox/mockups/v85-proposal-ux-mockup-atg.html` |

## 1. Purpose

Inspect-only läge **FUNDAMENTAL** between Expert and Kvantitativ. One sortable table per V85 avdelning (sub-tabs AVD1–AVD8). Does **not** generate a slip.

## 2. Fields

| Column | ATG / derived |
|--------|----------------|
| Nr | `starts[].number` |
| Spår | `starts[].postPosition` |
| Häst | `horse.name` |
| Kusk | `driver.firstName` + `lastName` |
| Tränare | `horse.trainer.firstName` + `lastName` |
| Last 5 | horse results: `d` if `disqualified`, else place 1–15, else `o` (osk!) |
| Odds | `pools.vinnare.odds` / 100 |
| V85 % | `pools.V85.betDistribution` / 10000 |
| Häst km | estimate home track → race track |
| Kusk km | estimate driver home track → race track |
| Tränare km | estimate trainer home track → race track |
| Anm | `STRUKEN` if `scratched` |

km is **ESTIMATE** (haversine × 1.35, round 10). Not ST avståndstabell.

## 3. API

`GET /api/v1/start-info/{game_id_or_yaml_id}?include_form=1`

- `include_form=1` (default): fetch last-5 (cached per horse id).
- `include_form=0`: refresh odds / V85 % / scratches from game JSON; reuse last-5 cache.

Strukna remain in `starts_by_leg`. YAML: numbers (+ names if present); other columns null; refresh disabled.

## 4. UX

- Tabs: Hari \| Expert \| FUNDAMENTAL \| Kvantitativ (disabled)
- AVD1–AVD8 sub-tabs; default AVD1
- Column header click sorts asc/desc
- **Uppdatera** reloads live odds, booking %, strykningar
- Horse grid / Generera / Expert roster hidden in this mode

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-09-19 | APPROVED — live UI + API shipped |
| 1.1 | 2026-10-03 | Tränare + Tränare km from `horse.trainer` (same name and km estimate as Kusk) |
