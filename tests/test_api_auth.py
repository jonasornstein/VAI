import json
import logging
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from vai.api_auth import is_protected
from test_server import TEST_API_KEY, _start_test_server


def _req(base: str, method: str, path: str, key: str | None = None, body: dict | None = None):
    headers = {"Content-Type": "application/json"}
    if key is not None:
        headers["X-API-Key"] = key
    data = json.dumps(body or {}).encode() if method != "DELETE" else None
    try:
        with urlopen(Request(base + path, data=data, headers=headers, method=method)) as r:
            return r.status, json.loads(r.read() or b"{}")
    except HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


WRITES = [
    ("POST", "/api/v1/betslips"),
    ("POST", "/api/v1/betslips/delete"),
    ("DELETE", "/api/v1/betslips/x.yaml"),
    ("POST", "/api/v1/expert-tips"),
    ("PUT", "/api/v1/expert-tips"),
    ("DELETE", "/api/v1/expert-tips/abc"),
    ("POST", "/api/v1/experts"),
    ("POST", "/api/v1/experts/reset"),
    ("PUT", "/api/v1/experts/visibility"),
    ("PUT", "/api/v1/experts/reorder"),
    ("PUT", "/api/v1/experts/someone"),
    ("DELETE", "/api/v1/experts/someone"),
]


@pytest.fixture
def server():
    srv, base = _start_test_server()
    yield base
    srv.shutdown()
    srv.server_close()


@pytest.mark.parametrize("method,path", WRITES)
def test_write_without_key_is_401(server, method, path):
    status, body = _req(server, method, path)
    assert status == 401
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.parametrize("method,path", WRITES)
def test_write_with_wrong_key_is_401(server, method, path):
    status, _ = _req(server, method, path, key="wrong")
    assert status == 401


@pytest.mark.parametrize("method,path", WRITES)
def test_write_fails_closed_without_server_key(server, monkeypatch, method, path):
    monkeypatch.delenv("VAI_API_KEY", raising=False)
    status, body = _req(server, method, path, key=TEST_API_KEY)
    assert status == 503
    assert body["error"]["code"] == "API_KEY_NOT_CONFIGURED"


def test_correct_key_passes_gate(server):
    # Invalid payload: gate passes, handler rejects with 4xx other than 401/503.
    status, _ = _req(server, "POST", "/api/v1/betslips", key=TEST_API_KEY, body={})
    assert status not in (401, 503)


def test_read_endpoints_unaffected(server, monkeypatch):
    monkeypatch.delenv("VAI_API_KEY", raising=False)
    with urlopen(server + "/api/v1/experts") as r:
        assert r.status == 200


def test_compute_only_posts_unprotected():
    assert not is_protected("POST", "/api/v1/generate/random")
    assert not is_protected("POST", "/api/v1/generate/expert")
    assert not is_protected("POST", "/api/v1/betslips/parse")
    assert not is_protected("GET", "/api/v1/betslips")
    assert is_protected("POST", "/api/v1/betslips")


def test_log_never_contains_key(server, caplog):
    caplog.set_level(logging.INFO, logger="vai.api_auth")
    _req(server, "PUT", "/api/v1/experts/reorder", key=TEST_API_KEY, body={})
    _req(server, "PUT", "/api/v1/experts/reorder", key="bad-secret-xyz")
    text = caplog.text
    assert "write ok method=PUT path=/api/v1/experts/reorder ip=127.0.0.1" in text
    assert "denied(invalid)" in text
    assert TEST_API_KEY not in text and "bad-secret-xyz" not in text
