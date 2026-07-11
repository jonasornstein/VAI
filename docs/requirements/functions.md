# ATG — System Functions Catalog

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Status** | APPROVED |
| **Reviewer** | Povl (math), ornstein (operator) |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Owner** | ornstein (M-004) |
| **Specs** | [random-v1.1](../../outbox/specs/random-v1.1.md), [local-ui-v1.1](../../outbox/specs/local-ui-v1.1.md), [atg-data-source](../../outbox/specs/atg-data-source.md) |

Concrete system functions referenced by use-case steps (`F-*`). Implementation: `src/atg/` per [src/README.md](../../src/README.md).

---

## 1. Input and storage

| ID | Name | Description | Inputs | Outputs | Use cases |
|----|------|-------------|--------|---------|-----------|
| F-001 | `store_race_card` | Save validated race card to inbox | YAML/JSON race card | Path under `inbox/race-cards/` | UC-01 |
| F-002 | `store_odds` | Save odds or probability sheet | File or structured odds | Path under `inbox/odds/` | UC-01 |
| F-003 | `store_request` | Save operator or task brief | Text/markdown file | Path under `inbox/requests/` | UC-01 |
| F-004 | `parse_race_card` | Parse race card file into leg model | File path | `RaceCard` object | UC-01, UC-10 |
| F-005 | `validate_race_card` | Check 8 legs, unique horse numbers per leg | `RaceCard` | Pass or error list | UC-01, UC-10 |
| F-006 | `fetch_atg_schedule` | Fetch V85 schedule from ATG (`schedule.py`) | — | `V85Schedule` | UC-09 |
| F-007 | `fetch_race_card_from_atg` | Build `RaceCard` from ATG game JSON (`atg_race_card.py`) | `game_id` | `RaceCard` | UC-01, UC-09 |
| F-008 | `scrape_atg_race_card` | Website fallback when API unavailable | URL context | `RaceCard` | UC-01, UC-09 |
| F-009 | `fetch_atg_odds` | Odds/probability archive; **partial:** V85 `betDistribution` for F-052 basic | `game_id` | Odds or leg distributions | UC-01, UC-11, UC-13 |
| F-029 | `extract_race_info` | Per-leg race metadata from ATG `races[]` or YAML | Race object | `RaceInfo` | UC-15 |

---

## 2. ATG schedule and UX

| ID | Name | Description | Inputs | Outputs | Use cases |
|----|------|-------------|--------|---------|-----------|
| F-027 | `resolve_next_v85_date` | Default DATUM: today if unsettled, else next future V85 | Current time, ATG schedule | ISO date | UC-09 |
| F-028 | `populate_race_day_dropdowns` | Fill BANA and SPELFORM from schedule | Schedule, DATUM | Dropdown options | UC-09 |

---

## 3. AIRUP workflow

| ID | Name | Description | Inputs | Outputs | Use cases |
|----|------|-------------|--------|---------|-----------|
| F-010 | `analyze_task_scope` | Record game, date, track, mode, reviewer | Task brief | Scope record | UC-02 |
| F-011 | `create_pending_artifact` | Write draft with `AWAITING_*` status | Content, path, status | Pending file path | UC-02, UC-10 |
| F-012 | `set_review_status` | Update status on pending artifact | Path, new status | Updated file | UC-02, UC-20 |
| F-013 | `publish_artifact` | Copy approved artifact to outbox | Pending path, outbox path | Published path | UC-02, UC-21 |
| F-014 | `log_trace_entry` | Append significant decision to TRACE-LOG | Summary, link | Log row | UC-02, UC-21, UC-30 |

---

## 4. Proposal core

| ID | Name | Description | Inputs | Outputs | Use cases |
|----|------|-------------|--------|---------|-----------|
| F-020 | `load_race_card` | Load race card for game/date/track | Identifiers | `RaceCard` | UC-10 |
| F-021 | `validate_horse_selection` | Ensure each pick exists on race card leg | Leg picks, `RaceCard` | Pass or `InvalidHorseError` | UC-10, UC-11–13 |
| F-022 | `select_game_and_mode` | Bind game (`v85`), mode, date, track | User choice | Session context | UC-10 |
| F-023 | `write_proposal_draft` | Write proposal markdown to pending | `Proposal` | `pending/proposals/.../proposal.md` | UC-10 |
| F-024 | `write_proposal_manifest` | Write YAML sidecar (mode, inputs, seed, etc.) | `Proposal` metadata | `manifest.yaml` | UC-10 |
| F-025 | `set_stake_budget` | Operator SYSTEMKOSTNAD; default 500 SEK | SEK amount | Budget in session | UC-10 |
| F-026 | `set_operator_horse_pool` | Operator marks horses per leg for model | Leg, horse toggles | Pool per leg | UC-10, UC-11–13 |

---

## 5. Random mode

| ID | Name | Description | Inputs | Outputs | Use cases |
|----|------|-------------|--------|---------|-----------|
| F-030 | `random_select_horses` | Uniform random subset per leg | `RaceCard`, leg config | Leg → horse[] | UC-11 |
| F-031 | `apply_random_constraints` | Exact-budget leg counts; frozen legs; nearest stake on failure | Pools, budget, `frozen_legs` | Selection or `BUDGET_NOT_MET` | UC-11 |
| F-032 | `set_rng_seed` | Set or record RNG seed for reproducibility | Integer or null | Seeded RNG state | UC-11 |

---

## 6. Expert mode

| ID | Name | Description | Inputs | Outputs | Use cases |
|----|------|-------------|--------|---------|-----------|
| F-040 | `load_expert_template` | Load named template from catalog | Template ID | Template definition | UC-12 |
| F-041 | `classify_legs` | Label legs spik / halvleg / öppen | `RaceCard`, template | Leg classifications | UC-12 |
| F-042 | `apply_expert_pattern` | Map classification to horse counts/picks | Classifications, `RaceCard` | Leg selections | UC-12 |
| F-043 | `apply_manual_override` | Replace leg selection with operator picks | Leg, horses[] | Updated selection | UC-12 |

---

## 7. Quantitative mode

| ID | Name | Description | Inputs | Outputs | Use cases |
|----|------|-------------|--------|---------|-----------|
| F-050 | `load_odds_input` | Load probabilities or odds per horse | File path | Odds map | UC-13 |
| F-051 | `compute_leg_probabilities` | Derive \(p_i = P(\text{winner} \in W_i)\) | Odds, candidate set | Per-leg probabilities | UC-13 |
| F-052 | `compute_hit_probabilities` | P(exactly k), P(≥k); **basic** (Hari): ATG bet-% proxy, independent legs | Leg probs or distributions, selections | Hit prob table | UC-11 (basic), UC-13 (full) |
| F-053 | `optimize_under_budget` | Maximize objective (e.g. P(≥7)) subject to cost cap | Budget, odds, `RaceCard` | Leg selections | UC-13 |
| F-054 | `run_monte_carlo` | Optional simulation of leg outcomes | Model params, N iterations | Simulated hit rates | UC-13 (Could) |

---

## 8. Cost and combinations

| ID | Name | Description | Inputs | Outputs | Use cases |
|----|------|-------------|--------|---------|-----------|
| F-060 | `count_combinations` | \(N = \prod n_i\) | Leg horse counts | Integer N | UC-14 |
| F-061 | `compute_cost_sek` | \(C = N \times s\) (0.50 SEK V85) | N, stake | SEK amount | UC-14 |
| F-062 | `format_cost_breakdown` | Human string e.g. `1×3×1×2×1×4×1×2` | Leg counts | Display string | UC-14 |

---

## 9. Review and operator

| ID | Name | Description | Inputs | Outputs | Use cases |
|----|------|-------------|--------|---------|-----------|
| F-070 | `display_proposal` | Render proposal for review (UI or markdown) | Proposal path | View | UC-20 |
| F-071 | `run_operator_checklist` | Track checklist items (legs, cost, scratches) | Proposal, race card | Checklist state | UC-20, UC-22 |
| F-072 | `approve_proposal` | Set status APPROVED | Pending path | Approved artifact | UC-20 |
| F-073 | `request_proposal_revision` | Set status AWAITING_UPDATE with notes | Pending path, notes | Updated pending | UC-20 |

---

## 10. Publish and export

| ID | Name | Description | Inputs | Outputs | Use cases |
|----|------|-------------|--------|---------|-----------|
| F-080 | `copy_to_outbox` | Publish proposal folder | Approved pending path | `outbox/proposals/...` | UC-21 |
| F-081 | `write_review_record` | Save review packet to outbox/reviews | Review content | Review file | UC-21 |
| F-090 | `export_pdf` | Generate PDF from proposal *(deferred v1.2; v1.1 uses browser print slip)* | Proposal path | PDF file | UC-23 |
| F-091 | `open_atg_link` | Open atg.se/v85 (browser; no automation) | — | URL opened | UC-22, UC-23 |
| F-092 | `toggle_display_theme` | Switch light/dark UI theme | Theme choice | UI state | UC-23 (mockup) |

---

## 11. Documentation maintenance

| ID | Name | Description | Inputs | Outputs | Use cases |
|----|------|-------------|--------|---------|-----------|
| F-100 | `draft_betting_rules` | Create/update pending research | Sources | `pending/research/` | UC-30 |
| F-101 | `promote_betting_rules` | Move approved rules to docs/betting | Approved draft | `docs/betting/` | UC-30 |
| F-102 | `draft_strategy_spec` | Create/update strategy spec | Requirements | `pending/specs/` or docs | UC-31 |
| F-103 | `promote_strategy_spec` | Publish approved strategy doc | Approved draft | `docs/strategies/` | UC-31 |

---

## 12. Implementation priority

| Priority | Functions | Notes |
|----------|-----------|-------|
| **Shipped (v1.0 — CLI)** | F-001, F-004–005, F-020–021, F-023–026, F-030–032, F-060–062 | Manual YAML race cards; `python -m atg random` |
| **Shipped (v1.1 — local UI + ATG)** | F-006–007, F-025–028, F-052 (basic), F-071, F-091 | `python -m atg serve`; see [local-ui-v1.1](../../outbox/specs/local-ui-v1.1.md) |
| **Shipped (v1.2 — race info)** | F-029 | Leg header metadata; [race-info-v1](../../outbox/specs/race-info-v1.md) |
| **Partial** | F-009 | V85 `betDistribution` only; no `inbox/odds/` archive |
| **UX / mockup only** | F-070, F-090, F-092 | Print slip (not PDF export); theme toggle in mockup variants |
| **Agent / manual (AIRUP)** | F-002–003, F-010–014, F-072–073, F-080–081 | Skills and operator workflow; not automated in `src/` |
| **Deferred** | F-008, F-040–043, F-050–051, F-053–054 | Scrape fallback; expert; full quant model |
| **Could (v1.2+)** | Reduced-stake cost variants (UC-14 §3a), F-054, F-090 (PDF) | α ∈ {0.30, 0.50, 0.70} |

### Module map (shipped)

| Module | Functions |
|--------|-----------|
| `io/race_card.py` | F-004, F-005 |
| `io/race_card_json.py` | F-020 (YAML id lookup) |
| `io/pools.py` | F-026 |
| `io/proposal.py` | F-023, F-071 (markdown checklist) |
| `schedule.py` | F-006, F-027, F-028 |
| `atg_race_card.py` | F-007, F-009 (partial), F-029 |
| `strategies/random.py` | F-030–032, F-031 |
| `cost.py` | F-060–062 |
| `hit_summary.py` | F-052 (basic) |
| `server.py` | Local UI API routes |

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.1 | 2026-07-08 | F-029 race info shipped (UC-15) |
| 1.0 | 2026-07-07 | APPROVED — canonical F-* catalog; shipped vs deferred aligned with v1.1 |
| 0.4 | 2026-07-07 | v1.1 shipped set: ATG fetch, schedule UX, F-052 basic, F-071; module map |
| 0.3 | 2026-07-07 | v1 shipped set vs deferred; scope-lock alignment |
| 0.2 | 2026-07-06 | ATG fetch F-006–009; UX F-025–028; SYSTEMKOSTNAD default 500 |
| 0.1 | 2026-07-06 | Initial catalog; 30 functions across 10 domains |