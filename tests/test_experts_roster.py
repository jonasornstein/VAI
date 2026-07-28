from pathlib import Path

import yaml

from vai.io.experts_roster import (
    ExpertRosterError,
    add_expert,
    default_roster_path,
    delete_expert,
    list_experts,
    load_experts_roster,
    reset_experts_roster,
    suggest_expert_id,
    update_expert,
    working_roster_path,
)


def test_load_experts_roster_has_core_ids() -> None:
    entries = load_experts_roster()
    ids = {e.expert_id for e in entries}
    assert "bjorn-goop" in ids
    assert "referenten" in ids
    assert "fixture" in ids
    assert len(entries) >= 20


def test_list_experts_excludes_fixture_by_default() -> None:
    entries = list_experts()
    assert all(e.expert_id != "fixture" for e in entries)
    assert any(e.expert_id == "leboff" for e in entries)


def test_list_experts_free_only() -> None:
    free = list_experts(free_only=True)
    assert free
    assert all(e.free is True for e in free)


def test_cold_start_uses_defaults(tmp_path: Path) -> None:
    root = tmp_path
    assert not working_roster_path(root).is_file()
    entries = list_experts(repo_root=root)
    assert any(e.expert_id == "bjorn-goop" for e in entries)
    assert not working_roster_path(root).is_file()


def test_add_expert_materializes_working_file(tmp_path: Path) -> None:
    root = tmp_path
    entry = add_expert(
        {
            "expert_id": "eddie-ostlund",
            "display_name": "Eddie Östlund",
            "outlet": "Travcash",
            "free": True,
        },
        repo_root=root,
    )
    assert entry.expert_id == "eddie-ostlund"
    working = working_roster_path(root)
    assert working.is_file()
    loaded = load_experts_roster(working)
    assert any(e.expert_id == "eddie-ostlund" for e in loaded)
    # Defaults were copied in
    assert any(e.expert_id == "bjorn-goop" for e in loaded)


def test_add_expert_duplicate_id(tmp_path: Path) -> None:
    root = tmp_path
    add_expert(
        {"expert_id": "new-tipster", "display_name": "New"},
        repo_root=root,
    )
    try:
        add_expert(
            {"expert_id": "new-tipster", "display_name": "Dup"},
            repo_root=root,
        )
        raise AssertionError("expected EXPERT_EXISTS")
    except ExpertRosterError as exc:
        assert exc.code == "EXPERT_EXISTS"


def test_add_expert_invalid_id(tmp_path: Path) -> None:
    try:
        add_expert(
            {"expert_id": "Bad ID!", "display_name": "X"},
            repo_root=tmp_path,
        )
        raise AssertionError("expected INVALID_EXPERT")
    except ExpertRosterError as exc:
        assert exc.code == "INVALID_EXPERT"


def test_delete_expert_leaves_tips_untouched(tmp_path: Path) -> None:
    root = tmp_path
    # Seed a tip file that should survive roster delete
    tip_dir = root / "inbox" / "expert-tips" / "2026-08-01-solvalla"
    tip_dir.mkdir(parents=True)
    tip_path = tip_dir / "bjorn-goop-2026-08-01.yaml"
    tip_path.write_text("tip_id: bjorn-goop-2026-08-01\nexpert_id: bjorn-goop\n", encoding="utf-8")

    deleted = delete_expert("bjorn-goop", repo_root=root)
    assert deleted.expert_id == "bjorn-goop"
    assert tip_path.is_file()
    assert all(e.expert_id != "bjorn-goop" for e in list_experts(repo_root=root))


def test_delete_fixture_forbidden(tmp_path: Path) -> None:
    try:
        delete_expert("fixture", repo_root=tmp_path)
        raise AssertionError("expected FORBIDDEN_ID")
    except ExpertRosterError as exc:
        assert exc.code == "FORBIDDEN_ID"


def test_delete_unknown(tmp_path: Path) -> None:
    try:
        delete_expert("no-such-expert", repo_root=tmp_path)
        raise AssertionError("expected EXPERT_NOT_FOUND")
    except ExpertRosterError as exc:
        assert exc.code == "EXPERT_NOT_FOUND"


def test_update_expert(tmp_path: Path) -> None:
    root = tmp_path
    updated = update_expert(
        "leboff",
        {"display_name": "Leboff (updated)", "notes": "test note", "free": False},
        repo_root=root,
    )
    assert updated.display_name == "Leboff (updated)"
    assert updated.notes == "test note"
    assert updated.free is False
    assert updated.expert_id == "leboff"
    again = next(e for e in list_experts(repo_root=root) if e.expert_id == "leboff")
    assert again.display_name == "Leboff (updated)"


def test_reset_restores_defaults(tmp_path: Path) -> None:
    root = tmp_path
    add_expert(
        {"expert_id": "temp-custom", "display_name": "Temp"},
        repo_root=root,
    )
    delete_expert("leboff", repo_root=root)
    ids_before = {e.expert_id for e in list_experts(repo_root=root)}
    assert "temp-custom" in ids_before
    assert "leboff" not in ids_before

    restored = reset_experts_roster(repo_root=root)
    default_ids = {e.expert_id for e in load_experts_roster(default_roster_path())}
    restored_ids = {e.expert_id for e in restored}
    assert restored_ids == default_ids
    effective = {e.expert_id for e in list_experts(repo_root=root, exclude_fixture=False)}
    assert "temp-custom" not in effective
    assert "leboff" in effective
    assert "fixture" in effective


def test_suggest_expert_id() -> None:
    assert suggest_expert_id("Eddie Östlund") == "eddie-ostlund"
    assert suggest_expert_id("Björn Goop") == "bjorn-goop"


def test_working_roster_yaml_roundtrip(tmp_path: Path) -> None:
    root = tmp_path
    add_expert(
        {
            "expert_id": "round-trip",
            "display_name": "Round Trip",
            "free": False,
            "publishes_full_system": "partial",
        },
        repo_root=root,
    )
    data = yaml.safe_load(working_roster_path(root).read_text(encoding="utf-8"))
    assert isinstance(data["experts"], list)
    found = next(e for e in data["experts"] if e["expert_id"] == "round-trip")
    assert found["free"] is False
    assert found["publishes_full_system"] == "partial"
