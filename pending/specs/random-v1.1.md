# Random mode (Hari) — v1.1 implementation spec

| Field | Value |
|-------|-------|
| **Version** | 0.1 |
| **Status** | APPROVED |
| **AIRUP phase** | R |
| **Reviewer** | Povl |
| **Approved** | 2026-07-07 · Povl |
| **Author** | Assistant (ornstein direction 2026-07-07) |
| **Last updated** | 2026-07-07 |
| **Supersedes** | [random-v1.md](./random-v1.md) algorithm §5 (greedy shrink) |
| **Implements** | UC-11 extensions, F-030–F-032, F-052 (basic), nearest stake |

---

## 1. Purpose

Document the **shipped** Hari (random) generator and local UI behaviour as of v1.1. This spec replaces the v1 **draw-then-shrink** model with **exact-budget fill** from operator marks.

---

## 2. Resolved decisions (v1.1)

| ID | Topic | **v1.1 decision** |
|----|-------|-------------------|
| SL-101 | Budget target | **Exact** SYSTEMKOSTNAD: `cost_sek == stake_budget_sek` (ε = 0.001 SEK) |
| SL-102 | Empty operator marks | Allowed — leg min count = 1; random fills from full eligible field |
| SL-103 | Marked horses | **Locked** — always included in final selection |
| SL-104 | Frozen legs | Operator may freeze legs; frozen leg uses **only** marked horses (min = max = mark count) |
| SL-105 | Budget not achievable | Return `BUDGET_NOT_MET` with `suggested_stake_sek` / `suggested_combinations` (nearest valid stake) |
| SL-106 | UX mode name | Tab label **Hari**; API mode remains `random` |
| SL-107 | Hit summary | **F-052 basic** when ATG `betDistribution` available per start |

**Unchanged from v1:** SL-001 (max = eligible field per leg), SL-003 (no field-size weighting), seed reproducibility (F-032).

---

## 3. Algorithm (exact-budget fill)

1. Validate inputs (8 legs, pools keys 1..8, picks ⊆ race card, budget multiple of 0.50 SEK).
2. `target_combinations = stake_budget_sek / 0.50`.
3. Per leg, compute `min_counts` / `max_counts`:
   - Frozen: `min = max = |operator_picks|`
   - Else: `min = max(1, |operator_picks|)`, `max = |eligible horses|`
4. Find all 8-tuples of leg counts whose product equals `target_combinations` within min/max bounds.
5. If none: compute **nearest** achievable combination count; return `BUDGET_NOT_MET` with suggestion.
6. Choose one count vector uniformly at random (seeded RNG).
7. Per leg: start with locked picks; sample remaining horses to reach leg count.
8. Emit `RandomResult` with `cost_sek == stake_budget_sek`.

`shrink_steps_used` in manifest = total **fill** steps (horses added beyond operator minimum), not shrink.

---

## 4. API extensions (local UI)

### POST `/api/v1/generate/random`

Optional body field:

```json
{ "frozen_legs": [2, 4] }
```

Error `400` may include:

```json
{
  "error": {
    "code": "BUDGET_NOT_MET",
    "suggested_stake_sek": 19845.0,
    "suggested_combinations": 39690,
    "hint": "Nearest achievable SYSTEMKOSTNAD is 19845.00 SEK (39690 rows)"
  }
}
```

Success `200` may include optional `hit_summary` when leg distributions exist (F-052).

### GET `/api/v1/race-cards/{atg_game_id}`

ATG-sourced cards may include `leg_distributions`: leg → horse → fraction (sum of V85 bet % for selected horses used in hit model).

---

## 5. Operator UX (mockup)

| Control | Behaviour |
|---------|-----------|
| Horse click | Toggle operator mark (orange frame) |
| Generera system | POST generate; on `BUDGET_NOT_MET` offer nearest stake confirm |
| Frys avd. | Leg excluded from random fill; marks required |
| Seed | Optional reproducibility |
| Träffsannolikhet | Shown when `leg_distributions` present; else placeholder |
| Rationale header | **Hari** (not Random) |

---

## 6. F-052 basic hit summary

When `leg_distributions` available:

- Per leg: \(p_i = \min(1, \sum_{h \in selection_i} distribution_{i,h})\)
- Independent-leg assumption: compute P(exactly k) for k = 0..8 via DP
- Display P(8), P(≥7), P(≥6), P(≥5) in sidebar

**Limitation:** Uses ATG pool % as proxy; not a quantitative model. Full F-052 remains with UC-13.

---

## 7. Deferred (v1.2+)

| Item | Ref | Notes |
|------|-----|-------|
| Reduced-stake systems | UC-14 §3a | α ∈ {0.30, 0.50, 0.70}; separate cost formula |
| Field-size weighting | SL-003 | Still no |
| Expert / Quant modes | UC-12, UC-13 | UX tabs disabled |
| Other games (V86, V64) | Phase 5 | V75 discontinued at ATG — not planned |

---

## 8. Tests

| Test | Coverage |
|------|----------|
| `test_empty_picks_hit_exact_budget` | No marks → exact budget |
| `test_frozen_leg_*` | Freeze semantics |
| `test_all_horses_one_leg_suggests_nearest_stake` | Suggestion + retry |
| `test_hit_summary_*` | F-052 when distributions present |
| `scripts/verify_suggested_stake_leg6.py` | E2E stake prompt |

---

## 9. Promotion checklist (on APPROVED)

| Artifact | Action |
|----------|--------|
| [random.md](../../docs/strategies/random.md) | Bump to v0.3; exact-fill algorithm |
| [UC-11](../../docs/requirements/use-cases/UC-11-random-mode.md) | Update main scenario |
| [ux-workflow.md](../../docs/requirements/ux-workflow.md) | Hari, ATG fetch, nearest stake |
| [local-ui-v1.1.md](./local-ui-v1.1.md) | API + UX deltas |
| `outbox/specs/random-v1.1.md` | Copy on publish |
| [TRACE-LOG.md](../../docs/TRACE-LOG.md) | Log Povl approval |

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-07-07 | Initial v1.1 — exact budget, frozen legs, nearest stake, F-052 basic |