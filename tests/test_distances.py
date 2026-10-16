import json, os
os.environ["VAI_NO_OSRM"] = "1"
from vai.distances import road_km, fill_card

def test_same_track():
    assert road_km("SOL", "SOL") == 0

def test_fallback_solvalla_jagersro():
    assert road_km("SOL", "JGR") == 667

def test_fill_card_tmp_copy(tmp_path):
    card = {"trackCode": "5", "trackName": "Solvalla", "legs": [{"starters": [
        {"horseHemmabana": "Jägersro", "driverHemmabana": "SOL", "trainerHemmabana": None}]}]}
    p = tmp_path / "card.json"; p.write_text(json.dumps(card))
    r = fill_card(str(p))
    s = json.loads(p.read_text())["legs"][0]["starters"][0]
    assert r["today"] == "SOL"
    assert s["horseKm"] == 667 and s["driverKm"] == 0 and s["trainerKm"] is None
