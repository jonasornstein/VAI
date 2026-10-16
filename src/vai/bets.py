"""Bet tracking ("Mina spel", card T-35): SQLite storage for placed bets,
their picks, leg results, and start snapshots used for odds calibration.

Storage: one SQLite file (stdlib ``sqlite3``). Path from env ``VAI_DB_PATH``,
default ``<repo>/data/vai.sqlite``. The ``.sqlite`` extension and location under
the app dir make the weekly backup (deploy/backup/vai-backup.sh) pick it up.
The schema is created idempotently on every connect.
"""

from __future__ import annotations

import math
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

DB_PATH_ENV = "VAI_DB_PATH"

SCHEMA = """
CREATE TABLE IF NOT EXISTS bets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    game TEXT NOT NULL,
    track TEXT,
    stake_per_row REAL NOT NULL,
    rows INTEGER NOT NULL,
    price REAL NOT NULL,
    created_at TEXT NOT NULL,
    settled INTEGER NOT NULL DEFAULT 0,
    correct INTEGER,
    of_legs INTEGER NOT NULL,
    payout REAL
);
CREATE INDEX IF NOT EXISTS idx_bets_date_game ON bets(date, game);
CREATE TABLE IF NOT EXISTS bet_picks (
    bet_id INTEGER NOT NULL REFERENCES bets(id) ON DELETE CASCADE,
    leg INTEGER NOT NULL,
    start_no INTEGER NOT NULL,
    horse_name TEXT,
    streck_pct REAL,
    odds REAL,
    final_odds REAL,
    final_streck_pct REAL,
    PRIMARY KEY (bet_id, leg, start_no)
);
CREATE TABLE IF NOT EXISTS bet_legs (
    date TEXT NOT NULL,
    game TEXT NOT NULL,
    leg INTEGER NOT NULL,
    winner_start_no INTEGER,
    winner_name TEXT,
    PRIMARY KEY (date, game, leg)
);
CREATE TABLE IF NOT EXISTS start_snapshots (
    date TEXT NOT NULL,
    game TEXT NOT NULL,
    track TEXT,
    leg INTEGER NOT NULL,
    start_no INTEGER NOT NULL,
    horse_name TEXT,
    scratched INTEGER NOT NULL DEFAULT 0,
    final_odds REAL,
    streck_pct REAL,
    captured_at TEXT NOT NULL,
    PRIMARY KEY (date, game, leg, start_no)
);
"""

MAX_LEGS = 20
MAX_START_NO = 30


class BetValidationError(ValueError):
    def __init__(self, errors: list[dict[str, Any]]):
        super().__init__("invalid bet")
        self.errors = errors


def default_db_path(repo_root: Path) -> Path:
    env = os.environ.get(DB_PATH_ENV, "").strip()
    return Path(env) if env else repo_root / "data" / "vai.sqlite"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _num(v: Any, *, lo: float = 0.0, hi: float = 1e9, allow_none: bool = True) -> bool:
    if v is None:
        return allow_none
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return False
    return math.isfinite(v) and lo <= v <= hi


def _int(v: Any, lo: int, hi: int) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def compute_rows(pick_counts: Iterable[int]) -> int:
    rows = 1
    for n in pick_counts:
        rows *= n
    return rows


def _valid_date(v: Any) -> bool:
    if not isinstance(v, str):
        return False
    try:
        datetime.strptime(v, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# card_lookup(date, game) -> {leg: {"starters": set[int], "scratched": set[int]}} or None
CardLookup = Callable[[str, str], "dict[int, dict[str, set[int]]] | None"]


def validate_bet(body: dict[str, Any], card: dict[int, dict[str, set[int]]] | None = None) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    def err(reason: str, leg: Any = None, start_no: Any = None, field: str | None = None) -> None:
        e: dict[str, Any] = {"leg": leg, "startNo": start_no, "reason": reason}
        if field:
            e["field"] = field
        errors.append(e)

    if not _valid_date(body.get("date")):
        err("invalid_value", field="date")
    if not isinstance(body.get("game"), str) or not body.get("game", "").strip():
        err("invalid_value", field="game")
    if body.get("track") is not None and not isinstance(body.get("track"), str):
        err("invalid_value", field="track")
    if not _num(body.get("stakePerRow"), lo=0.01, hi=100000, allow_none=False):
        err("invalid_value", field="stakePerRow")
    legs = body.get("legs")
    if not isinstance(legs, list) or not legs or len(legs) > MAX_LEGS:
        err("invalid_value", field="legs")
        return errors
    seen_legs: set[int] = set()
    for leg_obj in legs:
        if not isinstance(leg_obj, dict) or not _int(leg_obj.get("leg"), 1, MAX_LEGS):
            err("invalid_value", field="leg")
            continue
        leg = leg_obj["leg"]
        if leg in seen_legs:
            err("duplicate", leg=leg, field="leg")
            continue
        seen_legs.add(leg)
        picks = leg_obj.get("picks")
        if not isinstance(picks, list) or not picks:
            err("empty_leg", leg=leg)
            continue
        seen: set[int] = set()
        leg_card = card.get(leg) if card is not None else None
        for p in picks:
            if not isinstance(p, dict) or not _int(p.get("startNo"), 1, MAX_START_NO):
                err("invalid_value", leg=leg, start_no=p.get("startNo") if isinstance(p, dict) else None, field="startNo")
                continue
            sn = p["startNo"]
            if sn in seen:
                err("duplicate", leg=leg, start_no=sn)
                continue
            seen.add(sn)
            if p.get("horseName") is not None and not isinstance(p.get("horseName"), str):
                err("invalid_value", leg=leg, start_no=sn, field="horseName")
            if not _num(p.get("streckPct"), lo=0, hi=100):
                err("invalid_value", leg=leg, start_no=sn, field="streckPct")
            if not _num(p.get("odds"), lo=1.0, hi=100000):
                err("invalid_value", leg=leg, start_no=sn, field="odds")
            if card is not None:
                if leg_card is None:
                    err("unknown_start", leg=leg, start_no=sn)
                elif sn in leg_card.get("scratched", set()):
                    err("scratched", leg=leg, start_no=sn)
                elif sn not in leg_card.get("starters", set()):
                    err("unknown_start", leg=leg, start_no=sn)
    return errors


class BetStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._lock = threading.Lock()
        self._initialized = False

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        if not self._initialized:
            with self._lock:
                conn.executescript(SCHEMA)
                self._initialized = True
        return conn

    # --- bets -------------------------------------------------------------
    def create_bet(self, body: dict[str, Any], card: dict[int, dict[str, set[int]]] | None = None) -> dict[str, Any]:
        errors = validate_bet(body, card)
        if errors:
            raise BetValidationError(errors)
        legs = sorted(body["legs"], key=lambda l: l["leg"])
        rows = compute_rows(len(l["picks"]) for l in legs)
        stake = float(body["stakePerRow"])
        price = round(rows * stake, 2)
        conn = self.connect()
        try:
            with conn:
                cur = conn.execute(
                    "INSERT INTO bets(date, game, track, stake_per_row, rows, price, created_at, of_legs)"
                    " VALUES (?,?,?,?,?,?,?,?)",
                    (body["date"], body["game"].strip(), body.get("track"), stake, rows, price, _now(), len(legs)),
                )
                bet_id = cur.lastrowid
                for l in legs:
                    for p in l["picks"]:
                        conn.execute(
                            "INSERT INTO bet_picks(bet_id, leg, start_no, horse_name, streck_pct, odds)"
                            " VALUES (?,?,?,?,?,?)",
                            (bet_id, l["leg"], p["startNo"], p.get("horseName"), p.get("streckPct"), p.get("odds")),
                        )
            return self._load(conn, [bet_id])[0]
        finally:
            conn.close()

    def list_bets(self, date: str | None = None) -> list[dict[str, Any]]:
        conn = self.connect()
        try:
            if date:
                ids = [r[0] for r in conn.execute("SELECT id FROM bets WHERE date=? ORDER BY id", (date,))]
            else:
                ids = [r[0] for r in conn.execute("SELECT id FROM bets ORDER BY date DESC, id DESC")]
            return self._load(conn, ids)
        finally:
            conn.close()

    def _load(self, conn: sqlite3.Connection, ids: list[int]) -> list[dict[str, Any]]:
        out = []
        for bet_id in ids:
            b = conn.execute("SELECT * FROM bets WHERE id=?", (bet_id,)).fetchone()
            if b is None:
                continue
            winners = {
                r["leg"]: r
                for r in conn.execute("SELECT * FROM bet_legs WHERE date=? AND game=?", (b["date"], b["game"]))
            }
            picks_by_leg: dict[int, list[dict[str, Any]]] = {}
            for p in conn.execute("SELECT * FROM bet_picks WHERE bet_id=? ORDER BY leg, start_no", (bet_id,)):
                picks_by_leg.setdefault(p["leg"], []).append(
                    {
                        "startNo": p["start_no"],
                        "horseName": p["horse_name"],
                        "streckPct": p["streck_pct"],
                        "odds": p["odds"],
                        "finalOdds": p["final_odds"],
                        "finalStreckPct": p["final_streck_pct"],
                    }
                )
            legs = []
            for leg in sorted(picks_by_leg):
                w = winners.get(leg)
                winner = w["winner_start_no"] if w else None
                legs.append(
                    {
                        "leg": leg,
                        "winner": winner,
                        "winnerName": w["winner_name"] if w else None,
                        "hit": None if winner is None else any(p["startNo"] == winner for p in picks_by_leg[leg]),
                        "picks": picks_by_leg[leg],
                    }
                )
            out.append(
                {
                    "id": b["id"],
                    "date": b["date"],
                    "game": b["game"],
                    "track": b["track"],
                    "rows": b["rows"],
                    "stakePerRow": b["stake_per_row"],
                    "price": b["price"],
                    "createdAt": b["created_at"],
                    "legs": legs,
                    "result": {
                        "correct": b["correct"],
                        "of": b["of_legs"],
                        "payout": b["payout"],
                        "settled": bool(b["settled"]),
                    },
                }
            )
        return out

    # --- settle -----------------------------------------------------------
    def settle(self, body: dict[str, Any]) -> dict[str, Any]:
        errors: list[dict[str, Any]] = []
        if not _valid_date(body.get("date")):
            errors.append({"leg": None, "startNo": None, "reason": "invalid_value", "field": "date"})
        if not isinstance(body.get("game"), str) or not body["game"].strip():
            errors.append({"leg": None, "startNo": None, "reason": "invalid_value", "field": "game"})
        legs = body.get("legs")
        if not isinstance(legs, list) or not legs:
            errors.append({"leg": None, "startNo": None, "reason": "invalid_value", "field": "legs"})
            legs = []
        for l in legs:
            if not isinstance(l, dict) or not _int(l.get("leg"), 1, MAX_LEGS) or not _int(l.get("winner"), 1, MAX_START_NO):
                errors.append({"leg": l.get("leg") if isinstance(l, dict) else None, "startNo": None,
                               "reason": "invalid_value", "field": "winner"})
        payouts_raw = body.get("payouts")
        payouts: dict[int, float] = {}
        if payouts_raw is not None:
            if not isinstance(payouts_raw, dict):
                errors.append({"leg": None, "startNo": None, "reason": "invalid_value", "field": "payouts"})
            else:
                for k, v in payouts_raw.items():
                    try:
                        kk = int(k)
                    except (TypeError, ValueError):
                        kk = -1
                    if kk < 0 or not _num(v, lo=0, hi=1e12, allow_none=False):
                        errors.append({"leg": None, "startNo": None, "reason": "invalid_value", "field": "payouts"})
                    else:
                        payouts[kk] = float(v)
        if errors:
            raise BetValidationError(errors)
        date, game = body["date"], body["game"].strip()
        conn = self.connect()
        try:
            with conn:
                for l in legs:
                    conn.execute(
                        "INSERT INTO bet_legs(date, game, leg, winner_start_no, winner_name) VALUES (?,?,?,?,?)"
                        " ON CONFLICT(date, game, leg) DO UPDATE SET winner_start_no=excluded.winner_start_no,"
                        " winner_name=excluded.winner_name",
                        (date, game, l["leg"], l["winner"], l.get("winnerName")),
                    )
                winners = {
                    r["leg"]: r["winner_start_no"]
                    for r in conn.execute("SELECT leg, winner_start_no FROM bet_legs WHERE date=? AND game=?", (date, game))
                }
                bet_ids = [r[0] for r in conn.execute("SELECT id FROM bets WHERE date=? AND game=?", (date, game))]
                for bet_id in bet_ids:
                    self._settle_one(conn, bet_id, date, game, winners, payouts)
            return {"settled": len(bet_ids), "bets": self._load(conn, bet_ids)}
        finally:
            conn.close()

    @staticmethod
    def _settle_one(conn, bet_id, date, game, winners, payouts) -> None:
        b = conn.execute("SELECT * FROM bets WHERE id=?", (bet_id,)).fetchone()
        picks: dict[int, set[int]] = {}
        for p in conn.execute("SELECT leg, start_no FROM bet_picks WHERE bet_id=?", (bet_id,)):
            picks.setdefault(p["leg"], set()).add(p["start_no"])
        # Final odds / streck from snapshots.
        conn.execute(
            "UPDATE bet_picks SET"
            " final_odds=(SELECT s.final_odds FROM start_snapshots s WHERE s.date=? AND s.game=?"
            "   AND s.leg=bet_picks.leg AND s.start_no=bet_picks.start_no),"
            " final_streck_pct=(SELECT s.streck_pct FROM start_snapshots s WHERE s.date=? AND s.game=?"
            "   AND s.leg=bet_picks.leg AND s.start_no=bet_picks.start_no)"
            " WHERE bet_id=?",
            (date, game, date, game, bet_id),
        )
        all_known = all(leg in winners for leg in picks)
        correct = sum(1 for leg, s in picks.items() if winners.get(leg) in s)
        payout = None
        if all_known:
            # Winning rows at the top level: only a row with every leg right counts as "of" correct.
            # rows hitting N legs = product over legs of (1 if hit else 0) for full hits;
            # for lower tiers: count rows with exactly k hits.
            tiers = _rows_by_correct(picks, winners)
            if payouts:
                payout = round(sum(tiers.get(k, 0) * amt for k, amt in payouts.items()), 2)
        conn.execute(
            "UPDATE bets SET correct=?, settled=?, payout=? WHERE id=?",
            (correct, 1 if all_known else 0, payout, bet_id),
        )


def _rows_by_correct(picks: dict[int, set[int]], winners: dict[int, int]) -> dict[int, int]:
    """Number of system rows with exactly k correct legs (polynomial expansion)."""
    dist = {0: 1}
    for leg, s in picks.items():
        hit = 1 if winners.get(leg) in s else 0
        miss = len(s) - hit
        nd: dict[int, int] = {}
        for k, n in dist.items():
            if hit:
                nd[k + 1] = nd.get(k + 1, 0) + n * hit
            if miss:
                nd[k] = nd.get(k, 0) + n * miss
        dist = nd
    return dist


# --- snapshots --------------------------------------------------------------
def record_snapshots(store: BetStore, body: dict[str, Any]) -> int:
    errors: list[dict[str, Any]] = []
    if not _valid_date(body.get("date")):
        errors.append({"leg": None, "startNo": None, "reason": "invalid_value", "field": "date"})
    if not isinstance(body.get("game"), str) or not body.get("game", "").strip():
        errors.append({"leg": None, "startNo": None, "reason": "invalid_value", "field": "game"})
    starts = body.get("starts")
    if not isinstance(starts, list) or not starts:
        errors.append({"leg": None, "startNo": None, "reason": "invalid_value", "field": "starts"})
        starts = []
    for s in starts:
        ok = (
            isinstance(s, dict)
            and _int(s.get("leg"), 1, MAX_LEGS)
            and _int(s.get("startNo"), 1, MAX_START_NO)
            and _num(s.get("finalOdds"), lo=1.0, hi=100000)
            and _num(s.get("streckPct"), lo=0, hi=100)
            and (s.get("horseName") is None or isinstance(s.get("horseName"), str))
            and (s.get("scratched") is None or isinstance(s.get("scratched"), bool))
        )
        if not ok:
            errors.append({"leg": s.get("leg") if isinstance(s, dict) else None,
                           "startNo": s.get("startNo") if isinstance(s, dict) else None,
                           "reason": "invalid_value"})
    if errors:
        raise BetValidationError(errors)
    now = _now()
    conn = store.connect()
    try:
        with conn:
            for s in starts:
                conn.execute(
                    "INSERT INTO start_snapshots(date, game, track, leg, start_no, horse_name, scratched,"
                    " final_odds, streck_pct, captured_at) VALUES (?,?,?,?,?,?,?,?,?,?)"
                    " ON CONFLICT(date, game, leg, start_no) DO UPDATE SET track=excluded.track,"
                    " horse_name=excluded.horse_name, scratched=excluded.scratched,"
                    " final_odds=excluded.final_odds, streck_pct=excluded.streck_pct,"
                    " captured_at=excluded.captured_at",
                    (body["date"], body["game"].strip(), body.get("track"), s["leg"], s["startNo"],
                     s.get("horseName"), 1 if s.get("scratched") else 0, s.get("finalOdds"),
                     s.get("streckPct"), now),
                )
        return len(starts)
    finally:
        conn.close()


def snapshot_card(store: BetStore, date: str, game: str) -> dict[int, dict[str, set[int]]] | None:
    """Starters/scratches per leg from recorded snapshots, or None if none recorded."""
    conn = store.connect()
    try:
        rows = conn.execute(
            "SELECT leg, start_no, scratched FROM start_snapshots WHERE date=? AND game=?", (date, game)
        ).fetchall()
    finally:
        conn.close()
    if not rows:
        return None
    card: dict[int, dict[str, set[int]]] = {}
    for r in rows:
        c = card.setdefault(r["leg"], {"starters": set(), "scratched": set()})
        c["starters"].add(r["start_no"])
        if r["scratched"]:
            c["scratched"].add(r["start_no"])
    return card
