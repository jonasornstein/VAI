from pathlib import Path

import pytest

from vai.io.expert_tips import (
    ExpertTipValidationError,
    find_expert_tip,
    list_expert_tips,
    load_expert_tip,
    parse_expert_tip,
)
from vai.io.race_card import load_race_card
from vai.models.expert_tip import ExpertError, ExpertResult
from vai.strategies.expert import generate_expert_v1


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _fixture_tip_path() -> Path:
    return (
        _repo_root()
        / "inbox"
        / "expert-tips"
        / "2026-07-18-axevalla"
        / "fixture-axevalla-2026-07-18.yaml"
    )


def test_load_fixture_tip() -> None:
    tip = load_expert_tip(_fixture_tip_path())
    assert tip.tip_id == "fixture-axevalla-2026-07-18"
    assert tip.expert_id == "fixture"
    assert len(tip.legs) == 8
    assert tip.legs[1] == [1]


def test_list_tips_filter_date() -> None:
    tips_dir = _repo_root() / "inbox" / "expert-tips"
    all_tips = list_expert_tips(tips_dir)
    assert any(t.tip_id == "fixture-axevalla-2026-07-18" for t in all_tips)
    filtered = list_expert_tips(tips_dir, date="2026-07-18", track="Axevalla")
    assert len(filtered) >= 1
    assert filtered[0].cost_sek == 54.0  # 1*2*3*3*3*1*2*1 * 0.5 = 108*0.5? Wait
    # 1×2×3×3×3×1×2×1 = 108 combinations → 54.0 SEK


def test_fixture_cost_is_54() -> None:
    tip = load_expert_tip(_fixture_tip_path())
    result = generate_expert_v1(tip)
    assert isinstance(result, ExpertResult)
    assert result.combinations == 108
    assert result.cost_sek == 54.0
    assert result.cost_breakdown == "1×2×3×3×3×1×2×1"


def test_generate_with_race_card() -> None:
    card = load_race_card(_repo_root() / "inbox" / "race-cards" / "2026-07-18-axevalla.yaml")
    result = generate_expert_v1(
        "fixture-axevalla-2026-07-18",
        race_card=card,
        tips_dir=_repo_root() / "inbox" / "expert-tips",
    )
    assert isinstance(result, ExpertResult)
    assert result.manifest.mode == "expert"
    assert result.manifest.tip_id == "fixture-axevalla-2026-07-18"


def test_override_leg() -> None:
    tip = load_expert_tip(_fixture_tip_path())
    card = load_race_card(_repo_root() / "inbox" / "race-cards" / "2026-07-18-axevalla.yaml")
    result = generate_expert_v1(tip, race_card=card, overrides={1: [2, 3]})
    assert isinstance(result, ExpertResult)
    assert result.selections[1] == [2, 3]
    assert result.manifest.overridden_legs == (1,)
    assert result.combinations == 216  # doubled leg 1


def test_invalid_horse_against_card() -> None:
    tip = load_expert_tip(_fixture_tip_path())
    card = load_race_card(_repo_root() / "inbox" / "race-cards" / "2026-07-18-axevalla.yaml")
    # Leg 3 only has horses 1-6
    result = generate_expert_v1(tip, race_card=card, overrides={3: [99]})
    assert isinstance(result, ExpertError)
    assert result.code == "INVALID_HORSE"


def test_missing_leg_rejected() -> None:
    with pytest.raises(ExpertTipValidationError):
        parse_expert_tip(
            {
                "tip_id": "bad",
                "expert_id": "x",
                "expert_name": "X",
                "game": "v85",
                "date": "2026-01-01",
                "track": "Test",
                "legs": {leg: [1] for leg in range(1, 8)},
            }
        )


def test_find_tip_not_found() -> None:
    with pytest.raises(ExpertTipValidationError) as exc:
        find_expert_tip(_repo_root() / "inbox" / "expert-tips", "no-such-tip")
    assert exc.value.code == "TIP_NOT_FOUND"
