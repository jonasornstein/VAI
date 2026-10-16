# Bets API ("Mina spel", card T-35)

Backend for tracking placed bets, settling them against results, and recording
start snapshots (final odds / streck %) for odds calibration (Povl). No UI is
exposed yet; the page stays hidden until the sketch is approved.

## Authentication

**Every** endpoint below requires the `X-API-Key` header, **including GET**
(no read access without protection until password protection exists).
Same mechanism as the other write endpoints (`src/vai/api_auth.py`):

| Situation | Status |
|-----------|--------|
| Header missing or wrong | `401` `{"error":{"code":"UNAUTHORIZED"}}` |
| `VAI_API_KEY` not set on server | `503` `{"error":{"code":"API_KEY_NOT_CONFIGURED"}}` |

## Storage

- SQLite (stdlib `sqlite3`), file from env `VAI_DB_PATH`, default `<repo>/data/vai.sqlite`
  (production: `/opt/vai/data/vai.sqlite`). Gitignored (`*.sqlite`, `data/`).
- Schema is created idempotently (`CREATE TABLE IF NOT EXISTS`) on first use; the
  parent directory is created if missing (must be writable by the service user).
- The weekly backup (`deploy/backup/vai-backup.sh`) snapshots every `*.sqlite` under
  `/opt/vai` with the sqlite3 backup API, so the DB is included automatically.
- Tables: `bets`, `bet_picks`, `bet_legs` (results keyed by date/game/leg),
  `snapshots` + `snapshot_starts` (manual snapshot history, K-35; legacy `start_snapshots` unused). See `src/vai/bets.py`.

## Endpoints

### `POST /api/bets`

```json
{"date":"2026-10-17","game":"V85","track":"Solvalla","stakePerRow":0.5,
 "legs":[{"leg":1,"picks":[{"startNo":1,"horseName":"A","streckPct":30.5,"odds":3.2}]}]}
```

The server computes `rows` = product of pick counts per leg and `price` = `rows * stakePerRow`
(client-supplied values are ignored). Returns `201` with the stored bet (shape as in GET).

Validation → `422` `{"errors":[{"leg":2,"startNo":5,"reason":"scratched"}]}`
(field-level errors also carry `"field"`). Reason codes:

| Reason | Meaning |
|--------|---------|
| `empty_leg` | Leg has no picks |
| `duplicate` | Same `startNo` twice in a leg (or same leg twice) |
| `invalid_value` | Bad date (`YYYY-MM-DD`), game, stake, startNo (1–30), streckPct (0–100), odds (≥1) |
| `scratched` | Start is scratched according to the race card |
| `unknown_start` | Start number / leg not on the race card |

Race-card check: if a local YAML race card in `inbox/race-cards/` matches `date` + `game`
(case-insensitive), its `horses`/`scratches` are used; otherwise recorded `start_snapshots`
(latest per leg) for that date/game are used. If neither exists, the card check is skipped. There is no live
ATG fetch on POST.

### `GET /api/bets?date=YYYY-MM-DD`

`date` optional. Returns `{"bets":[...]}`; each bet:

```json
{"id":1,"date":"2026-10-17","game":"V85","track":"Solvalla","rows":6,"stakePerRow":0.5,"price":3.0,
 "createdAt":"2026-10-16T14:00:00+00:00",
 "legs":[{"leg":1,"winner":1,"winnerName":"A","hit":true,
          "picks":[{"startNo":1,"horseName":"A","streckPct":30.5,"odds":3.2,"finalOdds":2.9,"finalStreckPct":33.0}]}],
 "result":{"correct":2,"of":3,"payout":30.0,"settled":true}}
```

Unknown values are `null` (`hit` is `null` until the leg winner is known).

### `POST /api/bets/settle`

```json
{"date":"2026-10-17","game":"V85","legs":[{"leg":1,"winner":1,"winnerName":"A"}],
 "payouts":{"8":12345.0,"7":210.0}}
```

Upserts leg winners (may be sent incrementally), then for every bet on that date/game:
sets `hit` per leg, `correct` (legs hit), `settled` (true when all legs have a winner),
copies `final_odds`/`final_streck_pct` per pick from the latest `phase=final` manual snapshot (see below), and computes
`payout` = Σ over tiers of (rows with exactly *k* correct × `payouts[k]` per row) when
`payouts` is given, else `null`. Returns `{"settled":<n bets>,"bets":[...]}`.

### `POST /api/snapshots` (card K-35: manual snapshots)

**Legal constraint (JR decision, binding):** a snapshot is stored **only** when Jonas presses
**Update** in the UI. One press = one request = one snapshot. The server performs no retries,
loops, timers, scheduling or background fetching, and contains no ATG scraping code. Do not add
an automatic collector. If a request fails, the user simply presses Update again.

Request (the full payload the Update button sends):

```json
{"date":"2026-10-17","game":"V85","track":"Solvalla",
 "source":"manual",
 "phase":"pre",
 "legs":[
   {"leg":1,
    "startTime":"2026-10-17T16:20:00+02:00",
    "winnerStartNo":null,
    "starts":[
      {"startNo":1,"horseName":"A","scratched":false,"odds":3.2,"streckPct":30.5},
      {"startNo":2,"horseName":"B","scratched":true,"odds":null,"streckPct":null},
      {"startNo":3,"horseName":"C","scratched":false,"odds":5.0,"streckPct":12.0}]}]}
```

| Field | Rule |
|-------|------|
| `source` | Required, must be exactly `"manual"`; anything else (or missing) → `422` `invalid_source` |
| `phase` | `"pre"` or `"final"`. `"final"` only when the leg is decided: `winnerStartNo` given, a winner already settled via `/api/bets/settle`, or the start time has passed. Otherwise `422` `not_decided` |
| `legs[].starts` | The **full field**: every start number of the race, scratched ones with `scratched:true`. `odds` ≥ 1 or null, `streckPct` 0–100 or null |
| `legs[].startTime` | Optional ISO datetime (no offset = Swedish local time). Used only if no local race card has a `start_time` for that leg |
| `legs[].winnerStartNo` | Optional; must be a non-scratched start in `starts` |
| `legs[].starts[].horseName` | Optional string. If omitted/null/blank the server fills it from the local YAML race card's `horse_names` (matched on date + game), else from the latest prior snapshot for the same date/game/leg/startNo; otherwise stays `null`. A client-supplied name is always kept |

Full-field check: the known start list comes from the local YAML race card in
`inbox/race-cards/` (matched on date + game; horses + scratches), else from all prior snapshots
for that date/game/leg. Each known start missing from the payload → `incomplete_field`;
with a YAML card, a start not on the card → `unknown_start`. With no known start list the
check is skipped (first snapshot defines the field).

Server-side per stored row: `taken_at` (server time, UTC ISO, seconds), `source='manual'`,
`phase`, `start_time`, `minutes_to_start` = (start time − takenAt) in minutes, 1 dp, negative
after the start, `null` if no start time is known. Rows are **inserted** (tables `snapshots` +
`snapshot_starts`), never overwritten, so the full history is kept.

Response `201`:

```json
{"snapshotId":7,"takenAt":"2026-10-17T12:00:00+00:00","source":"manual","phase":"pre","inserted":3,
 "legs":[{"leg":1,"starts":3,"minutesToStart":140.0,"startTime":"2026-10-17T14:20:00+00:00","winnerStartNo":null}]}
```

Errors `422`, same format as bets: `{"errors":[{"leg":1,"startNo":4,"reason":"incomplete_field"}]}`
(field-level errors also carry `"field"`). Reasons: `invalid_source`, `incomplete_field`,
`unknown_start`, `not_decided`, `duplicate`, `empty_leg`, `invalid_value`. Nothing is stored
when any error is returned.

`GET /api/bets`: a pick stored without `horseName` is returned with the latest non-null snapshot
name for the same date/game/leg/startNo (read-time fallback; the stored pick is unchanged).

Settle: `/api/bets/settle` fills `finalOdds`/`finalStreckPct` from the latest `phase='final'`
row per leg/start (by `taken_at`, then id). `pre` rows never feed settle. The legacy T-35
`start_snapshots` upsert table is kept in the schema but is no longer written or read.

Python: `vai.bets.record_snapshots(store, body, card=None, now=None)`.
