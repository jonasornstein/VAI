# UC-09 — Select race day and fetch from ATG

| Field | Value |
|-------|-------|
| **ID** | UC-09 |
| **Status** | APPROVED |
| **Version** | 1.0 |
| **Reviewer** | Jonte (operator), Nisse (ATG read-only) |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Primary actor** | Operator |
| **Preconditions** | Network available; ATG website or API reachable for read-only race data |

## Brief description

Operator selects **DATUM** in UX; system fetches schedule from ATG and populates **BANA** and **SPELFORM** dropdowns. Race card loads automatically for the selected round.

## Main success scenario

1. On UX load, **F-027** `resolve_next_v85_date`:
   - If today's V85 round exists and **not all legs settled** (results missing) → default **DATUM** = today.
   - If today's round fully settled → default **DATUM** = next future V85 date on ATG.
   - If no V85 today → default **DATUM** = next future V85 date on ATG.
2. System invokes **F-006** `fetch_atg_schedule` for default date (and game filter `v85`).
3. **F-028** `populate_race_day_dropdowns` fills:
   - **BANA** — tracks hosting selected round
   - **SPELFORM** — game forms available (default `V85`)
4. Operator may change **DATUM**; on change, repeat steps 2–3.
5. Operator selects **BANA** and **SPELFORM** (V85 default).
6. **F-007** `fetch_race_card_from_atg` — download startlista for selected date/track/game.
7. **F-005** `validate_race_card`; **F-001** `store_race_card` → cache in `inbox/race-cards/` (and session).
8. UX displays 8 legs with eligible horses per leg (race card populated).
9. Operator proceeds to horse selection and UC-10.

## UX fields (meta bar)

| UX label | Requirement |
|----------|-------------|
| **DATUM** | Date picker; default per step 1 |
| **BANA** | Dropdown; options from ATG schedule for DATUM |
| **SPELFORM** | Dropdown; default V85 |

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 1a | ATG unreachable | Show error; offer manual UC-01 fallback (cached or file upload) |
| 6a | Selected round cancelled | Show status; pick next date |
| 6b | Partial results (some legs settled) | Load card for remaining legs; flag settled legs read-only |
| 7a | API unavailable | **F-008** `scrape_atg_race_card` from public website (same validation) |

## Functions invoked

F-006, F-007, F-008, F-027, F-028, F-001, F-005

## Special requirements

- [SUP-F-008](../supplementary-specification.md#1-functionality-cross-cutting) — automatic race card collection
- [SUP-U-006](../supplementary-specification.md#2-usability) — UX workflow
- [SUP-I-005](../supplementary-specification.md#7-implementation-constraints) — read-only ATG access; no bet placement

## Notes

- ATG data source: [atg-data-source.md](../../../outbox/specs/atg-data-source.md) APPROVED — API primary, HTML scrape fallback (F-008).
- Legal/ToS review for automated fetch remains operator responsibility before production use.

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | APPROVED — v1.1 ATG schedule + race card fetch; matches local UI |