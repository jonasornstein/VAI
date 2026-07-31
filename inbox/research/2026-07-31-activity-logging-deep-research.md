# Inbox — activity logging research (2026-07-31)

| Field | Value |
|-------|-------|
| **AIRUP** | I (Inbox) |
| **Source** | `/deep-research` workflow (partial) |
| **Follow-up** | [pending/specs/activity-logging-v1.md](../../pending/specs/activity-logging-v1.md) |

## Summary

Industry schemas (Office 365 AuditRecord, Elastic ECS, cloud audit logs, OWASP) agree on mandatory **time**, **actor/client**, and **operation/function**, plus careful **client IP** behind proxies.

VAI today only has TRACE-LOG (decision trail), not product activity logs.

## Takeaways applied in v1 spec

1. Structured event: when / where / who / what / outcome
2. Operation name separate from event type
3. X-Forwarded-For only from trusted peers (anti-spoof)
4. RFC 3339 UTC timestamps
5. Additive to TRACE-LOG, not an extension of it

## Full report

Session workflow scratch report (if retained): deep-research run for "implement logging of user activity, ip-address, function run, and time stamp".
