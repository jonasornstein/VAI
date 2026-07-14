# VAI — Supplementary Specification

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Status** | APPROVED |
| **Reviewer** | ornstein (operator), Povl (constraints), Nisse (compliance) |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Owner** | ornstein (M-004) |
| **Specs** | [local-ui-v1.1](../../outbox/specs/local-ui-v1.1.md), [atg-data-source](../../outbox/specs/atg-data-source.md), [ux-workflow](./ux-workflow.md) |
| **Supersedes** | SRS §4–§5, §7 (non-functional and cross-cutting) |

Requirements that do not fit a single use-case narrative. Organized with the **FURPS+** model (RUP).

---

## 1. Functionality (cross-cutting)

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| SUP-F-001 | System SHALL support game parameter with default `v85` | Must | See UC-10 |
| SUP-F-002 | System SHALL reject horse numbers not on the race card | Must | Validation in UC-10 |
| SUP-F-003 | V85 proposals SHALL have exactly 8 legs | Must | [v85.md](../betting/v85.md) |
| SUP-F-004 | Proposal manifest SHALL record mode, timestamp, and inputs | Must | AIRUP traceability |
| SUP-F-005 | Consolation payout rules SHALL be documented; calculation optional in v1 | Should | Nisse / Povl |
| SUP-F-006 | All artifacts SHALL follow [AIRUP](../AIRUP.md) | Must | UC-02 |
| SUP-F-007 | Significant decisions SHALL be logged in [TRACE-LOG.md](../TRACE-LOG.md) | Should | UC-02 |
| SUP-F-008 | Race card SHALL be collected automatically from ATG website or API when available | Must | UC-01, UC-09 |
| SUP-F-009 | Operator MAY mark horses per leg; unmarked legs filled randomly (Hari v1.1) | Must | UC-10, F-026 |
| SUP-F-010 | Model SHALL produce betting slip and cost; hit summary when data available (F-052 basic Hari; full UC-13 deferred) | Must | UC-10–13 |
| SUP-F-011 | SYSTEMKOSTNAD (stake budget) SHALL be operator-entered; default **500 SEK** | Must | F-025 |

**Legacy mapping:** FR-010–016, FR-050–051, FR-000, FR-001d.

---

## 2. Usability

| ID | Requirement | Priority | Owner |
|----|-------------|----------|-------|
| SUP-U-001 | Operator SHALL read a proposal in under 2 minutes | Must | Kricke/ornstein |
| SUP-U-002 | Leg-by-leg horse numbers SHALL be unambiguous for ATG entry | Must | Kricke/ornstein |
| SUP-U-003 | Total cost and row count SHALL be visible before publish | Must | Kricke/ornstein |
| SUP-U-004 | Proposal UI SHALL support light and dark display modes | Should | Mockup variants; theme toggle F-092 |
| SUP-U-005 | Pre-entry checklist SHALL remind operator of scratches and reserves | Should | F-071 wired in local UI v1.1 |
| SUP-U-006 | On DATUM change, BANA and SPELFORM dropdowns SHALL repopulate from ATG schedule | Must | UC-09 |
| SUP-U-007 | Default DATUM SHALL be next relevant V85: today if unsettled, else next future round | Must | F-027 |
| SUP-U-008 | SYSTEMKOSTNAD input SHALL be visible in sidebar; default 500 SEK | Must | UX mockup |

**Legacy mapping:** NFR-001; [ux-workflow.md](./ux-workflow.md); mockups in `outbox/mockups/`.

---

## 3. Reliability

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| SUP-R-001 | When ATG unreachable, system SHALL fall back to manual YAML or cached card; stale cache flagged | Should | UC-09; disk cache v1.2 |
| SUP-R-005 | Fetched race cards SHALL be cached under `inbox/race-cards/` for replay | Must | F-001 after F-007 |
| SUP-R-002 | Random mode SHOULD support seedable RNG for reproducibility | Should | UC-11 |
| SUP-R-003 | Cost formula SHALL match ATG: ∏(horses per leg) × min stake | Must | Verified in quantitative.md |
| SUP-R-004 | Published artifacts SHALL be immutable copies in `outbox/` | Should | AIRUP **P** phase |

**Legacy mapping:** NFR-002, FR-022.

---

## 4. Performance

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| SUP-P-001 | Single V85 proposal generation SHOULD complete in &lt; 5 s on operator hardware | Should | v1.1 try-outs meet target; no formal benchmark |
| SUP-P-002 | Monte Carlo runs SHOULD be configurable (iterations cap) | Should | Povl — UC-13 |

*v1 has no hard latency SLA beyond operator tolerance on race day.*

---

## 5. Supportability

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| SUP-S-001 | Code SHALL be structured to add games without rewriting core | Must | Modular `src/` |
| SUP-S-002 | Grok agents SHALL load context from `AGENTS.md` and `.grok/rules/` | Must | Agent workflow |
| SUP-S-003 | Skills `/airup`, `/airup-review`, `/generate-proposal`, `/v85-system` SHALL be available | Must | `.grok/skills/` |
| SUP-S-004 | Major docs SHALL include version tables and change logs | Should | Documentation standard |
| SUP-S-005 | Requirements SHALL use RUP trilogy; legacy SRS is index only | Must | This restructure |

**Legacy mapping:** NFR-003–005, FR-003.

---

## 6. + Design constraints

| ID | Constraint | Rationale |
|----|------------|-----------|
| SUP-D-001 | Python for quantitative work (Monte Carlo, odds) | Povl / implementation |
| SUP-D-002 | Markdown artifacts for proposals and docs | Human-readable, git-friendly |
| SUP-D-003 | Shared V85 leg model across all modes | One cost/combination engine |
| SUP-D-004 | Strategies are modular plugins under `src/` | FR game extensibility |

---

## 7. + Implementation constraints

| ID | Constraint | Rationale |
|----|------------|-----------|
| SUP-I-001 | No automated bet placement or ATG login | [VISION](../VISION.md) NG-001 |
| SUP-I-002 | No guaranteed-profit or financial-advice claims | NG-002 |
| SUP-I-003 | Implementation specs start in `pending/specs/` before `src/` | AIRUP gate |
| SUP-I-004 | Use-case IDs (`UC-*`) SHALL appear in spec headers | Traceability |
| SUP-I-005 | ATG integration is **read-only** (schedule, race card, odds); no bet placement or login automation | [VISION](../VISION.md) NG-001 |

---

## 8. + Interface requirements

| Interface | Direction | Description | v1 |
|-----------|-----------|-------------|-----|
| **ATG website** | Outbound (human) | Manual bet entry at [atg.se/v85](https://www.atg.se/v85) | Yes |
| **ATG website / API** | Inbound (read) | Schedule, race card, odds — **F-006–F-009** | Yes (Must) |
| **Race card cache** | Inbound | `inbox/race-cards/` — [race-card-schema.md](./race-card-schema.md) | Yes |
| **Odds cache** | Inbound | `inbox/odds/` — fallback if ATG fetch fails | Yes |
| **Grok skills** | Tooling | `/airup`, `/generate-proposal`, etc. | Yes |

**Legacy mapping:** SRS §5.

---

## 9. + Regulatory and compliance

| ID | Requirement | Authority | Notes |
|----|-------------|-----------|-------|
| SUP-C-001 | Betting rules in `docs/betting/` SHALL align with official ATG regulations | Nisse | Flag discrepancies for reconciliation |
| SUP-C-002 | Tool is decision support only; operators place bets under ATG T&C | ornstein | Not a gambling operator |
| SUP-C-003 | ATG data fetch (race card, odds) SHALL comply with ATG ToS; document source in manifest | Povl / ornstein | [atg-data-source.md](../../outbox/specs/atg-data-source.md) APPROVED |
| SUP-C-004 | V85 pool percentages SHALL follow effective date rules (e.g. 2026-07-02 change) | Nisse | [v85.md](../betting/v85.md) v1.0 |

---

## 10. Open items

| Item | Waiting on | Linked UC/SUP |
|------|------------|---------------|
| Legal review of ATG read access | ornstein / Nisse | SUP-C-003 |
| Expert template catalog | Nisse | UC-12 |
| Monte Carlo iteration defaults | Povl | UC-13, SUP-P-002 |
| Disk cache / stale-while-revalidate | v1.2 | SUP-R-001, atg-data-source |

**Resolved (v1.1):** ATG API primary with HTML scrape fallback — [atg-data-source.md](../../outbox/specs/atg-data-source.md).

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | APPROVED — v1.1 alignments; optional horse marks; F-071 checklist; ATG source resolved |
| 0.2 | 2026-07-06 | ATG auto-fetch, UX workflow, SYSTEMKOSTNAD default 500 SEK |
| 0.1 | 2026-07-06 | Initial supplementary spec; migrated from SRS §4–§5, FURPS+ layout |