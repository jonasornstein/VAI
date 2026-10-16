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
  `start_snapshots` (keyed by date/game/leg/start_no). See `src/vai/bets.py`.

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
for that date/game are used. If neither exists, the card check is skipped. There is no live
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
copies `final_odds`/`final_streck_pct` per pick from `start_snapshots`, and computes
`payout` = Σ over tiers of (rows with exactly *k* correct × `payouts[k]` per row) when
`payouts` is given, else `null`. Returns `{"settled":<n bets>,"bets":[...]}`.

### `POST /api/snapshots`

```json
{"date":"2026-10-17","game":"V85","track":"Solvalla",
 "starts":[{"leg":1,"startNo":1,"horseName":"A","scratched":false,"finalOdds":2.9,"streckPct":33.0}]}
```

Upserts by (date, game, leg, startNo); `captured_at` is set server-side. Returns
`{"upserted":<n>}`. Python: `vai.bets.record_snapshots(store, body)`.
