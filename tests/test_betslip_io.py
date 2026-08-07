"""Unit tests for portable betslip YAML I/O."""

from __future__ import annotations

from pathlib import Path

import pytest

from vai.io.betslip import (
    BetslipValidationError,
    betslip_basename,
    delete_betslip_file,
    delete_betslip_files,
    dump_betslip_yaml,
    list_betslips,
    load_betslip_file,
    next_available_path,
    parse_betslip_yaml,
    safe_betslip_path,
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


def test_list_load_delete_betslips(tmp_path: Path) -> None:
    (tmp_path / "ignore-me.pdf").write_bytes(b"%PDF")
    p1 = save_betslip_file(_sample(date="2026-07-18", track="Axevalla"), directory=tmp_path)
    p2 = save_betslip_file(_sample(date="2026-07-11", track="Årjäng"), directory=tmp_path)

    listed = list_betslips(tmp_path)
    names = {item["filename"] for item in listed}
    assert p1.name in names
    assert p2.name in names
    assert all(item["filename"].endswith((".yaml", ".yml")) for item in listed)

    filtered = list_betslips(tmp_path, date="2026-07-18")
    assert len(filtered) == 1
    assert filtered[0]["track"] == "Axevalla"

    path, payload, text = load_betslip_file(tmp_path, p1.name)
    assert path == p1
    assert payload["track"] == "Axevalla"
    assert "vai_betslip_version" in text

    deleted = delete_betslip_file(tmp_path, p1.name)
    assert deleted.name == p1.name
    assert not p1.exists()
    with pytest.raises(BetslipValidationError) as exc:
        load_betslip_file(tmp_path, p1.name)
    assert exc.value.code == "NOT_FOUND"


def test_safe_betslip_path_rejects_traversal(tmp_path: Path) -> None:
    with pytest.raises(BetslipValidationError) as exc:
        safe_betslip_path(tmp_path, "../secrets.yaml")
    assert exc.value.code == "INVALID_FILENAME"
    with pytest.raises(BetslipValidationError):
        safe_betslip_path(tmp_path, "/etc/passwd.yaml")
    with pytest.raises(BetslipValidationError):
        safe_betslip_path(tmp_path, "not-yaml.txt")


def test_delete_betslip_files_batch(tmp_path: Path) -> None:
    p1 = save_betslip_file(_sample(), directory=tmp_path)
    p2 = save_betslip_file(_sample(), directory=tmp_path)
    result = delete_betslip_files(tmp_path, [p1.name, p2.name, "missing.yaml", "../x.yaml"])
    assert p1.name in result["deleted"]
    assert p2.name in result["deleted"]
    assert not p1.exists() and not p2.exists()
    failed_names = {f["filename"] for f in result["failed"]}
    assert "missing.yaml" in failed_names
    assert "../x.yaml" in failed_names
