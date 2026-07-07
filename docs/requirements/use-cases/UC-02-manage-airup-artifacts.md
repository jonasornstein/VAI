# UC-02 — Manage AIRUP artifacts

| Field | Value |
|-------|-------|
| **ID** | UC-02 |
| **Status** | DRAFT |
| **Primary actor** | Agent |
| **Preconditions** | Task received; AIRUP methodology active |

## Brief description

Execute Analyze → Inbox → Review ⇄ Update → Publish for any artifact type.

## Main success scenario

1. Agent invokes **F-010** `analyze_task_scope` — records game, date, track, mode, reviewer.
2. Agent ensures raw inputs land in `inbox/` (UC-01) before drafting.
3. Agent invokes **F-011** `create_pending_artifact` with status `AWAITING_NISSE` | `AWAITING_POVL` | `AWAITING_OPERATOR` | `AWAITING_JONTE`.
4. Reviewer examines pending artifact (use case specific: UC-20, UC-30, etc.).
5. If changes needed: agent invokes **F-073** or manual edit; loop to step 4.
6. On approval: agent invokes **F-012** `set_review_status` → `APPROVED`.
7. Agent invokes **F-013** `publish_artifact` to `outbox/` (or promote to `docs/` for rules/specs).
8. If significant: agent invokes **F-014** `log_trace_entry` in [TRACE-LOG.md](../../TRACE-LOG.md).

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 3a | Betting rules draft | Status `AWAITING_NISSE`; path `pending/research/` |
| 3b | Quant spec or quant proposal | Status `AWAITING_POVL` |
| 3c | Race-day proposal | Status `AWAITING_OPERATOR` |
| 3d | Use case / vision change | Status `AWAITING_JONTE`; path `pending/requirements/` |
| 7a | Publish blocked | Status ≠ APPROVED — AIRUP gate enforced |

## Functions invoked

F-010, F-011, F-012, F-013, F-014, F-073

## Special requirements

- [AIRUP.md](../../AIRUP.md) v1.1
- [SUP-F-006](../supplementary-specification.md#1-functionality-cross-cutting), [SUP-F-007](../supplementary-specification.md#1-functionality-cross-cutting)