"""Fundamental-mode start-info: per-horse form, kusk, km (FUNDAMENTAL läge)."""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any

from vai.atg_fetch import AtgFetchError, fetch_horse_results, fetch_v85_game
from vai.atg_race_card import extract_leg_distributions, extract_leg_odds, parse_atg_game
from vai.models.race_card import Leg, RaceCard
from vai.track_distance import km_between

_LAST5_CACHE: dict[int, str] = {}
_CACHE_LOCK = threading.Lock()
_FORM_WORKERS = 8


def form_token(record: dict[str, Any]) -> str:
    """Compact one start: d = diskad, 1–15 = placing, o = osk!."""
    if record.get("disqualified") is True:
        return "d"
    place = record.get("place")
    if isinstance(place, str) and place.isdigit():
        number = int(place)
        if 1 <= number <= 15:
            return str(number)
    if isinstance(place, int) and 1 <= place <= 15:
        return str(place)
    return "o"


def compact_last5(records: list[Any] | None) -> str:
    tokens: list[str] = []
    if not records:
        return ""
    for rec in records[:5]:
        if isinstance(rec, dict):
            tokens.append(form_token(rec))
    return "-".join(tokens)


def _person_name(person: Any) -> str | None:
    if not isinstance(person, dict):
        return None
    name = f"{person.get('firstName') or ''} {person.get('lastName') or ''}".strip()
    return name or None


def _home_track(obj: Any) -> str | None:
    if not isinstance(obj, dict):
        return None
    ht = obj.get("homeTrack")
    if isinstance(ht, dict) and isinstance(ht.get("name"), str) and ht["name"].strip():
        return ht["name"].strip()
    return None


def last5_from_cache(horse_id: int) -> str | None:
    with _CACHE_LOCK:
        return _LAST5_CACHE.get(horse_id)


def store_last5(horse_id: int, last5: str) -> None:
    with _CACHE_LOCK:
        _LAST5_CACHE[horse_id] = last5


def clear_last5_cache() -> None:
    with _CACHE_LOCK:
        _LAST5_CACHE.clear()


def fetch_last5_for_horse(horse_id: int) -> str:
    cached = last5_from_cache(horse_id)
    if cached is not None:
        return cached
    try:
        payload = fetch_horse_results(horse_id)
    except AtgFetchError:
        return ""
    records = payload.get("records")
    last5 = compact_last5(records if isinstance(records, list) else [])
    store_last5(horse_id, last5)
    return last5


def _prefetch_last5(horse_ids: list[int]) -> None:
    missing = [hid for hid in horse_ids if last5_from_cache(hid) is None]
    if not missing:
        return
    with ThreadPoolExecutor(max_workers=_FORM_WORKERS) as pool:
        futures = {pool.submit(fetch_last5_for_horse, hid): hid for hid in missing}
        for fut in as_completed(futures):
            fut.result()


def extract_starts_from_game(
    payload: dict[str, Any],
    *,
    race_track: str,
    include_form: bool,
) -> dict[int, list[dict[str, Any]]]:
    races = payload.get("races")
    if not isinstance(races, list):
        return {}
    horse_ids: list[int] = []
    if include_form:
        for race in races:
            if not isinstance(race, dict):
                continue
            for start in race.get("starts") or []:
                if not isinstance(start, dict):
                    continue
                horse = start.get("horse") if isinstance(start.get("horse"), dict) else {}
                hid = horse.get("id") if isinstance(horse, dict) else None
                if isinstance(hid, int):
                    horse_ids.append(hid)
        _prefetch_last5(list(dict.fromkeys(horse_ids)))

    odds = extract_leg_odds(payload)
    dists = extract_leg_distributions(payload)
    out: dict[int, list[dict[str, Any]]] = {}
    for index, race in enumerate(races, start=1):
        if not isinstance(race, dict):
            continue
        rows: list[dict[str, Any]] = []
        for start in race.get("starts") or []:
            if not isinstance(start, dict):
                continue
            number = start.get("number")
            if not isinstance(number, int) or number <= 0:
                continue
            horse = start.get("horse") if isinstance(start.get("horse"), dict) else {}
            driver = start.get("driver") if isinstance(start.get("driver"), dict) else {}
            hid = horse.get("id") if isinstance(horse, dict) else None
            last5 = last5_from_cache(hid) if isinstance(hid, int) else None
            horse_home = _home_track(horse)
            kusk_home = _home_track(driver)
            scratched = bool(start.get("scratched"))
            odds_val = odds.get(index, {}).get(number)
            pct_val = dists.get(index, {}).get(number)
            if scratched:
                odds_val = None
                pct_val = None
            post = start.get("postPosition")
            rows.append(
                {
                    "number": number,
                    "postPosition": post if isinstance(post, int) else number,
                    "horse_id": hid if isinstance(hid, int) else None,
                    "name": horse.get("name") if isinstance(horse, dict) else None,
                    "scratched": scratched,
                    "kusk": _person_name(driver),
                    "last5": last5 or None,
                    "odds": odds_val,
                    "v85_pct": pct_val,
                    "horse_home": horse_home,
                    "kusk_home": kusk_home,
                    "km_horse": km_between(horse_home, race_track),
                    "km_kusk": km_between(kusk_home, race_track),
                }
            )
        out[index] = rows
    return out


def starts_from_yaml_card(card: RaceCard) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = {}
    for leg in card.legs:
        names = dict(leg.horse_names)
        rows: list[dict[str, Any]] = []
        seen: set[int] = set()
        for number in list(leg.horses) + list(leg.scratches):
            if number in seen:
                continue
            seen.add(number)
            rows.append(
                {
                    "number": number,
                    "postPosition": number,
                    "horse_id": None,
                    "name": names.get(number),
                    "scratched": number in leg.scratches,
                    "kusk": None,
                    "last5": None,
                    "odds": None,
                    "v85_pct": None,
                    "horse_home": None,
                    "kusk_home": None,
                    "km_horse": None,
                    "km_kusk": None,
                }
            )
        rows.sort(key=lambda r: r["number"])
        out[leg.leg] = rows
    return out


def leg_header(leg: Leg) -> dict[str, Any]:
    """Race header for one avdelning, including the ATG prize ladder when present."""
    info = leg.race_info
    race_info = None
    if info is not None:
        race_info = {
            "race_name": info.race_name,
            "distance_m": info.distance_m,
            "start_method": info.start_method,
            "prize": info.prize,
        }
    return {
        "leg": leg.leg,
        "race_label": leg.race_label,
        "start_time": leg.start_time,
        "race_info": race_info,
    }


def fetch_start_info(game_id: str, *, include_form: bool = True) -> dict[str, Any]:
    payload = fetch_v85_game(game_id)
    card = parse_atg_game(game_id, payload)
    starts = extract_starts_from_game(payload, race_track=card.track, include_form=include_form)
    return {
        "id": game_id,
        "game": "v85",
        "date": card.date,
        "track": card.track,
        "source": "atg",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "km_note": "ESTIMATE driving km (haversine × 1.35, round 10). Not ST avståndstabell.",
        "include_form": include_form,
        "starts_by_leg": {str(leg): rows for leg, rows in starts.items()},
        "legs": [leg_header(leg) for leg in card.legs],
    }
