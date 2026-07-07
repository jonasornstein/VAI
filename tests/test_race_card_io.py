from pathlib import Path

import pytest

from atg.io.race_card import RaceCardValidationError, load_race_card

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RACE_CARD = REPO_ROOT / "inbox" / "race-cards" / "2026-07-05-halmstad.yaml"


def test_load_sample_race_card() -> None:
    card = load_race_card(SAMPLE_RACE_CARD)
    assert card.game == "v85"
    assert card.track == "Halmstad"
    assert card.date == "2026-07-05"
    assert len(card.legs) == 8
    assert card.leg_by_number(1).race_label == "V85-1"
    assert 5 not in card.horses_for_leg(1)
    assert 5 in card.leg_by_number(1).scratches


def test_rejects_wrong_leg_count(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "game: v85\ndate: 2026-01-01\ntrack: X\nsource: manual\n"
        "fetched_at: 2026-01-01T00:00:00Z\nsettled: false\n"
        "legs:\n  - leg: 1\n    race_label: V85-1\n    horses: [1]\n",
        encoding="utf-8",
    )
    with pytest.raises(RaceCardValidationError, match="exactly 8 legs"):
        load_race_card(bad)