from pathlib import Path

import pytest

from vai.io.race_card import load_race_card
from vai.models.race_card import RaceCard

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RACE_CARD = REPO_ROOT / "inbox" / "race-cards" / "2026-07-05-halmstad.yaml"


@pytest.fixture
def sample_race_card() -> RaceCard:
    return load_race_card(SAMPLE_RACE_CARD)

@pytest.fixture(autouse=True)
def _vai_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Write endpoints fail closed without VAI_API_KEY; give tests a known key."""
    monkeypatch.setenv("VAI_API_KEY", "test-key-0123456789abcdef")
