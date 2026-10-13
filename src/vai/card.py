"""FUNDAMENTAL race card (V85/V75…): port of v85-deploy seed_live.py into vai.

Fetched on demand only (no background refresh). Opening odds are persisted the
first time a plausible odds value is seen per start, under inbox/card-odds/<game>.json.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from vai.atg_fetch import ATG_GAME_URL_TEMPLATE, AtgFetchError, fetch_game_shared, fetch_horse_results, fetch_json
from vai.track_distance import km_between

CARD_GAME_ID_RE = re.compile(r"^V\d{2}_\d{4}-\d{2}-\d{2}_\d+_\d+$")
ODDS_CAP_RAW = 9999  # ATG placeholder (99.99) shown before a real win pool exists
ODDS_MIN_RAW = 100  # 1.00 — thin-pool artefact, never used as opening odds
_RECORDS_CACHE: dict[int, list[dict[str, Any]]] = {}
_RECORDS_KEY: dict[int, Any] = {}  # horse id -> life starts the cached records belong to
_CACHE_LOCK = threading.Lock()
_OPEN_LOCK = threading.Lock()
_WORKERS = 6  # polite to ATG: at most 6 concurrent horse-results calls
_FORM_KEEP = 5

SORTABLE_COLUMNS: list[dict[str, str]] = [
    {"key": "startNumber", "label": "#", "tip": "Startnummer."},
    {"key": "horseName", "label": "Häst/Kusk/Tränare", "tip": "Häst, K: kusk, T: tränare."},
    {"key": "odds", "label": "Odds", "tip": "Aktuella vinnarodds (live)."},
    {"key": "bookingPct", "label": "Streck %", "tip": "Andel av kupongerna som streckat hästen."},
    {"key": "formLast5", "label": "Form", "tip": "Fem senaste placeringar, senaste först. x = galopp, d = disk."},
    {"key": "prefDistance", "label": "Pref m", "tip": "Distans där hästen oftast varit topp 3 (senaste 5)."},
    {"key": "gallops", "label": "Galopp", "tip": "Galopper i de fem senaste starterna."},
    {"key": "dqs", "label": "Disk", "tip": "Diskvalifikationer i de fem senaste starterna."},
    {"key": "homeCombo", "label": "km / Hemmabana", "tip": "Uppskattad väg-km och hemmabana för häst, kusk, tränare (ej ST avståndstabell)."},
    {"key": "oddsOpen", "label": "Öppning", "tip": "Första odds VAI såg för spelet (sparas vid första hämtning)."},
    {"key": "oddsDelta", "label": "Δ", "tip": "Förändring öppning→nu; negativt = kortare odds (mer spel)."},
    {"key": "impliedWinPct", "label": "Impl %", "tip": "100 ÷ odds."},
    {"key": "hotMoney", "label": "Het", "tip": "Hög streck % utan stöd i senaste 3 starterna."},
    {"key": "coldMoney", "label": "Kall", "tip": "Låg streck % trots starka senaste 3 starterna."},
    {"key": "post", "label": "Spår", "tip": "Spår / startposition."},
    {"key": "shoes", "label": "Skor", "tip": "Skoning idag."},
    {"key": "driverChange", "label": "Kuskbyte", "tip": "Annan kusk än i senaste start."},
]


def is_card_game_id(game_id: str) -> bool:
    return bool(CARD_GAME_ID_RE.match(game_id or ""))


def default_odds_dir(repo_root: Path) -> Path:
    return repo_root / "inbox" / "card-odds"


def load_open_odds(path: Path) -> dict[str, float]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return {str(k): float(v) for k, v in data.items() if isinstance(v, (int, float))} if isinstance(data, dict) else {}


def save_open_odds_atomic(path: Path, data: dict[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def default_form_dir(odds_dir: Path) -> Path:
    """inbox/card-form next to inbox/card-odds."""
    return odds_dir.parent / "card-form"


def _life_starts(horse: Any) -> int | None:
    """ATG career start count from the game payload; changes exactly when the horse has raced."""
    v = (((horse or {}).get("statistics") or {}).get("life") or {}).get("starts") if isinstance(horse, dict) else None
    return v if isinstance(v, int) else None


def _form_path(form_dir: Path, horse_id: int) -> Path:
    return form_dir / f"{horse_id}.json"


def _load_form_disk(form_dir: Path | None, horse_id: int, starts: int | None) -> list[dict[str, Any]] | None:
    if form_dir is None or starts is None:
        return None
    try:
        d = json.loads(_form_path(form_dir, horse_id).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(d, dict) or d.get("lifeStarts") != starts or not isinstance(d.get("records"), list):
        return None
    return [r for r in d["records"] if isinstance(r, dict)]


def _save_form_disk(form_dir: Path | None, horse_id: int, starts: int | None, recs: list[dict[str, Any]]) -> None:
    if form_dir is None or starts is None:
        return
    path = _form_path(form_dir, horse_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({"horseId": horse_id, "lifeStarts": starts, "lastStart": (recs[0].get("date") if recs else None),
                       "records": recs}, fh, ensure_ascii=False)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except (OSError, UnboundLocalError):
            pass


def _cached_records(horse_id: int, starts: int | None, form_dir: Path | None) -> list[dict[str, Any]] | None:
    """Memory, then disk. A known start count that differs from the cached one invalidates."""
    with _CACHE_LOCK:
        if horse_id in _RECORDS_CACHE and (starts is None or _RECORDS_KEY.get(horse_id) == starts):
            return _RECORDS_CACHE[horse_id]
    recs = _load_form_disk(form_dir, horse_id, starts)
    if recs is not None:
        with _CACHE_LOCK:
            _RECORDS_CACHE[horse_id] = recs
            _RECORDS_KEY[horse_id] = starts
    return recs


def _records_for(horse_id: int, starts: int | None = None, form_dir: Path | None = None) -> list[dict[str, Any]]:
    recs = _cached_records(horse_id, starts, form_dir)
    if recs is not None:
        return recs
    try:
        recs = fetch_horse_results(horse_id).get("records")
    except AtgFetchError:
        return []  # not cached → retried on next explicit fetch
    recs = [r for r in recs if isinstance(r, dict)][:_FORM_KEEP] if isinstance(recs, list) else []
    with _CACHE_LOCK:
        _RECORDS_CACHE[horse_id] = recs
        _RECORDS_KEY[horse_id] = starts
    _save_form_disk(form_dir, horse_id, starts, recs)
    return recs


def clear_records_cache() -> None:
    with _CACHE_LOCK:
        _RECORDS_CACHE.clear()
        _RECORDS_KEY.clear()


def _shoes(sh: Any) -> str | None:
    if not isinstance(sh, dict):
        return None
    f = (sh.get("front") or {}).get("hasShoe")
    b = (sh.get("back") or {}).get("hasShoe")
    if f is None and b is None:
        return None
    return {(True, True): "sko", (False, False): "barfota", (False, True): "barfota_fram", (True, False): "barfota_bak"}[
        (bool(f), bool(b))
    ]


def _ladder(txt: Any) -> list[dict[str, int]]:
    m = re.search(r"Pris:\s*([\d\.\-\s]+)kr", txt or "")
    if not m:
        return []
    return [{"place": i + 1, "amount": int(x.replace(".", ""))} for i, x in enumerate(re.findall(r"[\d\.]+", m.group(1)))]


def _place_token(x: dict[str, Any]) -> str:
    if x.get("disqualified"):
        return "d"
    if x.get("galloped"):
        return "x"
    p = str(x.get("place", "0"))
    return p if p not in ("", "None") else "0"


def _name(p: Any) -> str | None:
    if not isinstance(p, dict):
        return None
    return f"{p.get('firstName') or ''} {p.get('lastName') or ''}".strip() or None


def _home(p: Any) -> str | None:
    ht = p.get("homeTrack") if isinstance(p, dict) else None
    return ht.get("name") if isinstance(ht, dict) else None


def _odds(raw: Any) -> float | None:
    if not isinstance(raw, (int, float)) or raw <= 0:
        return None
    return round(raw / 100, 2)


STRECK_OVER = 1.3
STRECK_UNDER = 0.7
STRECK_MIN_PCT = 3.0
_STRECK_EPS = 1e-9


def add_streck_flags(card: dict[str, Any]) -> dict[str, Any]:
    """Port of v85-card-api addStreckFlags: streck % vs odds-implied (normalized) win chance.

    Per leg, win% = (1/odds) / sum(1/odds of live starters) * 100. Sets winChancePct,
    streckRatio (bookingPct / win, 2 dp) and streckFlag ('over' >= 1.3, 'under' <= 0.7).
    Thresholds compare the ROUNDED streckRatio (2 dp) so the arrow always matches the
    shown number (1.296 -> 1.30 -> over), with a 1e-9 tolerance against float error. No flag when both streck % and win% are below 3.
    """
    for leg in card.get("legs") or []:
        starters = leg.get("starters") or []

        def _live_odds(s: dict[str, Any]) -> float | None:
            o = s.get("odds")
            if s.get("scratched") or not isinstance(o, (int, float)) or o <= 0:
                return None
            return float(o)

        total = sum(1 / o for o in (_live_odds(s) for s in starters) if o is not None)
        for s in starters:
            s["streckRatio"] = None
            s["streckFlag"] = None
            s["winChancePct"] = None
            o = _live_odds(s)
            book = s.get("bookingPct")
            if o is None or not isinstance(book, (int, float)) or not total:
                continue
            win = (1 / o) / total * 100
            s["winChancePct"] = round(win, 1)
            if win <= 0:
                continue
            r = book / win
            rr = round(r, 2)
            s["streckRatio"] = rr
            if book < STRECK_MIN_PCT and win < STRECK_MIN_PCT:
                continue
            if rr >= STRECK_OVER - _STRECK_EPS:
                s["streckFlag"] = "over"
            elif rr <= STRECK_UNDER + _STRECK_EPS:
                s["streckFlag"] = "under"
    return card


def build_card(
    game_id: str,
    *,
    odds_dir: Path,
    include_form: bool | str = True,
    fetch_game: Callable[[str], dict[str, Any]] | None = None,
    form_dir: Path | None = None,
) -> dict[str, Any]:
    """include_form: True = fetch missing form from ATG; "cached" = memory/disk only
    (reports formMissing so the UI can ask again with form); False = no form."""
    if not is_card_game_id(game_id):
        raise ValueError(f"Invalid game id: {game_id}")
    if fetch_game is not None:
        g = fetch_game(game_id)
    else:
        g = fetch_game_shared(game_id, lambda: fetch_json(ATG_GAME_URL_TEMPLATE.format(game_id=game_id)))
    races = g.get("races")
    if not isinstance(races, list) or not races:
        raise ValueError("ATG game has no races")
    product = g.get("type") or game_id.split("_", 1)[0]

    if form_dir is None:
        form_dir = default_form_dir(odds_dir)
    want: dict[int, int | None] = {}
    for r in races:
        for s in r.get("starts") or []:
            h = s.get("horse")
            if isinstance(h, dict) and isinstance(h.get("id"), int):
                want[h["id"]] = _life_starts(h)
    form_missing = 0
    if include_form == "cached":
        form_missing = sum(1 for hid, st in want.items() if _cached_records(hid, st, form_dir) is None)
    elif include_form:
        todo = [hid for hid, st in want.items() if _cached_records(hid, st, form_dir) is None]
        if todo:
            with ThreadPoolExecutor(max_workers=min(_WORKERS, len(todo))) as pool:
                list(pool.map(lambda hid: _records_for(hid, want[hid], form_dir), todo))

    open_path = odds_dir / f"{game_id}.json"
    with _OPEN_LOCK:
        opens = load_open_odds(open_path)
        n_before = len(opens)
        legs = []
        for i, r in enumerate(races, 1):
            track = r.get("track") or {}
            track_name = track.get("name")
            starters = []
            for s in r.get("starts") or []:
                n = s.get("number")
                if not isinstance(n, int):
                    continue
                h = s.get("horse") or {}
                drv = s.get("driver") or {}
                tr = h.get("trainer") or {}
                key = f"{r.get('id')}_{n}"
                hid = h.get("id")
                with _CACHE_LOCK:
                    ok = isinstance(hid, int) and (want.get(hid) is None or _RECORDS_KEY.get(hid) == want.get(hid))
                    rec = list(_RECORDS_CACHE.get(hid, []))[:_FORM_KEEP] if ok else []
                p = s.get("pools") or {}
                oraw = (p.get("vinnare") or {}).get("odds")
                odds = _odds(oraw)
                scratched = bool(s.get("scratched"))
                if scratched:
                    odds = None
                mp = p.get(product) or {}
                bd = mp.get("betDistribution")
                book = round(bd / 100, 2) if isinstance(bd, (int, float)) else None
                # Opening odds: first plausible value (skip ATG placeholder 99.99 / 0).
                if odds is not None and ODDS_MIN_RAW < oraw < ODDS_CAP_RAW and key not in opens:
                    opens[key] = odds
                op = opens.get(key)
                last3 = [int(x["place"]) for x in rec[:3] if str(x.get("place", "")).isdigit() and int(x["place"]) > 0]
                avg3 = sum(last3) / len(last3) if last3 else 9
                dists = [(x.get("start") or {}).get("distance") for x in rec if str(x.get("place")) in ("1", "2", "3")]
                lastdrv = ((rec[0].get("start") or {}).get("driver") or {}).get("id") if rec else None
                hh, dh, th = _home(h), _home(drv), _home(tr)
                starters.append(
                    {
                        "startNumber": n,
                        "horseId": hid,
                        "horseName": h.get("name"),
                        "scratched": scratched,
                        "odds": odds,
                        "oddsOpen": op,
                        "oddsDelta": round(odds - op, 2) if odds and op else None,
                        "bookingPct": None if scratched else book,
                        "impliedWinPct": round(100 / odds, 1) if odds else None,
                        "streckTrend": mp.get("trend"),
                        "hotMoney": bool(not scratched and book and book >= 15 and avg3 > 3),
                        "coldMoney": bool(not scratched and book is not None and book < 5 and avg3 <= 2 and last3),
                        "driver": _name(drv),
                        "trainer": _name(tr),
                        "horseHemmabana": hh,
                        "driverHemmabana": dh,
                        "trainerHemmabana": th,
                        "horseKm": km_between(hh, track_name),
                        "driverKm": km_between(dh, track_name),
                        "trainerKm": km_between(th, track_name),
                        "formLast5": "-".join(_place_token(x) for x in rec) or None,
                        "post": s.get("postPosition"),
                        "startDistance": s.get("distance"),
                        "shoes": _shoes(h.get("shoes")),
                        "driverChange": bool(lastdrv and lastdrv != drv.get("id")),
                        "prefDistance": Counter(dists).most_common(1)[0][0] if dists else None,
                        "gallops": sum(1 for x in rec if x.get("galloped")) if rec else None,
                        "dqs": sum(1 for x in rec if x.get("disqualified")) if rec else None,
                    }
                )
            lad = _ladder(r.get("prize"))
            legs.append(
                {
                    "leg": i,
                    "raceNumber": r.get("number"),
                    "raceId": r.get("id"),
                    "trackName": track_name,
                    "postTime": (r.get("startTime") or r.get("scheduledStartTime") or "")[11:16] or None,
                    "distance": r.get("distance"),
                    "startMethod": r.get("startMethod"),
                    "raceName": r.get("name"),
                    "trackCondition": track.get("condition"),
                    "starterCount": len(starters),
                    "prizeMoney": sum(x["amount"] for x in lad) or None,
                    "prizeMoneyLadder": lad,
                    "prizeText": r.get("prize"),
                    "status": r.get("status"),
                    "starters": starters,
                }
            )
        if len(opens) != n_before:
            save_open_odds_atomic(open_path, opens)

    pool = (g.get("pools") or {}).get(product) or {}
    turnover = pool.get("turnover")
    return add_streck_flags({
        "id": game_id,
        "gameId": game_id,
        "product": product,
        "status": g.get("status"),
        "legCount": len(legs),
        "meetingDate": str(legs[0].get("raceId") or "")[:10] or None,
        "trackName": legs[0].get("trackName"),
        "turnover": round(turnover / 100) if isinstance(turnover, (int, float)) else None,
        "turnoverCurrency": "SEK",
        "systemCount": pool.get("systemCount"),
        "source": "atg",
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "atgTimestamp": pool.get("timestamp"),
        "includeForm": include_form,
        "formMissing": form_missing,
        "openOddsSaved": len(opens),
        "kmNote": "ESTIMATE driving km (haversine × 1.35, round 10). Not ST avståndstabell.",
        "sortableColumns": SORTABLE_COLUMNS,
        "legs": legs,
    })
