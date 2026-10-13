import pytest

from vai.card import add_streck_flags


def _card(*starters):
    return {"legs": [{"starters": [dict(s) for s in starters]}]}


def _even_leg(book, n=10):
    """n starters all odds 10 -> each win = 100/n %. First starter gets `book`."""
    ss = [{"startNumber": i + 1, "odds": 10.0, "bookingPct": 10.0, "scratched": False} for i in range(n)]
    ss[0]["bookingPct"] = book
    return add_streck_flags(_card(*ss))["legs"][0]["starters"]


@pytest.mark.parametrize("book,flag", [(13.0, "over"), (7.0, "under"), (12.9, None), (7.1, None), (12.96, "over"), (7.04, "under"), (12.94, None), (7.06, None)])
def test_boundaries(book, flag):
    s = _even_leg(book)[0]
    assert s["winChancePct"] == 10.0
    assert s["streckRatio"] == round(book / 10, 2)
    assert s["streckFlag"] == flag


def test_boundary_non_trivial_floats():
    # 3 equal starters: win = 33.333..%; book chosen so ratio is mathematically 1.3 / 0.7
    ss = [{"odds": 3.0, "bookingPct": 10, "scratched": False} for _ in range(3)]
    ss[0]["bookingPct"] = 1.3 * 100 / 3
    ss[1]["bookingPct"] = 0.7 * 100 / 3
    out = add_streck_flags(_card(*ss))["legs"][0]["starters"]
    assert out[0]["streckFlag"] == "over"
    assert out[1]["streckFlag"] == "under"


def test_both_under_3pct_no_flag():
    # 50 equal starters -> win 2%; streck 1% (ratio 0.5) but both < 3
    s = _even_leg(1.0, n=50)[0]
    assert s["streckRatio"] == 0.5 and s["streckFlag"] is None


def test_one_above_3pct_flagged():
    s = _even_leg(4.0, n=50)[0]  # win 2%, streck 4% -> ratio 2.0
    assert s["streckFlag"] == "over"
    s = _even_leg(1.0, n=20)[0]  # win 5%, streck 1% -> ratio 0.2
    assert s["streckFlag"] == "under"


def test_scratched_and_missing():
    out = add_streck_flags(_card(
        {"odds": 2.0, "bookingPct": 50, "scratched": True},
        {"odds": None, "bookingPct": 30, "scratched": False},
        {"odds": 0, "bookingPct": 30, "scratched": False},
        {"odds": 4.0, "bookingPct": None, "scratched": False},
        {"odds": 4.0, "bookingPct": 20, "scratched": False},
    ))["legs"][0]["starters"]
    for s in out[:4]:
        assert s["streckRatio"] is None and s["streckFlag"] is None and s["winChancePct"] is None
    # only two live starters (both odds 4) -> 50% each; scratched excluded from sum
    assert out[4]["winChancePct"] == 50.0


def test_normalization_sums_to_100():
    odds = [1.8, 3.5, 6.2, 12.0, 25.0, 60.0]
    out = add_streck_flags(_card(*[{"odds": o, "bookingPct": 10, "scratched": False} for o in odds]))
    pct = [s["winChancePct"] for s in out["legs"][0]["starters"]]
    assert sum(pct) == pytest.approx(100, abs=0.1 * len(odds) / 2)
    inv = [1 / o for o in odds]
    assert pct[0] == round(inv[0] / sum(inv) * 100, 1)


def test_empty_leg_no_crash():
    assert add_streck_flags({"legs": [{"starters": []}]}) == {"legs": [{"starters": []}]}


def test_flag_uses_rounded_ratio():
    s = _even_leg(12.96)[0]  # raw 1.296 -> 1.30
    assert s["streckRatio"] == 1.3 and s["streckFlag"] == "over"
    s = _even_leg(7.04)[0]  # raw 0.704 -> 0.70
    assert s["streckRatio"] == 0.7 and s["streckFlag"] == "under"
