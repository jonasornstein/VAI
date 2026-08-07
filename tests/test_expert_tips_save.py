"""Tests for expert tip save / find-by-expert helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from vai.io.expert_tips import (
    ExpertTipValidationError,
    allocate_tip_id,
    default_tip_id,
    delete_expert_tip,
    find_expert_tip_for,
    list_expert_tips,
    load_expert_tip,
    save_expert_tip,
    track_slug,
)


def _minimal_legs() -> dict[int, list[int]]:
    return {leg: [1] for leg in range(1, 9)}


def test_track_slug_strips_accents() -> None:
    assert track_slug("Bollnäs") == "bollnas"
    assert track_slug("Årjäng") == "arjang"
    assert track_slug("Axevalla") == "axevalla"


def test_default_tip_id() -> None:
    assert default_tip_id("bjorn-goop", "2026-07-25") == "bjorn-goop-2026-07-25"


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    tip = save_expert_tip(
        tmp_path,
        {
            "expert_id": "bjorn-goop",
            "expert_name": "Björn Goop",
            "product_name": "Björnkollen",
            "game": "v85",
            "date": "2026-07-25",
            "track": "Bollnäs",
            "source_url": "https://example.test/tip",
            "legs": _minimal_legs(),
            "rationale": "test tip",
        },
        fetched_at="2026-07-25T12:00:00Z",
    )
    assert tip.tip_id == "bjorn-goop-2026-07-25"
    assert tip.path is not None
    path = Path(tip.path)
    assert path.is_file()
    assert path.parent.name == "2026-07-25-bollnas"

    loaded = load_expert_tip(path)
    assert loaded.expert_id == "bjorn-goop"
    assert loaded.legs[1] == [1]
    assert loaded.status == "DRAFT"
    assert loaded.fetched_at == "2026-07-25T12:00:00Z"

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert raw["date"] == "2026-07-25"
    assert raw["legs"][1] == [1] or raw["legs"]["1"] == [1]


def test_overwrite_same_tip_id(tmp_path: Path) -> None:
    first = save_expert_tip(
        tmp_path,
        {
            "expert_id": "leboff",
            "expert_name": "Leboff",
            "game": "v85",
            "date": "2026-07-25",
            "track": "Bollnäs",
            "legs": _minimal_legs(),
        },
        fetched_at="2026-07-25T10:00:00Z",
    )
    found = find_expert_tip_for(
        tmp_path, expert_id="leboff", date="2026-07-25", track="Bollnäs"
    )
    assert found is not None
    assert found.tip_id == "leboff-2026-07-25"

    legs2 = _minimal_legs()
    legs2[1] = [2, 4]
    updated = save_expert_tip(
        tmp_path,
        {
            "tip_id": first.tip_id,
            "expert_id": "leboff",
            "expert_name": "Leboff",
            "game": "v85",
            "date": "2026-07-25",
            "track": "Bollnäs",
            "legs": legs2,
        },
        fetched_at="2026-07-25T11:00:00Z",
    )
    assert updated.tip_id == "leboff-2026-07-25"
    assert Path(updated.path).resolve() == Path(found.path).resolve()  # type: ignore[arg-type]
    assert load_expert_tip(updated.path).legs[1] == [2, 4]  # type: ignore[arg-type]
    # Only one yaml when same tip_id is updated
    yamls = list(tmp_path.rglob("*.yaml"))
    assert len(yamls) == 1


def test_multiple_tips_same_expert_date_track(tmp_path: Path) -> None:
    """Same expert may have several systems for one omgång."""
    first = save_expert_tip(
        tmp_path,
        {
            "expert_id": "stridbeck",
            "expert_name": "Stridbeck",
            "product_name": "Stora V85",
            "game": "v85",
            "date": "2026-07-25",
            "track": "Bollnäs",
            "legs": _minimal_legs(),
        },
        fetched_at="2026-07-25T10:00:00Z",
    )
    legs2 = _minimal_legs()
    legs2[1] = [3, 5]
    second = save_expert_tip(
        tmp_path,
        {
            "expert_id": "stridbeck",
            "expert_name": "Stridbeck",
            "product_name": "Lilla V85",
            "game": "v85",
            "date": "2026-07-25",
            "track": "Bollnäs",
            "legs": legs2,
        },
        fetched_at="2026-07-25T11:00:00Z",
    )
    assert first.tip_id == "stridbeck-2026-07-25"
    assert second.tip_id == "stridbeck-2026-07-25-2"
    assert first.tip_id != second.tip_id
    yamls = list(tmp_path.rglob("*.yaml"))
    assert len(yamls) == 2
    listed = list_expert_tips(
        tmp_path, date="2026-07-25", track="Bollnäs", expert_id="stridbeck"
    )
    assert len(listed) == 2
    ids = {t.tip_id for t in listed}
    assert ids == {first.tip_id, second.tip_id}
    assert load_expert_tip(second.path).legs[1] == [3, 5]  # type: ignore[arg-type]


def test_allocate_tip_id_skips_existing(tmp_path: Path) -> None:
    save_expert_tip(
        tmp_path,
        {
            "expert_id": "x",
            "expert_name": "X",
            "game": "v85",
            "date": "2026-01-01",
            "track": "Test",
            "legs": _minimal_legs(),
        },
    )
    assert allocate_tip_id(tmp_path, "x", "2026-01-01") == "x-2026-01-01-2"


def test_save_rejects_empty_leg(tmp_path: Path) -> None:
    legs = _minimal_legs()
    legs[3] = []
    with pytest.raises(ExpertTipValidationError):
        save_expert_tip(
            tmp_path,
            {
                "expert_id": "x",
                "expert_name": "X",
                "game": "v85",
                "date": "2026-01-01",
                "track": "Test",
                "legs": legs,
            },
        )


def test_find_missing_returns_none(tmp_path: Path) -> None:
    assert (
        find_expert_tip_for(tmp_path, expert_id="nope", date="2026-01-01", track="X")
        is None
    )


def test_delete_expert_tip_removes_yaml(tmp_path: Path) -> None:
    saved = save_expert_tip(
        tmp_path,
        {
            "expert_id": "referenten",
            "expert_name": "Referenten",
            "game": "v85",
            "date": "2026-08-02",
            "track": "Jägersro",
            "legs": _minimal_legs(),
        },
        fetched_at="2026-08-02T10:00:00Z",
    )
    path = Path(saved.path)  # type: ignore[arg-type]
    assert path.is_file()

    deleted = delete_expert_tip(tmp_path, tip_id=saved.tip_id)
    assert deleted.tip_id == saved.tip_id
    assert not path.is_file()
    assert (
        find_expert_tip_for(
            tmp_path, expert_id="referenten", date="2026-08-02", track="Jägersro"
        )
        is None
    )


def test_delete_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(ExpertTipValidationError) as exc:
        delete_expert_tip(tmp_path, tip_id="no-such-tip")
    assert exc.value.code == "TIP_NOT_FOUND"
