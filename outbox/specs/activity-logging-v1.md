# Activity logging — v1 implementation spec

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Status** | **APPROVED** |
| **AIRUP phase** | P |
| **Reviewer** | Povl (schema/ops), ornstein (deploy/usability) |
| **Author** | Assistant (from deep-research 2026-07-31) |
| **Approved** | 2026-07-31 — Povl, ornstein |
| **Last updated** | 2026-07-31 |
| **Related** | [local-ui-v1.1](./local-ui-v1.1.md), [functions.md](../../docs/requirements/functions.md) F-014 (distinct), [inbox research](../../inbox/research/2026-07-31-activity-logging-deep-research.md) |
| **Implements** | F-110 `log_activity_event`, F-111 `resolve_client_ip` |
| **Review** | [REVIEW_activity-logging-v1.md](../reviews/REVIEW_activity-logging-v1.md) |

---

## 1. Purpose

Record **runtime user activity** for the local UI HTTP server: **when**, **who/where** (client IP), **what** (operation / function run), and **outcome**.

This is **not** AIRUP `TRACE-LOG` / F-014 (human decision audit). Product activity logs are additive.

---

## 2. Resolved decisions

| ID | Topic | Decision |
|----|-------|----------|
| AL-001 | Scope v1 | HTTP server only (`python -m vai serve`); CLI generate not required |
| AL-002 | Format | JSON Lines (one JSON object per line), UTF-8 |
| AL-003 | Timestamp | RFC 3339 UTC with milliseconds, e.g. `2026-07-31T14:22:01.123Z` |
| AL-004 | Client IP | Socket peer + trusted-proxy resolution of `X-Forwarded-For` |
| AL-005 | Trusted proxy default | `trusted_proxy_hops=1` (matches nginx → app on loopback) |
| AL-006 | Function identity | Stable `operation` string (not Python qualname with args) |
| AL-007 | Actor | Optional; null until auth exists (`actor` field reserved) |
| AL-008 | Destination | Default `logs/activity.jsonl` under repo root; override via CLI/env |
| AL-009 | Secrets | Never log request bodies, seeds, Authorization, cookies, or tip payloads |
| AL-010 | vs TRACE-LOG | No automatic TRACE-LOG rows from activity events |
| AL-011 | Disable | `--activity-log none` or empty path disables file logging |

---

## 3. Event schema

Each line is one object:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ts` | string | yes | Event time, RFC 3339 UTC (`…Z`) |
| `event_id` | string | yes | UUID4 |
| `event_type` | string | yes | `access` \| `change` \| `generation` \| `error` |
| `operation` | string | yes | Stable name of action (see §4) |
| `method` | string | yes | HTTP method |
| `path` | string | yes | Request path (no query string) |
| `status` | int | yes | HTTP status code |
| `outcome` | string | yes | `success` if status &lt; 400, else `failure` |
| `client_ip` | string \| null | yes | Best-effort end-client IP after trust rules |
| `peer_ip` | string \| null | yes | Direct TCP peer (`self.client_address[0]`) |
| `function` | string \| null | no | Handler label, e.g. `_handle_generate_random` |
| `actor` | string \| null | no | Reserved; null in v1 |
| `user_agent` | string \| null | no | Truncated User-Agent (max 256 chars) |

### Example

```json
{"ts":"2026-07-31T12:00:00.123Z","event_id":"a1b2c3d4-e5f6-7890-abcd-ef1234567890","event_type":"generation","operation":"generate_random","method":"POST","path":"/api/v1/generate/random","status":200,"outcome":"success","client_ip":"203.0.113.10","peer_ip":"127.0.0.1","function":"_handle_generate_random","actor":null,"user_agent":"Mozilla/5.0 ..."}
```

---

## 4. Operations catalog

| operation | Methods | Path pattern | event_type |
|-----------|---------|--------------|------------|
| `serve_index` | GET, HEAD | `/`, `/index.html` | access |
| `serve_mockup` | GET, HEAD | `/mockup/*` | access |
| `get_schedule_v85` | GET | `/api/v1/schedule/v85` | access |
| `list_race_cards` | GET | `/api/v1/race-cards` | access |
| `get_race_card` | GET | `/api/v1/race-cards/{id}` | access |
| `list_expert_tips` | GET | `/api/v1/expert-tips` | access |
| `get_expert_tip` | GET | `/api/v1/expert-tips/{id}` | access |
| `save_expert_tip` | POST, PUT | `/api/v1/expert-tips` | change |
| `delete_expert_tip` | DELETE | `/api/v1/expert-tips` or `…/{id}` | change |
| `list_experts` | GET | `/api/v1/experts` | access |
| `get_expert` | GET | `/api/v1/experts/{id}` | access |
| `add_expert` | POST | `/api/v1/experts` | change |
| `update_expert` | PUT | `/api/v1/experts/{id}` | change |
| `delete_expert` | DELETE | `/api/v1/experts/{id}` | change |
| `reset_experts` | POST | `/api/v1/experts/reset` | change |
| `set_experts_visibility` | PUT | `/api/v1/experts/visibility` | change |
| `reorder_experts` | PUT | `/api/v1/experts/reorder` | change |
| `generate_random` | POST | `/api/v1/generate/random` | generation |
| `generate_expert` | POST | `/api/v1/generate/expert` | generation |
| `cors_preflight` | OPTIONS | any | access |
| `not_found` | * | unmatched | error |
| `http_request` | * | fallback | access |

---

## 5. Client IP resolution (F-111)

Production path: browser → **nginx** (`X-Real-IP`, `X-Forwarded-For`) → app on `127.0.0.1:8765`.

Algorithm (Express-style `trust proxy N`):

1. `peer_ip` = TCP peer address.
2. If peer is **not** trusted (loopback or `--trusted-proxies`) **or** `trusted_proxy_hops == 0` → `client_ip = peer_ip` (ignore XFF — anti-spoof).
3. Parse XFF as comma-separated IPs; build chain = XFF entries + peer (rightmost).
4. Skip `N = trusted_proxy_hops` addresses from the right; the next address left is `client_ip`.
5. If the chain is shorter than `N+1`, fall back to `peer_ip`.
6. Default `N = 1` (single nginx on loopback): XFF `203.0.113.10`, peer `127.0.0.1` → client `203.0.113.10`.

Do **not** treat leftmost XFF as authoritative without a trusted peer.

---

## 6. Configuration

| Source | Setting | Default |
|--------|---------|---------|
| CLI | `--activity-log PATH` | `{repo}/logs/activity.jsonl` |
| CLI | `--activity-log none` | disabled |
| CLI | `--trusted-proxy-hops N` | `1` |
| CLI | `--trusted-proxies ip,ip` | empty (loopback always trusted for XFF) |
| Env | `VAI_ACTIVITY_LOG` | same as CLI if CLI omitted |
| Env | `VAI_TRUSTED_PROXY_HOPS` | optional int |

On `serve` start, print log destination (or “activity log disabled”).

**Viewing:** no in-app UI — operators use `tail -f logs/activity.jsonl` (or path under service `WorkingDirectory` on deploy).

---

## 7. Implementation map

| Module | Responsibility |
|--------|----------------|
| `src/vai/activity_log.py` | Schema build, IP resolve, JSONL writer (thread-safe) — F-110, F-111 |
| `src/vai/server.py` | Emit event after response (`log_request`) |
| `src/vai/cli.py` | `serve` flags for log path and proxy trust |
| `tests/test_activity_log.py` | Unit tests for schema + IP |
| `tests/test_server.py` | Integration: request produces a log line |

Default access `log_message` remains quiet; structured activity log replaces it for observability.

---

## 8. Privacy and ops notes

- **IP addresses** may be personal data; retain only as needed for ops/security. v1 has **no rotation** — operators may truncate/rotate `logs/activity.jsonl` externally.
- File is gitignored (`logs/`).
- Failures writing the log must **not** break the HTTP response (best-effort; stderr warning once per failure class optional).

---

## 9. Out of scope (v1)

- Authentication / real `actor` identity
- Request/response body logging
- Shipping logs to Elastic/Cloud
- CLI random/expert activity events
- Automatic TRACE-LOG integration
- GDPR retention UI

---

## 10. Acceptance criteria

- [x] Spec approved and published to `outbox/specs/`
- [x] Each completed HTTP response (via send path) may emit one JSONL event with `ts`, `client_ip`/`peer_ip`, `operation`, `status`
- [x] Behind mock nginx headers with trusted peer, `client_ip` reflects original client, not `127.0.0.1` alone
- [x] Untrusted peer cannot spoof `client_ip` via XFF
- [x] Bodies/seeds not present in log lines
- [x] Unit + server tests pass
- [x] `logs/` gitignored

---

## 11. Review checklist (Povl / ornstein)

- [x] Field set sufficient for incident review
- [x] Trusted-proxy default safe for Hetzner + local nginx
- [x] No PII beyond IP/UA acceptable for private operator deploy
- [x] Operation catalog complete for current API surface

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-31 | **APPROVED** — Povl + ornstein; published to outbox; F-110/F-111 catalogued |
| 0.1 | 2026-07-31 | Initial draft from deep-research; implement alongside |
