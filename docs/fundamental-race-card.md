# FUNDAMENTAL = race card (v1.3.8)

**Status:** Published in v1.3.8 (2026-10-12). Approved by ornstein (Jonas).

## What changed and why

The FUNDAMENTAL mode panel in the operator UI
(`outbox/mockups/v85-proposal-ux-mockup-atg.html`) is replaced by a full
**race card** (startlista) for the selected game: all legs, horses, driver,
trainer, opening/current odds and recent form. Operators wanted the same
information they read on ATG directly inside VAI while building a system,
instead of the earlier FUNDAMENTAL summary columns (Tränare / Tränare km, v1.3.7).

## Endpoint

`GET /api/v1/card/{gameId}` — e.g. `/api/v1/card/V85_2026-10-17_16_5`

- Returns the game with all legs (8 for V85) and starts per leg.
- `?include_form=cached` — attach per-horse form only from the local form
  cache (no extra ATG calls for horses not cached yet).
- Implemented in `src/vai/card.py`, route in `src/vai/server.py`.

## Caches (runtime, not versioned)

| Path | Content | Rule |
|------|---------|------|
| `inbox/card-odds/<gameId>.json` | Opening odds per start, saved first time a real value is seen | Placeholders `99.99`, `1.00`, `0` are skipped (not real odds) |
| `inbox/card-form/<horseId>.json` | Horse form/history | Keyed on career start count; refetched only when the count changes |

Both directories must exist and be writable by the service user `vai`
under `/opt/vai`. They are listed in `.gitignore`.

## ATG fetch rule (no timers)

ATG is fetched **only** when:
1. The FUNDAMENTAL panel is opened,
2. Datum or Bana is changed,
3. The operator presses **Uppdatera**.

No polling, no background timers. `src/vai/atg_fetch.py` reuses the HTTP
connection and shares one game fetch for 5 s so concurrent requests
(card + form) do not duplicate calls.

## UI

- CSS scoped under `#fundamental-panel` (does not leak into other modes).
- Color dropdown, default **VAI-tema**.
- Columns sortable; sort choice persisted in the browser (localStorage).

## Files

- `src/vai/card.py` (new), `src/vai/server.py`, `src/vai/atg_fetch.py`
- `outbox/mockups/v85-proposal-ux-mockup-atg.html`
- `tests/test_card.py` (new) — full suite 148 tests pass
- `pyproject.toml`, `src/vai/__init__.py` → version 1.3.8

## Parallel test race card (~/v85-card, port 8090) — kept by decision

A separate prototype race card lives on Hetzner in `~/v85-card` (user
`ornstein`, **not** in this repo), served by `serve.py` on port 8090.
`refresh_sched.sh` loops `seed_live.py`: every ~2 h (110–130 min) until
Sat 2026-10-17 09:00 UTC (11:00 Malta), then every 90–150 s, final pull and
stop at 2026-10-17 13:05 UTC (15:05 Malta). Logs: `refresh.log`, `updates.log`.
Jonas decided to keep it running in parallel with the in-app card until then.
Do not kill it or merge it into VAI without his say-so.

## Deploy

Standard: `sudo bash deploy/update-server.sh` (see `docs/deploy-hetzner.md`),
then ensure `/opt/vai/inbox/card-odds` and `/opt/vai/inbox/card-form` exist,
owned by `vai`.

## Streck arrows (v1.3.9)

`add_streck_flags` in `src/vai/card.py` runs inside `build_card()` and adds these fields to each starter:

- `winChancePct`: 1/odds normalized to 100% over the live (non-scratched) starters in the leg, 1 dp.
- `streckRatio`: `bookingPct / winChancePct`, rounded to 2 dp.
- `streckFlag`: decided on the **rounded** `streckRatio`. `"over"` if >= 1.30, `"under"` if <= 0.70, otherwise `null`. So 1.296 → 1.30 → over, and 1.294 → 1.29 → no flag.
- All three are `null` when the horse is scratched or odds or streck are missing. `streckFlag` is `null` when both streck % and win chance are below 3%.

UI (`outbox/mockups/v85-proposal-ux-mockup-atg.html`): orange ▲ for over, green ▼ for under, with a tooltip. A sortable **Kvot** column sits after **Streck %**.

## v1.3.10: form order, column order, version text

- `formLast5` is now **newest first** (for example `1-3-x-2-5`, where the first token is the latest start). The Form tooltip and the UI help text say "senaste först".
- `sortableColumns` puts **Öppning** (`oddsOpen`) and **Δ** (`oddsDelta`) right after **km / Hemmabana**. The panel (`rcColumns()` in the mockup html) renders the server order as is, so `card.py` controls it. Only Kvot (`streckRatio`) is added on the client, after Streck %.
- The version text in the UI comes from `vai.__version__`. The html holds `{{VAI_VERSION}}` (5 places), and `server.render_index_html` fills it in when serving `/`. Don't hardcode a version in the html; `tests/test_version_text.py` enforces this.

## v1.3.11: sort indicator and streck alignment

- Sort indicator: a thin ↑/↓ in the header text colour (`color: inherit`) instead of a green ▲/▼. Unsorted sortable columns show a faint ↕.
- Streck % cell (`.streck-cell`): right-aligned. The ▲/▼ arrow has a fixed width of 1em. Rows without an arrow get an invisible ▲ placeholder (`visibility:hidden`, `aria-hidden`), so the % values line up.
