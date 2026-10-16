"""Tests for vai.sportapp_import using SYNTHETIC fixtures only.

The real Sportappen exports are copyrighted and must never be committed; the
xlsx files below are generated at test time with invented horses/people but
the same column layout (positions) as the real exports.
"""
from __future__ import annotations

import ast
import sqlite3
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import pytest

from vai import sportapp_import as sa

NBSP = "\u00a0"

START_ROWS = [
    ["", "Häst", "Kön", "Ålder", "Kusk/Ryttare", "Spår/Dist.", "Startsumma", "Tränare", "Ägare", "Skor", "Vagn"],
    ["Lopp 1. Starttid 13:05", "", None, "", None, "", "", "", None, None, None],
    ["", "1  ALFA TESTSSON", "v", "3", "Kusk Anna", "1/2140", f"99{NBSP}000", "Tränare Bo", "Stall Test AB", "Barfota bak", "S"],
    ["", "2  BETA PROV* (NO)", "h", "4", "Kusk Carl", "2/2140", f"1{NBSP}607{NBSP}232", "Tränare Bo", "Ägare X, Norge", "Skor runt om", ("A", "red")],
    [("", None), ("3  GAMMA STRUKEN", "strike"), "s", "5", "Kusk Dora", "3/2140", "0", "Tränare Eva", "Ägare Y", "Barfota fram", "S"],
    ["Lopp 2. Starttid 13:27", "", None, "", None, "", "", "", None, None, None],
    ["", "1  DELTA VOLT", "v", "6", "Kusk Anna", "1/3140", f"500{NBSP}000", "Tränare Eva", "Ägare Z", "Skor runt om", "S"],
    ["", "2  EPSILON TILLÄGG", "h", "7", "Kusk Carl", "2/3160", f"800{NBSP}000", "Tränare Bo", "Ägare Z", "Barfota runt om", "A"],
]

RESULT_ROWS = [
    ["", "Plac.", "Häst", "Kusk/Ryttare", "Tränare", "Spår/Dist.", "Tid", "Skor", "Vagn", "Odds", "Plats"],
    ["Lopp 1. Starttid 13:05:00", "", "", None, None, "", "", None, None, "", ""],
    ["", "1", "2  BETA PROV* (NO)", "Kusk Carl", "Tränare Bo", "2/2140", "12,3a", "Skor runt om", "A", "", ""],
    ["", "d", "1  ALFA TESTSSON", "Kusk Anna", "Tränare Bo", "1/2140", "11ag", "Barfota bak", "S", "", ""],
    ["", "", "3 GAMMA STRUKEN  (hälta, startförbud 261010-261020)", None, None, "", "", None, None, "", ""],
    ["Lopp 2. Starttid 13:27:00", "", "", None, None, "", "", None, None, "", ""],
    ["", "1", "2  EPSILON TILLÄGG", "Kusk Carl", "Tränare Bo", "2/3160", "14,5", "Barfota runt om", "A", "5,40", "1,60"],
    ["", "0", "1  DELTA VOLT", "Kusk Anna", "Tränare Eva", "1/3140", "uag", "Skor runt om", "S", "", ""],
]

STYLES = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    '<fonts count="3"><font><sz val="11"/></font><font><color rgb="FFFF0000"/></font><font><strike/></font></fonts>'
    '<cellXfs count="3"><xf fontId="0"/><xf fontId="1" applyFont="1"/><xf fontId="2" applyFont="1"/></cellXfs>'
    "</styleSheet>"
)


def write_xlsx(path: Path, rows) -> Path:
    strings: list[str] = []
    sheet_rows = []
    for ri, row in enumerate(rows, 1):
        cells = []
        for ci, val in enumerate(row):
            style = None
            if isinstance(val, tuple):
                val, style = val
            if val is None:
                continue
            if val not in strings:
                strings.append(val)
            s = {"red": ' s="1"', "strike": ' s="2"'}.get(style, "")
            cells.append(f'<c r="{chr(65 + ci)}{ri}" t="s"{s}><v>{strings.index(val)}</v></c>')
        sheet_rows.append(f'<row r="{ri}">{"".join(cells)}</row>')
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/worksheets/sheet1.xml",
                   f'<?xml version="1.0"?><worksheet {ns}><sheetData>{"".join(sheet_rows)}</sheetData></worksheet>')
        z.writestr("xl/sharedStrings.xml",
                   f'<?xml version="1.0"?><sst {ns}>' + "".join(f"<si><t>{escape(s)}</t></si>" for s in strings) + "</sst>")
        z.writestr("xl/styles.xml", STYLES)
    return path


@pytest.fixture
def files(tmp_path):
    return (write_xlsx(tmp_path / "startlista.xlsx", START_ROWS),
            write_xlsx(tmp_path / "resultat.xlsx", RESULT_ROWS))


def test_parse_startlist(files):
    p = sa.parse_file(files[0])
    assert p.kind == "startlist"
    assert p.races == {1: "13:05", 2: "13:27"}
    r = {(x["race_no"], x["start_no"]): x for x in p.rows}
    assert len(r) == 5
    a = r[(1, 1)]
    assert (a["horse"], a["sex"], a["age"], a["post"], a["distance"]) == ("ALFA TESTSSON", "v", 3, 1, 2140)
    assert a["start_sum_kr"] == 99000 and a["owner"] == "Stall Test AB"
    assert r[(1, 2)]["start_sum_kr"] == 1607232 and r[(1, 2)]["sulky_flagged"] == 1
    assert r[(1, 3)]["scratched"] == 1 and a["scratched"] == 0
    assert r[(2, 2)]["handicap_m"] == 20 and r[(2, 1)]["handicap_m"] == 0


def test_parse_results(files):
    p = sa.parse_file(files[1])
    assert p.kind == "results"
    r = {(x["race_no"], x["start_no"]): x for x in p.rows}
    w = r[(1, 2)]
    assert (w["place"], w["km_time_s"], w["auto_start"], w["gallop"]) == (1, 72.3, 1, 0)
    d = r[(1, 1)]
    assert d["disqualified"] == 1 and d["place"] is None and d["gallop"] == 1 and d["km_time_s"] == 71.0
    s = r[(1, 3)]
    assert s["scratched"] == 1 and s["horse"] == "GAMMA STRUKEN" and s["scratch_reason"].startswith("hälta")
    v = r[(2, 2)]
    assert v["auto_start"] == 0 and v["km_time_s"] == 74.5 and v["odds"] == 5.4 and v["handicap_m"] == 20
    u = r[(2, 1)]
    assert u["place_raw"] == "0" and u["place"] is None and u["km_time_s"] is None and u["gallop"] == 1


def test_columns_by_position_not_header(tmp_path):
    rows = [list(r) for r in START_ROWS]
    rows[0] = ["", "Häst", "Bana", "Bana", "x", "y", "z", "q", "w", "e", "r"]
    p = sa.parse_file(write_xlsx(tmp_path / "s.xlsx", rows))
    assert p.rows[0]["sex"] == "v" and p.rows[0]["age"] == 3


def test_unknown_layout(tmp_path):
    with pytest.raises(ValueError):
        sa.parse_file(write_xlsx(tmp_path / "x.xlsx", [["", "Foo"]]))


def test_cli_import_idempotent(files, tmp_path, monkeypatch, capsys):
    db = tmp_path / "vai.sqlite"
    monkeypatch.setenv("VAI_DB_PATH", str(db))
    args = ["--raceday-id", "ts616707", "--date", "2026-10-10", "--track", "Testbana", *map(str, files)]
    assert sa.main(args) == 0
    assert sa.main(args) == 0  # re-import must not duplicate
    assert "startlist, 5 rows" in capsys.readouterr().out
    c = sqlite3.connect(db)
    assert c.execute("select count(*) from sportapp_races").fetchone()[0] == 2
    assert c.execute("select count(*) from sportapp_starts").fetchone()[0] == 5
    assert c.execute("select count(*) from sportapp_results").fetchone()[0] == 5
    assert c.execute("select raceday_id, race_date, track, base_distance from sportapp_races where race_no=2"
                     ).fetchone() == ("616707", "2026-10-10", "Testbana", 3140)


def test_reimport_updates_row(files, tmp_path):
    db = tmp_path / "v.sqlite"
    sa.import_files([files[1]], raceday_id="1", db=str(db))
    rows = [list(r) for r in RESULT_ROWS]
    rows[2][6] = "12,9a"
    f2 = write_xlsx(tmp_path / "r2.xlsx", rows)
    sa.import_files([f2], raceday_id="1", db=str(db))
    c = sqlite3.connect(db)
    assert c.execute("select km_time_raw from sportapp_results where race_no=1 and start_no=2").fetchone()[0] == "12,9a"
    assert c.execute("select count(*) from sportapp_results").fetchone()[0] == 5


def test_default_db_path(monkeypatch):
    monkeypatch.delenv("VAI_DB_PATH", raising=False)
    assert sa.db_path() == "/opt/vai/data/vai.sqlite"


NETWORK_MODULES = {"socket", "ssl", "http", "urllib", "urllib3", "requests", "httpx",
                   "aiohttp", "ftplib", "smtplib", "telnetlib", "xmlrpc", "websocket",
                   "websockets", "sched", "asyncio", "subprocess", "vai.atg_fetch", "vai.atg_race_card"}


def test_module_imports_no_network_modules():
    src = Path(sa.__file__).read_text(encoding="utf-8")
    found = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            found |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    bad = {m for m in found if m in NETWORK_MODULES or m.split(".")[0] in NETWORK_MODULES}
    assert not bad, bad


def test_not_exposed_via_server():
    server_src = Path(sa.__file__).with_name("server.py").read_text(encoding="utf-8")
    assert "sportapp" not in server_src.lower()
