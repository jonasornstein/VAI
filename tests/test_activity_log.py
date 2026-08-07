"""Unit tests for activity logging (F-110 / F-111)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from vai.activity_log import (
    ActivityLogger,
    build_activity_event,
    classify_request,
    parse_activity_log_path,
    parse_x_forwarded_for,
    resolve_client_ip,
    utc_now_rfc3339,
)


def test_utc_now_rfc3339_format() -> None:
    fixed = datetime(2026, 7, 31, 12, 0, 0, 123456, tzinfo=timezone.utc)
    assert utc_now_rfc3339(when=fixed) == "2026-07-31T12:00:00.123Z"


def test_parse_x_forwarded_for() -> None:
    assert parse_x_forwarded_for("203.0.113.10, 198.51.100.1") == [
        "203.0.113.10",
        "198.51.100.1",
    ]
    assert parse_x_forwarded_for(None) == []
    assert parse_x_forwarded_for(" not-an-ip , 1.2.3.4 ") == ["1.2.3.4"]


def test_resolve_client_ip_trusted_peer_one_hop() -> None:
    # nginx on loopback: XFF = client, peer = 127.0.0.1
    assert (
        resolve_client_ip(
            "127.0.0.1",
            "203.0.113.10",
            trusted_proxy_hops=1,
        )
        == "203.0.113.10"
    )


def test_resolve_client_ip_multi_proxy_chain() -> None:
    # XFF client, intermediate; peer = our nginx. hops=1 → who connected to nginx
    assert (
        resolve_client_ip(
            "127.0.0.1",
            "203.0.113.10, 198.51.100.1",
            trusted_proxy_hops=1,
        )
        == "198.51.100.1"
    )
    # hops=2 → trust nginx + one more hop → original client
    assert (
        resolve_client_ip(
            "127.0.0.1",
            "203.0.113.10, 198.51.100.1",
            trusted_proxy_hops=2,
        )
        == "203.0.113.10"
    )


def test_resolve_client_ip_untrusted_peer_ignores_xff() -> None:
    # Spoof attempt: remote client sets XFF; peer is not trusted
    assert (
        resolve_client_ip(
            "198.51.100.50",
            "1.2.3.4",
            trusted_proxy_hops=1,
        )
        == "198.51.100.50"
    )


def test_resolve_client_ip_explicit_trusted_proxy() -> None:
    trusted = frozenset({"10.0.0.1"})
    assert (
        resolve_client_ip(
            "10.0.0.1",
            "203.0.113.99",
            trusted_proxy_hops=1,
            trusted_proxies=trusted,
        )
        == "203.0.113.99"
    )


def test_resolve_client_ip_zero_hops_uses_peer() -> None:
    assert (
        resolve_client_ip(
            "127.0.0.1",
            "203.0.113.10",
            trusted_proxy_hops=0,
        )
        == "127.0.0.1"
    )


def test_classify_generate_random() -> None:
    op, etype, fn = classify_request("POST", "/api/v1/generate/random")
    assert op == "generate_random"
    assert etype == "generation"
    assert fn == "_handle_generate_random"


def test_classify_serve_stats_and_activity_log() -> None:
    op, etype, fn = classify_request("GET", "/vai-stats.html")
    assert op == "serve_stats"
    assert etype == "access"
    assert fn == "_serve_file"
    op2, etype2, fn2 = classify_request("GET", "/activity.jsonl")
    assert op2 == "serve_activity_log"
    assert etype2 == "access"
    assert fn2 == "_serve_activity_jsonl"


def test_classify_race_card() -> None:
    op, etype, _ = classify_request("GET", "/api/v1/race-cards/V85_2026-07-11_31_5")
    assert op == "get_race_card"
    assert etype == "access"


def test_build_activity_event_fields() -> None:
    event = build_activity_event(
        method="POST",
        path="/api/v1/generate/random?x=1",
        status=200,
        peer_ip="127.0.0.1",
        x_forwarded_for="203.0.113.10",
        user_agent="TestAgent/1.0",
        event_id="00000000-0000-0000-0000-000000000001",
        when=datetime(2026, 7, 31, 12, 0, 0, 0, tzinfo=timezone.utc),
    )
    d = event.to_dict()
    assert d["ts"] == "2026-07-31T12:00:00.000Z"
    assert d["event_id"] == "00000000-0000-0000-0000-000000000001"
    assert d["operation"] == "generate_random"
    assert d["event_type"] == "generation"
    assert d["method"] == "POST"
    assert d["path"] == "/api/v1/generate/random"
    assert d["status"] == 200
    assert d["outcome"] == "success"
    assert d["client_ip"] == "203.0.113.10"
    assert d["peer_ip"] == "127.0.0.1"
    assert d["function"] == "_handle_generate_random"
    assert d["actor"] is None
    assert d["user_agent"] == "TestAgent/1.0"
    # No body / secrets keys
    assert "body" not in d
    assert "seed" not in d


def test_activity_logger_jsonl(tmp_path: Path) -> None:
    log_file = tmp_path / "activity.jsonl"
    logger = ActivityLogger(log_file)
    event = build_activity_event(
        method="GET",
        path="/api/v1/experts",
        status=200,
        peer_ip="127.0.0.1",
        event_id="11111111-1111-1111-1111-111111111111",
        when=datetime(2026, 7, 31, 15, 0, 0, 0, tzinfo=timezone.utc),
    )
    logger.emit(event)
    logger.emit(event)
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    row = json.loads(lines[0])
    assert row["operation"] == "list_experts"
    assert row["status"] == 200


def test_activity_logger_disabled() -> None:
    logger = ActivityLogger(None)
    assert not logger.enabled
    event = build_activity_event(
        method="GET",
        path="/",
        status=200,
        peer_ip="127.0.0.1",
    )
    logger.emit(event)  # no-op


def test_parse_activity_log_path(tmp_path: Path) -> None:
    default = parse_activity_log_path(None, repo_root=tmp_path)
    assert default == (tmp_path / "logs" / "activity.jsonl").resolve()
    assert parse_activity_log_path("none", repo_root=tmp_path) is None
    assert parse_activity_log_path("off", repo_root=tmp_path) is None
    custom = parse_activity_log_path("var/act.jsonl", repo_root=tmp_path)
    assert custom == (tmp_path / "var" / "act.jsonl").resolve()
