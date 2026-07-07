# ATG data source — implementation spec

| Field | Value |
|-------|-------|
| **Version** | 0.1 |
| **Status** | APPROVED |
| **AIRUP phase** | R |
| **Reviewer** | Povl (API); Nisse (field semantics) |
| **Approved** | 2026-07-07 · Povl |
| **Author** | Assistant |
| **Last updated** | 2026-07-07 |
| **Implements** | F-006, F-007, F-008, F-027, F-028, UC-09 (partial) |

---

## 1. Purpose

Specify how the local UI and generator consume **live ATG** schedule and race-card data. v1 scope lock deferred this; v1.1 **ships** a subset.

---

## 2. Endpoints (ATG public API)

| ATG resource | Project function | Module |
|--------------|------------------|--------|
| V85 products list | `fetch_v85_products()` | `atg_fetch.py` |
| V85 game by id | `fetch_v85_game(game_id)` | `atg_fetch.py` |
| Schedule for UI | `fetch_atg_schedule()` | `schedule.py` |
| Race card model | `fetch_race_card_from_atg(game_id)` | `atg_race_card.py` |

**Base URL:** `https://www.atg.se/services/racinginfo/v1/api`

**Game id pattern:** `V85_YYYY-MM-DD_{trackId}_{round}`

---

## 3. Local server API

| Route | Method | Description |
|-------|--------|-------------|
| `/api/v1/schedule/v85` | GET | Dates, rounds, default_date |
| `/api/v1/race-cards/{id}` | GET | YAML id **or** ATG game id |
| `/api/v1/generate/random` | POST | Uses either card source |

Errors: `ATG_UNAVAILABLE` (502), `ATG_PARSE_ERROR` (502), `INVALID_ID` (400).

---

## 4. Schedule semantics (F-027, F-028)

- `default_date`: next bettable V85 date (today if unsettled round exists, else next upcoming).
- `rounds[]`: `{ game_id, date, track, track_id, bettable, settled, start_time }`.
- UI: DATUM dropdown ← unique dates; BANA ← rounds for selected date.

---

## 5. Race card mapping (F-007, F-008)

From ATG game JSON:

| RaceCard field | ATG source |
|----------------|------------|
| `legs[].horses` | `races[].starts[].number` (non-scratched eligible) |
| `legs[].scratches` | `starts[].scratched == true` |
| `legs[].start_time` | `races[].startTime` (HH:MM) |
| `source` | `"atg"` |
| `settled` | all races `status == results` |

**Not mapped in v1.1:** driver, distance, form rows, official reserves (reserves `[]` unless manual YAML).

---

## 6. Odds / distributions (F-009 partial)

For F-052 basic hit summary:

| Field | ATG path | Transform |
|-------|----------|-----------|
| V85 bet % | `starts[].pools.V85.betDistribution` | ÷ 10000 → fraction |

Exposed in API as `leg_distributions` on ATG race-card responses.

**Deferred:** Vinnare odds, Plats, full quant odds pipeline (UC-13).

---

## 7. Caching and resilience

| Policy | v1.1 |
|--------|------|
| HTTP cache | None (live fetch per request) |
| Timeout | 15 s |
| User offline | Mockup shows API status; YAML cards still work |

**v1.2 candidates:** disk cache per `game_id`, stale-while-revalidate for race day.

---

## 8. Security and compliance

- Read-only public endpoints; no ATG credentials.
- No automated bet placement (NG-001).
- Respect ATG terms; rate-limit in production deployment (out of scope v1.1).

---

## 9. Tests

| Test | Coverage |
|------|----------|
| `tests/test_schedule.py` | Parse products, default_date |
| `tests/test_server.py::test_api_schedule_v85` | HTTP route |
| Live fetch | Manual / CI optional (network) |

---

## 10. Out of scope

- V86 / V64 schedule (V75 discontinued at ATG)
- Historical results ingestion
- Odds archive to `inbox/odds/`
- Hosted deployment

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-07-07 | Initial spec — documents shipped v1.1 ATG integration |