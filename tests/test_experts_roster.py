from pathlib import Path

import yaml

from vai.io.experts_roster import (
    ExpertRosterError,
    add_expert,
    default_roster_path,
    delete_expert,
    list_experts,
    load_experts_roster,
    reorder_experts,
    reset_experts_roster,
    set_all_visible,
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


def test_defaults_visible_true_when_missing() -> None:
    entries = load_experts_roster()
    assert entries
    assert all(e.visible is True for e in entries)


def test_list_experts_visible_only(tmp_path: Path) -> None:
    root = tmp_path
    update_expert("leboff", {"visible": False}, repo_root=root)
    all_entries = list_experts(repo_root=root)
    assert any(e.expert_id == "leboff" and e.visible is False for e in all_entries)
    visible = list_experts(repo_root=root, visible_only=True)
    assert all(e.visible is True for e in visible)
    assert all(e.expert_id != "leboff" for e in visible)


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


def test_delete_expert_soft_hides_and_leaves_tips(tmp_path: Path) -> None:
    root = tmp_path
    # Seed a tip file that should survive roster soft-hide
    tip_dir = root / "inbox" / "expert-tips" / "2026-08-01-solvalla"
    tip_dir.mkdir(parents=True)
    tip_path = tip_dir / "bjorn-goop-2026-08-01.yaml"
    tip_path.write_text("tip_id: bjorn-goop-2026-08-01\nexpert_id: bjorn-goop\n", encoding="utf-8")

    hidden = delete_expert("bjorn-goop", repo_root=root)
    assert hidden.expert_id == "bjorn-goop"
    assert hidden.visible is False
    assert tip_path.is_file()
    # Row retained in full list
    still_there = next(e for e in list_experts(repo_root=root) if e.expert_id == "bjorn-goop")
    assert still_there.visible is False
    assert all(e.expert_id != "bjorn-goop" for e in list_experts(repo_root=root, visible_only=True))
    # Idempotent second hide
    again = delete_expert("bjorn-goop", repo_root=root)
    assert again.visible is False


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
        {
            "display_name": "Leboff (updated)",
            "notes": "test note",
            "free": False,
            "visible": False,
        },
        repo_root=root,
    )
    assert updated.display_name == "Leboff (updated)"
    assert updated.notes == "test note"
    assert updated.free is False
    assert updated.visible is False
    assert updated.expert_id == "leboff"
    again = next(e for e in list_experts(repo_root=root) if e.expert_id == "leboff")
    assert again.display_name == "Leboff (updated)"
    assert again.visible is False
    shown = update_expert("leboff", {"visible": True}, repo_root=root)
    assert shown.visible is True


def test_reset_restores_defaults(tmp_path: Path) -> None:
    root = tmp_path
    add_expert(
        {"expert_id": "temp-custom", "display_name": "Temp"},
        repo_root=root,
    )
    delete_expert("leboff", repo_root=root)
    ids_before = {e.expert_id for e in list_experts(repo_root=root)}
    assert "temp-custom" in ids_before
    assert "leboff" in ids_before
    leboff = next(e for e in list_experts(repo_root=root) if e.expert_id == "leboff")
    assert leboff.visible is False

    restored = reset_experts_roster(repo_root=root)
    default_ids = {e.expert_id for e in load_experts_roster(default_roster_path())}
    restored_ids = {e.expert_id for e in restored}
    assert restored_ids == default_ids
    effective = {e.expert_id for e in list_experts(repo_root=root, exclude_fixture=False)}
    assert "temp-custom" not in effective
    assert "leboff" in effective
    assert "fixture" in effective
    leboff_after = next(e for e in list_experts(repo_root=root) if e.expert_id == "leboff")
    assert leboff_after.visible is True


def test_set_all_visible(tmp_path: Path) -> None:
    root = tmp_path
    public, updated = set_all_visible(False, repo_root=root)
    assert public
    assert updated == len(public)
    assert all(e.visible is False for e in public)
    assert all(e.visible is False for e in list_experts(repo_root=root, visible_only=False))
    # Idempotent
    _, updated2 = set_all_visible(False, repo_root=root)
    assert updated2 == 0
    public_on, updated_on = set_all_visible(True, repo_root=root)
    assert updated_on == len(public_on)
    assert all(e.visible is True for e in public_on)
    # fixture not in public list and still present in full roster
    full = list_experts(repo_root=root, exclude_fixture=False)
    assert any(e.expert_id == "fixture" for e in full)


def test_reorder_experts(tmp_path: Path) -> None:
    root = tmp_path
    current = list_experts(repo_root=root)
    ids = [e.expert_id for e in current]
    assert len(ids) >= 3
    # Reverse order
    reversed_ids = list(reversed(ids))
    reordered = reorder_experts(reversed_ids, repo_root=root)
    assert [e.expert_id for e in reordered] == reversed_ids
    assert [e.expert_id for e in list_experts(repo_root=root)] == reversed_ids
    # fixture remains last among full roster
    full = list_experts(repo_root=root, exclude_fixture=False)
    assert full[-1].expert_id == "fixture"


def test_reorder_experts_rejects_partial_and_unknown(tmp_path: Path) -> None:
    root = tmp_path
    ids = [e.expert_id for e in list_experts(repo_root=root)]
    try:
        reorder_experts(ids[:-1], repo_root=root)
        raise AssertionError("expected INVALID_EXPERT for partial order")
    except ExpertRosterError as exc:
        assert exc.code == "INVALID_EXPERT"
    try:
        reorder_experts(ids + ["no-such-expert"], repo_root=root)
        raise AssertionError("expected INVALID_EXPERT for unknown id")
    except ExpertRosterError as exc:
        assert exc.code == "INVALID_EXPERT"
    try:
        reorder_experts(["fixture"] + ids, repo_root=root)
        raise AssertionError("expected FORBIDDEN_ID for fixture")
    except ExpertRosterError as exc:
        assert exc.code == "FORBIDDEN_ID"


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
    assert found["visible"] is True

    update_expert("round-trip", {"visible": False}, repo_root=root)
    data2 = yaml.safe_load(working_roster_path(root).read_text(encoding="utf-8"))
    found2 = next(e for e in data2["experts"] if e["expert_id"] == "round-trip")
    assert found2["visible"] is False
