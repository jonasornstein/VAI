from pathlib import Path

import pytest

from atg.io.race_card import load_race_card
from atg.models.race_card import RaceCard

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RACE_CARD = REPO_ROOT / "inbox" / "race-cards" / "2026-07-05-halmstad.yaml"


@pytest.fixture
def sample_race_card() -> RaceCard:
    return load_race_card(SAMPLE_RACE_CARD)