from vai.io.experts_roster import list_experts, load_experts_roster


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
