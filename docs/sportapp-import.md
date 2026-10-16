# Sportappen import (#5, T-5 / K-05)

Imports **manually downloaded** Sportappen Excel exports (start list and results)
into the VAI SQLite database for private analysis (field list: erik's doc
"#5 Sportappen-export – samlad fältlista").

## Data terms (JR's conditions) — mandatory

1. **Download is done manually by Jonas.** VAI contains no download code: no HTTP
   to travsport.se or ATG, no scraping, no scheduler. A test enforces that
   `vai.sportapp_import` imports no network modules.
2. **The data stays behind the password.** It is never shared or published.
3. **Not commercial.** The data is used for private, non-commercial analysis only.
4. **If VAI is ever made available to others, Svensk Travsport must be asked first.**
5. **No exposure before K-01.** Imported data must not be exposed via any API
   endpoint or UI until password protection (K-01) exists. This change adds no
   endpoints; a test asserts `server.py` does not reference the sportapp tables.
6. **Never commit real exports.** The files are copyrighted. Keep them under
   `data/` (gitignored). Tests use synthetic files generated at test time.

## Usage

```bash
VAI_DB_PATH=/opt/vai/data/vai.sqlite \
python -m vai.sportapp_import --raceday-id ts616707 --date 2026-10-10 --track Solvalla \
    data/sportapp/solvalla-2026-10-10/startlista.xlsx \
    data/sportapp/solvalla-2026-10-10/resultat.xlsx
```

- File type (start list vs results) is detected from the header in column B
  (`Häst` → start list, `Plac.` → results).
- The exports contain **no date, track or raceday id**, so they are given on the
  command line (`--raceday-id` required; a `ts` prefix is stripped).
- DB path: `--db`, else `$VAI_DB_PATH`, else `/opt/vai/data/vai.sqlite`.
- Re-import is idempotent: upsert keyed by `(raceday_id, race_no, start_no)`.
- Python API: `parse_file(path)`, `store(conn, parsed, raceday_id=...)`,
  `import_files(paths, raceday_id=..., db=...)`.
- Parsing uses the stdlib only (zipfile + ElementTree), no new dependency.

## Column layout (read by position, never by header name)

Some exports repeat header titles (e.g. two columns titled "Bana"), so all
columns are read by position (A = 0).

Start list: A race header (`Lopp N. Starttid HH:MM`), B `"<startNo>  <HORSE>"`,
C sex, D age, E driver, F `post/distance`, G start sum (kr, NBSP thousands),
H trainer, I owner, J shoes, K sulky. Strikethrough on B = scratched; red font
on K is stored as `sulky_flagged`.

Results: A race header, B placing (`1..n`, `0` unplaced, `d` disqualified,
empty = scratched), C horse (scratched rows: `"<no> HORSE  (reason)"`),
D driver, E trainer, F `post/distance`, G km time, H shoes, I sulky,
J odds, K place odds.

Km time `12,3a` → `km_time_s = 72.3` (1:12.3), `a` = auto start, `g` = gallop.
The raw string is always kept in `km_time_raw`. Handicap (`handicap_m`) is the
distance minus the shortest distance in the race.

## Tables

- `sportapp_races(raceday_id, race_no, race_date, track, start_time, base_distance, imported_at)` PK `(raceday_id, race_no)`
- `sportapp_starts(raceday_id, race_no, start_no, horse, sex, age, driver, trainer, owner, post, distance, handicap_m, start_sum_kr, shoes, sulky, sulky_flagged, scratched, imported_at)` PK `(raceday_id, race_no, start_no)`
- `sportapp_results(raceday_id, race_no, start_no, horse, place_raw, place, disqualified, km_time_raw, km_time_s, auto_start, gallop, driver, trainer, post, distance, handicap_m, shoes, sulky, odds, place_odds, scratched, scratch_reason, imported_at)` PK `(raceday_id, race_no, start_no)`

## Open issues

- The sample exports (Solvalla 2026-10-10) have **no "Bana" columns** and no
  date/track; the "two Bana columns" layout has not been seen yet. When such a
  file arrives, extend the position maps (`START_COLS` / `RESULT_COLS`).
- Odds and place-odds columns were empty in the sample; closing odds and
  streck % from the field list are not in these exports. Prize money is also missing.
- Time codes without a number (`uag`, `ug`, `kubug`) are stored raw; meaning of
  `u` / `k` / `b` is to be confirmed. `3ag` parses as 1:03 (suspicious; raw kept).
- Meaning of the red Vagn (sulky) cell is assumed to be "changed sulky".
