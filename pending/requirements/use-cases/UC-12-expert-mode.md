# UC-12 — Expert mode (expert betslips)

| Field | Value |
|-------|-------|
| **ID** | UC-12 |
| **Status** | AWAITING_OPERATOR |
| **Version** | 1.1 |
| **AIRUP phase** | R |
| **Reviewer** | Nisse (roster/fidelity), ornstein (operator UX) |
| **Last updated** | 2026-07-15 |
| **Primary actor** | Operator |
| **Implements** | F-040–F-043 (betslip catalog) |
| **Spec** | [expert-v1.md](../../specs/expert-v1.md) |
| **Supersedes** | v1.0 pattern-template narrative (spik/halvleg/öppen generator) |

## Brief description

Operator **chooses among professional experts’ published system suggestions** (complete betslips / spelsystem) for the race day. VAI loads the selected tip into the proposal slip for review and manual ATG entry.

This is **curated tip selection**, not algorithmic pattern generation.

## Preconditions

- UC-09 complete (date/track/game context) preferred for filtering and validation.
- At least one tip file may exist under `inbox/expert-tips/` (empty catalog is allowed — empty state).

## Main success scenario

1. Race day context is set (date, track, race card when available).
2. **F-040** `list_expert_tips` returns tips matching date (and track when known) from the inbox catalog.
3. Operator **F-041** `select_expert_tip` by `tip_id`.
4. **F-042** `load_expert_betslip` yields leg → horses[]; **F-060**/**F-061** compute combinations and cost.
5. Optional **F-043** `apply_manual_override` on any leg after load.
6. Validate selections against race card when loaded (eligible horses; no scratches).
7. Return selections, cost, expert metadata, and rationale to UC-10 for draft proposal.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 2a | No tips for date/track | Empty list; UX empty state |
| 2b | Unknown or invalid tip file | Skip or surface error; do not crash list |
| 4a | Tip has horse not on race card | Abort `INVALID_HORSE` |
| 4b | Tip includes scratched horse | Abort `SCRATCHED_HORSE` |
| 5a | Override empty leg | Abort `EMPTY_LEG` |

## Functions invoked

F-040, F-041, F-042, F-043, F-060, F-061 (optional F-052 basic when distributions present)

## Special requirements

- [expert.md](../../../docs/strategies/expert.md) — roster, tip format, attribution
- [expert-v1.md](../../specs/expert-v1.md) — implementation
- Tips are for **private operator use**; always attribute source; no automated republication
- Operator pools (F-026) are **not** required for Expert load

## Non-goals (v1.1)

- Spik/halvleg/öppen pattern engine (old UC-12 v1.0)
- Live scrape of ATG/media tips
- Quantitative optimization of tips
- Automated bet placement

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.1 | 2026-07-15 | Redefined as expert betslip list/select; pending operator review |
| 1.0 | 2026-07-07 | APPROVED — pattern templates (superseded by 1.1 product intent) |
