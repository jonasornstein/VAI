"""Unit tests for portable betslip YAML I/O."""

from __future__ import annotations

from pathlib import Path

import pytest

from vai.io.betslip import (
    BetslipValidationError,
    betslip_basename,
    dump_betslip_yaml,
    next_available_path,
    parse_betslip_yaml,
    save_betslip_file,
    validate_betslip_payload,
)


def _sample(**overrides):
    data = {
        "vai_betslip_version": 1,
        "date": "2026-07-18",
        "track": "Axevalla",
        "game": "V85",
        "mode": "random",
        "stake_budget_sek": 500,
        "seed": 42,
        "frozen_legs": [3],
        "operator_pools": {
            "1": [2, 5],
            "2": [],
            "3": [1],
            "4": [],
            "5": [],
            "6": [],
            "7": [],
            "8": [],
        },
        "selections": {
            "1": [2, 5, 8],
            "2": [3],
            "3": [1],
            "4": [2],
            "5": [4],
            "6": [1, 2],
            "7": [5],
            "8": [6],
        },
        "cost_sek": 12.0,
        "combinations": 24,
    }
    data.update(overrides)
    return data


def test_betslip_basename_slugs_track() -> None:
    assert betslip_basename("2026-07-11", "Årjäng", "V85") == "2026-07-11-arjang-V85"
    assert betslip_basename("2026-07-18", "Axevalla", "v85") == "2026-07-18-axevalla-V85"


def test_next_available_path_increments(tmp_path: Path) -> None:
    first = next_available_path(tmp_path, "2026-07-18-axevalla-V85")
    assert first.name == "2026-07-18-axevalla-V85.yaml"
    first.write_text("x", encoding="utf-8")
    second = next_available_path(tmp_path, "2026-07-18-axevalla-V85")
    assert second.name == "2026-07-18-axevalla-V85-2.yaml"
    second.write_text("y", encoding="utf-8")
    third = next_available_path(tmp_path, "2026-07-18-axevalla-V85")
    assert third.name == "2026-07-18-axevalla-V85-3.yaml"


def test_validate_and_roundtrip_yaml() -> None:
    text = dump_betslip_yaml(_sample())
    assert "vai_betslip_version: 1" in text
    assert "track: Axevalla" in text
    parsed = parse_betslip_yaml(text)
    assert parsed["date"] == "2026-07-18"
    assert parsed["track"] == "Axevalla"
    assert parsed["game"] == "V85"
    assert parsed["mode"] == "random"
    assert parsed["seed"] == 42
    assert parsed["frozen_legs"] == [3]
    assert parsed["selections"]["1"] == [2, 5, 8]
    assert parsed["operator_pools"]["1"] == [2, 5]
    assert parsed["saved_at"]  # filled on dump


def test_operator_pools_default_from_selections() -> None:
    data = _sample()
    del data["operator_pools"]
    validated = validate_betslip_payload(data)
    assert validated["operator_pools"]["1"] == [2, 5, 8]


def test_missing_date_rejected() -> None:
    with pytest.raises(BetslipValidationError) as exc:
        validate_betslip_payload(_sample(date=""))
    assert exc.value.code == "MISSING_DATE"


def test_unsupported_version() -> None:
    with pytest.raises(BetslipValidationError) as exc:
        validate_betslip_payload(_sample(vai_betslip_version=99))
    assert exc.value.code == "UNSUPPORTED_VERSION"


def test_save_betslip_file_unique(tmp_path: Path) -> None:
    p1 = save_betslip_file(_sample(), directory=tmp_path)
    p2 = save_betslip_file(_sample(), directory=tmp_path)
    assert p1.name == "2026-07-18-axevalla-V85.yaml"
    assert p2.name == "2026-07-18-axevalla-V85-2.yaml"
    assert p1.is_file() and p2.is_file()
    assert parse_betslip_yaml(p1.read_text(encoding="utf-8"))["track"] == "Axevalla"


def test_yaml_parse_error() -> None:
    with pytest.raises(BetslipValidationError) as exc:
        parse_betslip_yaml("[unterminated")
    assert exc.value.code in ("YAML_ERROR", "INVALID_BETSLIP", "MISSING_DATE")
