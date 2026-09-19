"""Estimated road km between Swedish trotting tracks (not ST avståndstabell)."""

from __future__ import annotations

import math

# Approximate WGS84 of the travbana (not the town centre).
TRACK_COORDS: dict[str, tuple[float, float]] = {
    "Arvika": (59.655, 12.591),
    "Axevalla": (58.386, 13.428),
    "Bergsåker": (62.414, 17.306),
    "Boden": (65.825, 21.689),
    "Bollnäs": (61.348, 16.395),
    "Dannero": (62.931, 17.778),
    "Eskilstuna": (59.427, 16.632),
    "Färjestad": (59.389, 13.473),
    "Gävle": (60.674, 17.142),
    "Hagmyren": (61.729, 17.103),
    "Halmstad": (56.674, 12.857),
    "Hoting": (64.113, 16.204),
    "Jägersro": (55.570, 13.052),
    "Kalmar": (56.663, 16.357),
    "Karlshamn": (56.170, 14.863),
    "Lindesberg": (59.592, 15.222),
    "Lycksele": (64.595, 18.676),
    "Mantorp": (58.351, 15.287),
    "Oviken": (62.995, 14.445),
    "Romme": (60.432, 15.432),
    "Rättvik": (60.886, 15.118),
    "Skellefteå": (64.751, 20.951),
    "Solvalla": (59.365, 17.940),
    "Solänget": (63.290, 18.715),
    "Tingsryd": (56.525, 14.979),
    "Umåker": (63.826, 20.264),
    "Vaggeryd": (57.498, 14.148),
    "Visby": (57.635, 18.294),
    "Åby": (57.659, 12.012),
    "Åmål": (59.051, 12.705),
    "Årjäng": (59.392, 12.133),
    "Örebro": (59.275, 15.207),
    "Östersund": (63.179, 14.636),
}

_ROAD_FACTOR = 1.35
_EARTH_KM = 6371.0


def _haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * _EARTH_KM * math.asin(min(1.0, math.sqrt(h)))


def km_between(home: str | None, race_track: str | None) -> int | None:
    """Estimated driving km, rounded to 10. Same track → 0. Unknown → None."""
    if not home or not race_track:
        return None
    if home == race_track:
        return 0
    start = TRACK_COORDS.get(home)
    end = TRACK_COORDS.get(race_track)
    if start is None or end is None:
        return None
    road = _haversine_km(start, end) * _ROAD_FACTOR
    if road < 5:
        return 0
    return int(round(road / 10.0) * 10)
