"""Fill horseKm/driverKm/trainerKm on a card JSON in place. Usage: python3 -m vai.distances.fill_card card.json"""
import json, sys, unicodedata
from .distances import TRACKS, ALIASES, road_km
EXTRA = {"JAG": "JGR", "BOD": "BON", "OVJ": "OVI"}

def norm(v):
    if isinstance(v, dict): v = v.get("code") or v.get("name")
    if not v: return None
    s = str(v).strip(); u = s.upper()
    if u in TRACKS: return u
    if u in EXTRA: return EXTRA[u]
    k = s.lower().replace("travet", "").replace("trav", "").strip()
    return ALIASES.get(k) or ALIASES.get(unicodedata.normalize("NFKD", k).encode("ascii", "ignore").decode())

def fill_card(path):
    d = json.load(open(path))
    today = norm(d.get("trackCode")) or norm(d.get("trackName"))
    miss, n = set(), 0
    for leg in d["legs"]:
        t = norm(leg.get("trackCode")) or norm(leg.get("trackName")) or today
        for s in leg["starters"]:
            for r in ("horse", "driver", "trainer"):
                raw = s.get(f"{r}Hemmabana"); h = norm(raw)
                if h is None or t is None: miss.add(str(raw)); s[f"{r}Km"] = None
                else: s[f"{r}Km"] = road_km(h, t); n += 1
    json.dump(d, open(path, "w"), ensure_ascii=False, indent=2)
    return {"filled": n, "today": today, "unmapped": sorted(miss)}

if __name__ == "__main__":
    print(fill_card(sys.argv[1]))
