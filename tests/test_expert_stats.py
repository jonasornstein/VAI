from pathlib import Path

from vai.expert_stats import compute_expert_horse_stats, expert_horse_stats_for_round
from vai.io.expert_tips import load_expert_tip, parse_expert_tip
from vai.models.expert_tip import ExpertTip

REPO = Path(__file__).resolve().parents[1]
TIPS_DIR = REPO / "inbox" / "expert-tips"
BOLLNAS = TIPS_DIR / "2026-07-25-bollnas"


def _tip(**overrides: object) -> ExpertTip:
    base = {
        "tip_id": "t1",
        "expert_id": "alpha",
        "expert_name": "Alpha",
        "game": "v85",
        "date": "2026-07-25",
        "track": "Bollnäs",
        "legs": {i: [1] for i in range(1, 9)},
    }
    base.update(overrides)
    return parse_expert_tip(base)


def test_bollnas_leg2_horse2_is_unanimous() -> None:
    stats = expert_horse_stats_for_round(
        TIPS_DIR,
        date="2026-07-25",
        track="Bollnäs",
        repo_root=REPO,
        visible_only=True,
        exclude_fixture=True,
    )
    assert stats.tip_count == 5
    assert stats.expert_count == 5
    leg2 = {row.horse: row for row in stats.legs[2]}
    assert leg2[2].count == 5
    assert leg2[2].pct == 100.0
    leg1 = {row.horse: row for row in stats.legs[1]}
    assert leg1[3].count == 5
    assert leg1[6].count == 5
    assert 1 in leg1
    assert 99 not in leg1  # absent horses omitted from API rows
    leg8 = {row.horse: row for row in stats.legs[8]}
    assert leg8[3].count == 5
    assert leg8[3].pct == 100.0
    # split on leg 4
    leg4 = {row.horse: row for row in stats.legs[4]}
    assert leg4[1].count == 3
    assert leg4[4].count == 3
    assert leg4[1].pct == 60.0


def test_bollnas_yaml_matches_inbox_files() -> None:
    tips = [load_expert_tip(p) for p in sorted(BOLLNAS.glob("*.yaml"))]
    assert len(tips) == 5
    stats = compute_expert_horse_stats(tips, date="2026-07-25", track="Bollnäs")
    assert stats.tip_count == 5
    assert stats.legs[2][0].horse == 2
    assert stats.legs[2][0].count == 5


def test_multi_tip_same_expert_counts_twice() -> None:
    a = _tip(tip_id="a-1", expert_id="same", expert_name="Same", legs={i: [3] for i in range(1, 9)})
    b = _tip(tip_id="a-2", expert_id="same", expert_name="Same", legs={i: [3, 5] for i in range(1, 9)})
    stats = compute_expert_horse_stats([a, b], date="2026-07-25", track="Bollnäs")
    assert stats.tip_count == 2
    assert stats.expert_count == 1
    leg1 = {row.horse: row for row in stats.legs[1]}
    assert leg1[3].count == 2
    assert leg1[3].pct == 100.0
    assert leg1[5].count == 1
    assert leg1[5].pct == 50.0


def test_empty_tips_zero_population() -> None:
    stats = compute_expert_horse_stats([], date="2026-07-25", track="Bollnäs")
    assert stats.tip_count == 0
    assert stats.expert_count == 0
    assert stats.tips == ()
    for leg in range(1, 9):
        assert stats.legs[leg] == ()


def test_visible_filter_shrinks_n() -> None:
    stats_all = expert_horse_stats_for_round(
        TIPS_DIR,
        date="2026-07-25",
        track="Bollnäs",
        allowed_expert_ids=["bjorn-goop", "leboff"],
        exclude_fixture=True,
    )
    assert stats_all.tip_count == 2
    assert stats_all.expert_count == 2
    leg2 = {row.horse: row for row in stats_all.legs[2]}
    assert leg2[2].count == 2
    assert leg2[2].pct == 100.0
    # horse 9 only in leboff + travstugan among the five; with goop+leboff → 1/2
    assert leg2[9].count == 1
    assert leg2[9].pct == 50.0


def test_fixture_excluded_from_round_stats() -> None:
    stats = expert_horse_stats_for_round(
        TIPS_DIR,
        date="2026-07-18",
        track="Axevalla",
        repo_root=REPO,
        visible_only=False,
        exclude_fixture=True,
    )
    assert all(t.expert_id != "fixture" for t in stats.tips)
    # only fixture tip exists for that day in inbox
    assert stats.tip_count == 0


def test_to_dict_shape() -> None:
    tips = [load_expert_tip(p) for p in sorted(BOLLNAS.glob("*.yaml"))]
    payload = compute_expert_horse_stats(tips, date="2026-07-25", track="Bollnäs").to_dict()
    assert payload["tip_count"] == 5
    assert "1" in payload["legs"]
    row = payload["legs"]["1"][0]
    assert "horse" in row and "count" in row and "pct" in row
    assert "expert_ids" in row and "expert_names" in row


def test_duplicate_horse_in_one_tip_counts_once() -> None:
    # Schema forbids duplicates; F-049 still de-dupes per tip per leg.
    tip = ExpertTip(
        tip_id="dup",
        expert_id="alpha",
        expert_name="Alpha",
        game="v85",
        date="2026-07-25",
        track="Bollnäs",
        legs={1: [2, 2, 3], **{i: [1] for i in range(2, 9)}},
    )
    stats = compute_expert_horse_stats([tip])
    leg1 = {row.horse: row for row in stats.legs[1]}
    assert leg1[2].count == 1
