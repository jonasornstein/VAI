Whe# 2026-09-19 — Travsport startlist field coverage (Färjestad V85)

| Field | Value |
|-------|-------|
| **AIRUP phase** | I (Inbox) |
| **Status** | Raw |
| **Topic** | Can VAI present bana, AVD, spår, kusk, last 5, odds, V85 %, home-track km from ST startlists? |
| **Race day** | Färjestad 2026-09-19 V85 |
| **ATG game id** | `V85_2026-09-19_15_5` |
| **ST raceday** | `ts616654` (lopp 5–12) |

## User-supplied Sportapp URLs (not fetched)

Direct GET from this environment returns HTTP 403 (Baffin Bay bot protection). ST startlist pages also omit odds, V85 %, last-5 form rows, and km. Do not scrape.

- https://sportapp.travsport.se/race/raceday/ts616654/startlist/5
- https://sportapp.travsport.se/race/raceday/ts616654/startlist/6
- https://sportapp.travsport.se/race/raceday/ts616654/startlist/7
- https://sportapp.travsport.se/race/raceday/ts616654/startlist/8
- https://sportapp.travsport.se/race/raceday/ts616654/startlist/9
- https://sportapp.travsport.se/race/raceday/ts616654/startlist/10
- https://sportapp.travsport.se/race/raceday/ts616654/startlist/11
- https://sportapp.travsport.se/race/raceday/ts616654/startlist/12

## Presentation source used instead

Read-only ATG racinginfo API (existing VAI path, SUP-C-003):

- `GET https://www.atg.se/services/racinginfo/v1/api/games/V85_2026-09-19_15_5`
- `GET https://www.atg.se/services/racinginfo/v1/api/horses/{id}/results` (last 5)

Assembled snapshot: `inbox/research/2026-09-19-farjestad-start-info.json`

- Re-fetched: 2026-09-19T12:13:16Z (compact last-5 + estimated km)
- Unique horses: 99
- Horse-results errors: 0
- Scratches: Wise Emotions (V85-1), Comedy (V85-1), Classic Hill U.S. (V85-7)

### Last 5 compact

Newest first. ATG `disqualified` → `d`. Place 1–15 → digit. Else (`place` 0, missing, galopp without DQ, utgick) → `o` (osk!).

### km

Estimated driving km home track → Färjestad, rounded to 10. **Not** official ST avståndstabell. Missing ATG `homeTrack` (often Norwegian) → `—`.
