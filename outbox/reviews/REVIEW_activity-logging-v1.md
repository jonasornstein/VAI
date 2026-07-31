# Review — Activity logging v1

| Field | Value |
|-------|-------|
| **Artifact** | [activity-logging-v1.md](../specs/activity-logging-v1.md) |
| **Reviewer** | Povl (schema/ops), ornstein (deploy/usability) |
| **Date** | 2026-07-31 |
| **Verdict** | **APPROVED** |
| **Version** | 1.0 |

---

## Findings

- [x] Structured JSONL events: `ts`, `client_ip`/`peer_ip`, `operation`/`function`, `status`/`outcome`
- [x] Distinct from TRACE-LOG / F-014 (product runtime log, not decision trail)
- [x] Trusted-proxy XFF resolution (loopback + hops default 1) — anti-spoof
- [x] No bodies, seeds, or secrets in log lines
- [x] Default path `logs/activity.jsonl` (gitignored); CLI/env overrides; disable with `none`
- [x] Implemented in `src/vai/activity_log.py` + `server.py` / `cli.py`; tests pass
- [x] Inbox research retained: [2026-07-31-activity-logging-deep-research.md](../../inbox/research/2026-07-31-activity-logging-deep-research.md)

## Notes

Canonical published path: `outbox/specs/activity-logging-v1.md`. Functions: F-110, F-111 in [functions.md](../../docs/requirements/functions.md).
