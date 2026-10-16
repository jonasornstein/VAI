"""#5 Sportappen import (T-5 / K-05): parse manually downloaded Sportappen Excel exports.

Manual files only. This module never downloads anything: no HTTP, no ATG or
travsport.se access, no scheduler. Jonas downloads the start list / result
exports by hand and runs::

    python -m vai.sportapp_import --raceday-id 616707 --date 2026-10-10 \
        --track Solvalla startlista.xlsx resultat.xlsx

Data terms (Svensk Travsport / JR): see docs/sportapp-import.md. The imported
data stays behind the password, is never shared or published, is not used
commercially, and must NOT be exposed via any API endpoint or UI until
password protection (K-01) exists.

The .xlsx is read with the stdlib (zipfile + ElementTree) so no new dependency
is needed. Columns are read by POSITION, never by header name (Sportappen
exports can repeat header titles, e.g. two columns called "Bana").
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

from vai.distances import norm as _norm_track

DB_PATH_ENV = "VAI_DB_PATH"
DEFAULT_DB_PATH = "/opt/vai/data/vai.sqlite"

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
_M = "{%s}" % _NS["m"]

# Column positions (0-based, column A = 0). Header text is informational only.
START_COLS = {
    "horse": 1, "sex": 2, "age": 3, "driver": 4, "post_dist": 5,
    "start_sum": 6, "trainer": 7, "owner": 8, "shoes": 9, "sulky": 10,
}
RESULT_COLS = {
    "place": 1, "horse": 2, "driver": 3, "trainer": 4, "post_dist": 5,
    "time": 6, "shoes": 7, "sulky": 8, "odds": 9, "plats": 10,
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS sportapp_races (
    raceday_id   TEXT NOT NULL,
    race_no      INTEGER NOT NULL,
    race_date    TEXT,
    track        TEXT,
    start_time   TEXT,
    base_distance INTEGER,
    imported_at  TEXT NOT NULL,
    PRIMARY KEY (raceday_id, race_no)
);
CREATE TABLE IF NOT EXISTS sportapp_starts (
    raceday_id   TEXT NOT NULL,
    race_no      INTEGER NOT NULL,
    start_no     INTEGER NOT NULL,
    horse        TEXT NOT NULL,
    sex          TEXT,
    age          INTEGER,
    driver       TEXT,
    trainer      TEXT,
    owner        TEXT,
    post         INTEGER,
    distance     INTEGER,
    handicap_m   INTEGER,
    start_sum_kr INTEGER,
    shoes        TEXT,
    sulky        TEXT,
    sulky_flagged INTEGER NOT NULL DEFAULT 0,
    scratched    INTEGER NOT NULL DEFAULT 0,
    imported_at  TEXT NOT NULL,
    PRIMARY KEY (raceday_id, race_no, start_no)
);
CREATE TABLE IF NOT EXISTS sportapp_results (
    raceday_id   TEXT NOT NULL,
    race_no      INTEGER NOT NULL,
    start_no     INTEGER NOT NULL,
    horse        TEXT NOT NULL,
    place_raw    TEXT,
    place        INTEGER,
    disqualified INTEGER NOT NULL DEFAULT 0,
    km_time_raw  TEXT,
    km_time_s    REAL,
    auto_start   INTEGER,
    gallop       INTEGER NOT NULL DEFAULT 0,
    driver       TEXT,
    trainer      TEXT,
    post         INTEGER,
    distance     INTEGER,
    handicap_m   INTEGER,
    shoes        TEXT,
    sulky        TEXT,
    odds         REAL,
    place_odds   TEXT,
    scratched    INTEGER NOT NULL DEFAULT 0,
    scratch_reason TEXT,
    imported_at  TEXT NOT NULL,
    PRIMARY KEY (raceday_id, race_no, start_no)
);
"""


# --------------------------------------------------------------------- xlsx

@dataclass
class Cell:
    value: str = ""
    strike: bool = False
    red: bool = False


def _col_index(ref: str) -> int:
    n = 0
    for ch in ref:
        if not ch.isalpha():
            break
        n = n * 26 + (ord(ch.upper()) - 64)
    return n - 1


def read_xlsx(path: str | Path) -> list[list[Cell]]:
    """Return the first sheet as rows of Cells (stdlib only)."""
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        shared: list[str] = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", _NS):
                shared.append("".join(t.text or "" for t in si.iter(_M + "t")))
        xf_font: list[tuple[bool, bool]] = []
        if "xl/styles.xml" in names:
            st = ET.fromstring(z.read("xl/styles.xml"))
            fonts = []
            for f in st.findall("m:fonts/m:font", _NS):
                color = f.find("m:color", _NS)
                red = color is not None and (color.get("rgb") or "").upper().endswith("FF0000")
                fonts.append((f.find("m:strike", _NS) is not None, red))
            for xf in st.findall("m:cellXfs/m:xf", _NS):
                fid = int(xf.get("fontId", "0"))
                xf_font.append(fonts[fid] if fid < len(fonts) else (False, False))
        sheet = "xl/worksheets/sheet1.xml"
        if sheet not in names:
            sheet = sorted(n for n in names if n.startswith("xl/worksheets/sheet"))[0]
        root = ET.fromstring(z.read(sheet))
    rows: list[list[Cell]] = []
    for row in root.iter(_M + "row"):
        cells: list[Cell] = []
        for c in row.findall("m:c", _NS):
            idx = _col_index(c.get("r", "A"))
            while len(cells) < idx:
                cells.append(Cell())
            t = c.get("t")
            v = c.find("m:v", _NS)
            if t == "s" and v is not None:
                val = shared[int(v.text)]
            elif t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter(_M + "t"))
            else:
                val = v.text if v is not None and v.text is not None else ""
            s = int(c.get("s", "0"))
            strike, red = xf_font[s] if s < len(xf_font) else (False, False)
            cells.append(Cell(val.strip(), strike, red))
        rows.append(cells)
    return rows


# ------------------------------------------------------------------ parsing

_RACE_RE = re.compile(r"Lopp\s+(\d+)\.?\s*Starttid\s+(\d{1,2}:\d{2})")
_HORSE_RE = re.compile(r"^(\d+)\s+(.*)$")
_REASON_RE = re.compile(r"^(.*?)\s{2,}\((.*)\)\s*$")
_TIME_RE = re.compile(r"^(\d+(?:,\d)?)?([a-zå]*)$")


def _get(row: list[Cell], i: int) -> Cell:
    return row[i] if i < len(row) else Cell()


def _int(s: str) -> int | None:
    s = re.sub(r"[\s\u00a0]", "", s or "")
    return int(s) if s.isdigit() else None


def _float(s: str) -> float | None:
    s = (s or "").replace(",", ".").strip()
    try:
        return float(s)
    except ValueError:
        return None


def _post_dist(s: str) -> tuple[int | None, int | None]:
    if "/" not in (s or ""):
        return None, None
    a, b = s.split("/", 1)
    return _int(a), _int(b)


def parse_km_time(raw: str) -> dict:
    """'12,3a' -> 1:12.3 auto; 'g' = gallop. Letters kept raw for unclear codes."""
    raw = (raw or "").strip()
    m = _TIME_RE.match(raw)
    if not raw or not m:
        return {"km_time_s": None, "auto_start": None, "gallop": 0}
    num, flags = m.group(1), m.group(2)
    km = None
    if num:
        km = round(60 + float(num.replace(",", ".")), 1)
    return {
        "km_time_s": km,
        "auto_start": 1 if "a" in flags else 0,
        "gallop": 1 if "g" in flags else 0,
    }


@dataclass
class Parsed:
    kind: str  # "startlist" | "results"
    races: dict[int, str] = field(default_factory=dict)  # race_no -> start_time
    rows: list[dict] = field(default_factory=list)


def detect_kind(rows: list[list[Cell]]) -> str:
    head = [c.value for c in rows[0]] if rows else []
    b = head[1] if len(head) > 1 else ""
    if b == "Häst":
        return "startlist"
    if b.startswith("Plac"):
        return "results"
    raise ValueError(f"Unknown Sportappen export layout (column B header {b!r})")


def parse_rows(rows: list[list[Cell]]) -> Parsed:
    kind = detect_kind(rows)
    out = Parsed(kind)
    cols = START_COLS if kind == "startlist" else RESULT_COLS
    race_no = None
    for row in rows[1:]:
        a = _get(row, 0).value
        m = _RACE_RE.search(a)
        if m:
            race_no = int(m.group(1))
            out.races[race_no] = m.group(2)
            continue
        hc = _get(row, cols["horse"])
        hm = _HORSE_RE.match(hc.value)
        if race_no is None or not hm:
            continue
        name, reason = hm.group(2).strip(), None
        rm = _REASON_RE.match(name)
        if rm:
            name, reason = rm.group(1).strip(), rm.group(2).strip()
        post, dist = _post_dist(_get(row, cols["post_dist"]).value)
        rec = {
            "race_no": race_no, "start_no": int(hm.group(1)), "horse": name,
            "driver": _get(row, cols["driver"]).value or None,
            "trainer": _get(row, cols["trainer"]).value or None,
            "post": post, "distance": dist,
            "shoes": _get(row, cols["shoes"]).value or None,
            "sulky": _get(row, cols["sulky"]).value or None,
        }
        if kind == "startlist":
            rec.update(
                sex=_get(row, cols["sex"]).value or None,
                age=_int(_get(row, cols["age"]).value),
                owner=_get(row, cols["owner"]).value or None,
                start_sum_kr=_int(_get(row, cols["start_sum"]).value),
                sulky_flagged=1 if _get(row, cols["sulky"]).red else 0,
                scratched=1 if hc.strike else 0,
            )
        else:
            place_raw = _get(row, cols["place"]).value
            time_raw = _get(row, cols["time"]).value
            scratched = 1 if (reason is not None or (not place_raw and not time_raw)) else 0
            rec.update(
                place_raw=place_raw or None,
                place=int(place_raw) if place_raw.isdigit() and place_raw != "0" else None,
                disqualified=1 if place_raw.lower() == "d" else 0,
                km_time_raw=time_raw or None,
                odds=_float(_get(row, cols["odds"]).value),
                place_odds=_get(row, cols["plats"]).value or None,
                scratched=scratched, scratch_reason=reason,
                **parse_km_time(time_raw),
            )
        out.rows.append(rec)
    # handicap = distance minus shortest distance in the race
    base: dict[int, int] = {}
    for r in out.rows:
        if r["distance"]:
            base[r["race_no"]] = min(base.get(r["race_no"], r["distance"]), r["distance"])
    for r in out.rows:
        b = base.get(r["race_no"])
        r["handicap_m"] = (r["distance"] - b) if (b and r["distance"]) else None
    out.base_distance = base  # type: ignore[attr-defined]
    return out


def parse_file(path: str | Path) -> Parsed:
    return parse_rows(read_xlsx(path))


# ------------------------------------------------------------------ storage

def db_path() -> str:
    import os
    return os.environ.get(DB_PATH_ENV) or DEFAULT_DB_PATH


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


def _upsert(conn, table: str, keys: tuple[str, ...], rec: dict) -> None:
    cols = list(rec)
    upd = ", ".join(f"{c}=excluded.{c}" for c in cols if c not in keys)
    conn.execute(
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))}) "
        f"ON CONFLICT ({', '.join(keys)}) DO UPDATE SET {upd}",
        [rec[c] for c in cols],
    )


def normalize_track(track: str | None) -> str | None:
    """Normalize a track name/code via erik's vai.distances.norm() (e.g. Solvalla -> SOL).

    None/empty stays None. An unknown track raises ValueError so nothing is stored.
    """
    if track is None or not str(track).strip():
        return None
    code = _norm_track(track)
    if code is None:
        raise ValueError(f"unknown track {track!r}: not recognised by vai.distances.norm()")
    return code


def store(conn: sqlite3.Connection, parsed: Parsed, *, raceday_id: str,
          race_date: str | None = None, track: str | None = None) -> int:
    """Idempotent upsert keyed by (raceday_id, race_no, start_no). Returns rows written."""
    track = normalize_track(track)
    ensure_schema(conn)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    base = getattr(parsed, "base_distance", {})
    with conn:
        for race_no, st in parsed.races.items():
            conn.execute(
                "INSERT INTO sportapp_races (raceday_id, race_no, race_date, track, start_time,"
                " base_distance, imported_at) VALUES (?,?,?,?,?,?,?) "
                "ON CONFLICT (raceday_id, race_no) DO UPDATE SET"
                " race_date=COALESCE(excluded.race_date, race_date),"
                " track=COALESCE(excluded.track, track),"
                " start_time=excluded.start_time,"
                " base_distance=COALESCE(excluded.base_distance, base_distance),"
                " imported_at=excluded.imported_at",
                (raceday_id, race_no, race_date, track, st, base.get(race_no), now),
            )
        table = "sportapp_starts" if parsed.kind == "startlist" else "sportapp_results"
        for r in parsed.rows:
            _upsert(conn, table, ("raceday_id", "race_no", "start_no"),
                    {"raceday_id": raceday_id, **r, "imported_at": now})
    return len(parsed.rows)


def import_files(paths, *, raceday_id: str, race_date=None, track=None, db=None) -> dict:
    track = normalize_track(track)  # fail before opening the DB / parsing anything
    conn = sqlite3.connect(db or db_path())
    try:
        counts = {}
        for p in paths:
            parsed = parse_file(p)
            counts[str(p)] = (parsed.kind, store(conn, parsed, raceday_id=raceday_id,
                                                 race_date=race_date, track=track))
        return counts
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m vai.sportapp_import",
        description="Import manually downloaded Sportappen start list / result .xlsx "
                    "exports into the VAI SQLite DB (private data; no API/UI exposure).")
    ap.add_argument("files", nargs="+", help="Sportappen .xlsx export(s)")
    ap.add_argument("--raceday-id", required=True, help="e.g. 616707 (ts616707)")
    ap.add_argument("--date", help="Race date YYYY-MM-DD (not present in the export)")
    ap.add_argument("--track", help="Track name or code, e.g. Solvalla; normalized via "
                    "vai.distances.norm() (stored as SOL); unknown name aborts")
    ap.add_argument("--db", help=f"SQLite path (default ${DB_PATH_ENV} or {DEFAULT_DB_PATH})")
    a = ap.parse_args(argv)
    rid = a.raceday_id.removeprefix("ts")
    if a.date:
        datetime.strptime(a.date, "%Y-%m-%d")
    try:
        track = normalize_track(a.track)
    except ValueError as e:
        print(f"error: {e}; nothing imported", file=sys.stderr)
        return 2
    for path, (kind, n) in import_files(a.files, raceday_id=rid, race_date=a.date,
                                        track=track, db=a.db).items():
        print(f"{path}: {kind}, {n} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
