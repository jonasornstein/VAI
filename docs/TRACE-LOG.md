# ATG — Trace Log

| Field | Value |
|-------|-------|
| **Version** | 0.1 |
| **Owner** | Jonte |
| **Last updated** | 2026-07-08 |

Optional audit trail of significant project decisions and AIRUP **Update** events. Jonte requests entries; agents suggest but do not append without direction.

---

## Format

| Date | AIRUP phase | Actor | Summary | Artifact / link |
|------|-------------|-------|---------|-----------------|
| 2026-07-08 | R | Jonte | **Träffsannolikhet** — F-052 basic formula reference (pool-share proxy, independent-leg DP) | See [§ Träffsannolikhet](#träffsannolikhet-f-052-basic) |
| 2026-07-08 | P | Jonte | **End of session** — UC-15 race info in leg headers; operator verified in local UI | See [§ End of day — 2026-07-08](#end-of-day--2026-07-08) |
| 2026-07-08 | P | Nisse, Jonte | **UC-15 race info shipped** — F-029 leg headers; ATG metadata; scratches fix | [UC-15-race-info.md](./requirements/use-cases/UC-15-race-info.md), [race-info-v1.md](../../outbox/specs/race-info-v1.md) |
| 2026-07-07 | P | Jonte | **End of session** — v1.1 Hari shipped; RUP trilogy APPROVED; Phase 2b complete; race day Årjäng 2026-07-11 next | See [§ End of day — 2026-07-07](#end-of-day--2026-07-07) |
| 2026-07-07 | P | Jonte, Povl, Nisse | **supplementary-specification APPROVED** — FURPS+ v1.0; v1.1 NFR alignments | [supplementary-specification.md](./requirements/supplementary-specification.md), [REVIEW_supplementary-specification.md](../../outbox/reviews/REVIEW_supplementary-specification.md) |
| 2026-07-07 | P | Povl, Jonte | **functions.md APPROVED** — v1.0 F-* catalog; shipped vs deferred; module map | [functions.md](./requirements/functions.md), [REVIEW_functions.md](../../outbox/reviews/REVIEW_functions.md) |
| 2026-07-07 | P | Jonte, Povl, Nisse | **All use cases APPROVED** — 13 UCs v1.0; Phase 2b complete; UC-12/13 spec-only | [use-cases/](./requirements/use-cases/), [REVIEW_use-cases_v1.0.md](../../outbox/reviews/REVIEW_use-cases_v1.0.md) |
| 2026-07-07 | U | Assistant | **functions.md refreshed** — v0.4 shipped vs deferred; v1.1 ATG fetch, F-052 basic, module map | [functions.md](./requirements/functions.md) |
| 2026-07-07 | P | Povl, Nisse | **race-card-schema APPROVED** — v1.0; ATG primary ingestion, validation rules, source enum | [race-card-schema.md](./requirements/race-card-schema.md), [REVIEW_race-card-schema.md](../../outbox/reviews/REVIEW_race-card-schema.md) |
| 2026-07-07 | P | Jonte | **ux-workflow APPROVED** — operator UX workflow v1.0; Hari v1.1 flow, ATG fetch, nearest stake | [ux-workflow.md](./requirements/ux-workflow.md), [REVIEW_ux-workflow.md](../../outbox/reviews/REVIEW_ux-workflow.md) |
| 2026-07-07 | P | Povl, Jonte | **UC-11 APPROVED** — Random mode (Hari) use case v1.0; exact-budget fill, frozen legs, nearest stake | [UC-11-random-mode.md](./requirements/use-cases/UC-11-random-mode.md), [REVIEW_UC-11_random-mode.md](../../outbox/reviews/REVIEW_UC-11_random-mode.md) |
| 2026-07-07 | U | Jonte | **V75 removed** — game discontinued at ATG; spelform dropdown V85-only in mockup | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | P | Povl | **Random v1.1 + ATG data source APPROVED** — exact-budget Hari, nearest stake, F-052 basic | [random-v1.1.md](../../outbox/specs/random-v1.1.md), [atg-data-source.md](../../outbox/specs/atg-data-source.md) |
| 2026-07-07 | P | Jonte | **V85 Årjäng 2026-07-11 proposal APPROVED** — Hari seed 42, 500 SEK, 1 000 rader | [proposal.md](../../outbox/proposals/v85/2026-07-11-arjang/proposal.md) |
| 2026-07-07 | P | Jonte | **V75 spelform v1.1** — selector enabled for title/ATG link; V85 schedule API unchanged until `docs/betting/v75.md` | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | R | Assistant | **Random v1.1 spec + ATG data source** — exact-budget Hari, nearest stake, F-052 basic; docs and UX workflow updated | [random-v1.1.md](../../pending/specs/random-v1.1.md), [atg-data-source.md](../../pending/specs/atg-data-source.md) |
| 2026-07-07 | R | Assistant | **Race-day draft** — Årjäng 2026-07-11 inbox card + pending proposal (seed 42, 500 SEK) | [pending/proposals/v85/2026-07-11-arjang/](../../pending/proposals/v85/2026-07-11-arjang/) |
| 2026-07-07 | U | Jonte | **Hästar labels** — legend `Slumpens hästar`; stat `Antal hästar tillagda`; rationale uses `hästar till budget` (seed help unchanged) | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | U | Jonte | **Rationale text** — default `Slumpmässigt urval ur operatörens kandidatpool per avdelning.`; after generate appends `Markerade hästar låses. Slumpen fyller på med x hästar till budget.` | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | U | Jonte | **Hari mode + action buttons** — Random tab renamed `Hari`; `GENERERA SYSTEM` and `ÖPPNA ATG/V85` matched size via `.btn-action` | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | U | Jonte | **Innan spel checklist wired** — `F-071` items update from generated system + race card (legs, cost, scratches, reserves) | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | U | Jonte | **Dynamic title verified** — headline, page title, and logo tooltip update to `VAI` + spelform on change (e.g. V85 → V75) | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | U | Jonte | **VAI branding** — logo badge `VAI`; headline `VAI` + spelform; PDF export button removed; print-only slip export | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | P | Jonte | **Genererat spel betslip APPROVED** — layout matches `inbox/betslip.png`; 8-leg V85, footer `x` format, no title bar | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | P | Jonte | **v1 close-out** — specs + canonical docs; random.md v0.2 APPROVED | [outbox/specs/](../../outbox/specs/) |
| 2026-07-07 | P | Assistant | **v1.1 local UI** — `atg serve` API + mockup wiring | [local-ui-v1.1.md](../../outbox/specs/local-ui-v1.1.md) |
| 2026-07-07 | P | Jonte | **UX mockup v0.5** published — Random default; Expert/Kvant disabled | [outbox/mockups/](../../outbox/mockups/) |
| 2026-07-07 | P | Jonte | **First random v1 proposal APPROVED** — Halmstad 2026-07-05 → `outbox/proposals/` | [proposal.md](../../outbox/proposals/v85/2026-07-05-halmstad/proposal.md) |
| 2026-07-07 | R | Assistant | **Operator review** sample proposal Halmstad 2026-07-05 — READY FOR OPERATOR | [REVIEW_proposal_2026-07-05-halmstad.md](../../pending/reviews/REVIEW_proposal_2026-07-05-halmstad.md) |
| 2026-07-07 | R | Assistant | **UX mockup v0.5:** Random default; Expert/Kvant disabled (*Kommer senare*) | [pending/mockups/](../../pending/mockups/) |
| 2026-07-07 | R | Assistant | **Random v1 implementation:** `src/atg/` vertical slice + CLI + 13 tests; sample proposal | [src/](../../src/) |
| 2026-07-07 | R | Jonte + Assistant | **Random v1 spec:** dynamic max_horses_per_leg = pool size; greedy shrink; uniform draw | [random-v1.md](../../pending/specs/random-v1.md) |
| 2026-07-07 | R | Jonte + Assistant | **v1 scope lock:** Random-only implementation; manual YAML race cards; Expert/Quant UX-only (deferred) | [scope-lock-v1-random.md](../../pending/specs/scope-lock-v1-random.md) |
| 2026-07-06 | P | Assistant | RUP requirements package (UC-01–UC-31, F-001–F-103, UX workflow) → `docs/requirements/` | [requirements/](./requirements/) |
| 2026-07-06 | P | Assistant | UX mockup v0.4 (ATG fetch UX, horse pools, SYSTEMKOSTNAD, logo) → `outbox/mockups/` | [outbox/mockups/](../../outbox/mockups/) |
| 2026-07-06 | R | Assistant | UC-09 ATG auto-fetch; UX workflow; SYSTEMKOSTNAD default 500 SEK | [ux-workflow.md](./requirements/ux-workflow.md) |
| 2026-07-06 | R | Assistant | Use cases UC-01–UC-31 narratives + functions F-001–F-103 + race card schema | [requirements/](./requirements/) |
| 2026-07-06 | P | Assistant | SRS decomposed to IBM RUP trilogy; AIRUP v1.1 requirements workflow | [requirements/](./requirements/) |
| 2026-07-06 | P | Assistant | V85 proposal UX mockups v0.1–v0.3 (ATG branding, dark mode) → `outbox/mockups/` | [outbox/mockups/](../../outbox/mockups/) |
| 2026-07-06 | I | Assistant | S-009 blocked; replaced with S-009a EN PDF + access note | [S-009-access-note.md](../../inbox/research/S-009-access-note.md) |
| 2026-07-06 | P | Assistant | Quantitative strategy APPROVED v0.3 (Phase 2) | [REVIEW_quantitative.md](../../outbox/reviews/REVIEW_quantitative.md) |
| 2026-07-06 | P | Assistant | V85 rules APPROVED → `outbox/` + `docs/betting/v85.md` v1.0 | [REVIEW_v85_rules.md](../../outbox/reviews/REVIEW_v85_rules.md) |
| 2026-07-06 | R | Assistant | Phase 1 V85 rules research draft → `pending/research/` | [PENDING-RESEARCH_v85_rules.md](../../pending/research/PENDING-RESEARCH_v85_rules.md) |
| 2026-07-06 | I | Assistant | V85 source bibliography ingested | [inbox/research/v85-sources.md](../../inbox/research/v85-sources.md) |
| 2026-07-06 | P | Jonte | AIRUP methodology adopted; scaffold restructured | [AIRUP.md](./AIRUP.md) |
| 2026-07-06 | P | Assistant | Initial project scaffold (pre-AIRUP) | AGENTS.md, docs/, skills |

---

## When to log

- Methodology or requirements changes
- Nisse / Povl / operator approvals
- Promotion of `pending/` → `outbox/` or `docs/`
- Rejected proposals or superseded rules

## When not to log

- Routine agent edits, typo fixes, or exploratory drafts still in `pending/`

---

## Träffsannolikhet (F-052 basic)

**UI:** `#hit-summary-help-btn` in [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html)  
**Code:** [hit_summary.py](../../src/atg/hit_summary.py) · **Spec:** [random-v1.1.md §6](../../outbox/specs/random-v1.1.md)

### Data

- ATG `starts[].pools.V85.betDistribution` ÷ 10 000 → fraction per horse per leg

### Per leg i = 1..8

\(p_i = \min(1,\ \sum_{h \in \text{selection}_i} \text{distribution}_{i,h}\)\)

Interpretation: sum of V85 pool shares on your picks ≈ P(win leg i). **Proxy only** — not true win odds.

### Across legs (independence assumption)

Dynamic programming over k = 0..8:

- P(exactly k correct) after each leg: wrong leg adds mass at k; right leg at k+1
- Outputs: P(8), P(≥7), P(≥6), P(≥5) → sidebar bars after **Generera system**

### Limitations

- Legs treated as independent (simplified)
- Not utdelning, EV, or guaranteed return
- Full quantitative model deferred to UC-13
- Hidden when `leg_distributions` missing (manual YAML / no ATG bet %)

---

## End of day — 2026-07-08

**Session owner:** Jonte  
**Git remote:** `origin` → `https://github.com/jonasornstein/ATG.git` (`master` synced)

### Completed

| Phase | Deliverable | Status |
|-------|-------------|--------|
| Plan | UC-15 Race-info — race-level metadata per avdelning (scope confirmed) | Done |
| Ship | F-029 `extract_race_info` — name, distance, start method, class from ATG JSON | `319a12e` |
| Ship | Multi-line leg headers in local UI (`.race-info-primary/secondary/class`) | Done |
| Fix | Scratched horses excluded from `legs[].horses` (schema rule 5) | Done |
| Review + Publish | UC-15 APPROVED, `race-info-v1.md`, race-card-schema v1.1 | Done |
| Verify | Operator sign-off — race info headers look great in browser | Jonte ✓ |
| Ops | ATG server restarted (`python -m atg serve` → :8765) | Done |

### Published / approved artifacts (today)

- **Spec:** `outbox/specs/race-info-v1.md`
- **Use case:** `docs/requirements/use-cases/UC-15-race-info.md`
- **Review:** `outbox/reviews/REVIEW_UC-15_race-info.md`
- **Code:** `src/atg/atg_race_card.py`, `models/race_card.py`, mockup, 34 tests pass

### Open for next session

| ID | Item | Owner |
|----|------|-------|
| — | **Race day Saturday** — Årjäng 2026-07-11; re-fetch with race info; UC-22 ATG entry | Kricke / Jonte |
| — | **v1.2** — reduced-stake (UC-14 §3a); ATG disk cache | Povl |
| — | Per-horse info in leg grid (deferred from UC-15 v1) | Future |
| — | Housekeeping — archive duplicate `pending/` copies | Assistant |
| OI-004 | Spelstopp after Sept 2026 schedule change — TBD | Nisse |

### Notes

- Race info uses existing `games/{game_id}` fetch — no extra ATG call.
- YAML inbox cards without `race_info` still show time-only headers.
- Local UI: http://127.0.0.1:8765/

---

## End of day — 2026-07-07

**Session owner:** Jonte  
**Git remote:** `origin` → `https://github.com/jonasornstein/ATG.git` (`master` synced)

### Completed

| Phase | Deliverable | Status |
|-------|-------------|--------|
| Ship | Random v1.1 + local UI (`python -m atg serve`) — exact budget, ATG fetch, nearest stake, F-052 basic, F-071 checklist | Done |
| Review + Publish | `random-v1.1.md`, `atg-data-source.md`, `local-ui-v1.1.md` | APPROVED |
| Review + Publish | UC-11, ux-workflow, race-card-schema v1.0 | APPROVED |
| Review + Publish | All 13 remaining use cases v1.0 — Phase 2b complete | `b571037` |
| Review + Publish | `functions.md` v1.0, `supplementary-specification.md` v1.0 — **RUP trilogy complete** | `9d76d89`, `b2670cc` |
| Proposal | V85 Årjäng 2026-07-11 — Hari seed 42, 500 SEK, 1 000 rader | [outbox/proposals/v85/2026-07-11-arjang/](../../outbox/proposals/v85/2026-07-11-arjang/) |
| Tooling | Try-out scripts (UI screenshot, hit tooltip, live V85 API) | `268de32` |
| Docs | `functions.md` v0.4 refresh; VISION Phase 3b link fix; scope-lock + random-v1.1 promotion checklists ✓ | Done |

### Published / approved artifacts (today)

- **Specs:** `outbox/specs/random-v1.1.md`, `atg-data-source.md`, `local-ui-v1.1.md`
- **Requirements:** all `docs/requirements/use-cases/UC-*.md`, `use-case-model.md` v0.4, `functions.md` v1.0, `supplementary-specification.md` v1.0, `ux-workflow.md`, `race-card-schema.md`
- **Reviews:** `outbox/reviews/REVIEW_*` (UC-11, ux-workflow, race-card-schema, use-cases batch, functions, supplementary)
- **Proposal:** `outbox/proposals/v85/2026-07-11-arjang/`

### Open for next session

| ID | Item | Owner |
|----|------|-------|
| — | **Race day** — re-fetch Årjäng 2026-07-11; scratches/reserves; UC-22 ATG entry | Kricke / Jonte |
| — | **v1.2** — reduced-stake systems (UC-14 §3a); ATG disk cache | Povl |
| — | Expert / Quant modes — UX tabs disabled; UC-12/13 spec-only | Nisse / Povl |
| — | Housekeeping — archive duplicate `pending/specs/` and `pending/mockups/` | Assistant |
| OI-004 | Spelstopp after Sept 2026 schedule change — TBD | Nisse |

### Notes

- Hari (random) v1.1 is the only active mode; Expert/Kvant show *Kommer senare*.
- Local UI: http://127.0.0.1:8765/ after `python -m atg serve`.
- No automated bet placement — proposals are operator-transcribed artifacts only.

---

## End of day — 2026-07-06

**Session owner:** Jonte  
**Git remote:** `origin` → `https://github.com/jonasornstein/ATG.git` (`main` + `master` synced)

### Completed

| Phase | Deliverable | Status |
|-------|-------------|--------|
| Research | V85 2026 payout rules verified (S-013, N-004); stale sources flagged | Done |
| Review + Publish | `docs/betting/v85.md` v1.0 APPROVED | `87eff44` / `c26587a` |
| Review + Publish | `docs/strategies/quantitative.md` v0.3 APPROVED | `7e50237` / `54dcfef` |
| UX (mockup) | V85 proposal UI v0.1 → v0.3; ATG.se colors/CSS; light/dark toggle | Done |
| Publish | UX mockups → `outbox/mockups/` | `0ca357c` / `51987af` |

### Published artifacts (outbox)

- `outbox/reviews/REVIEW_v85_rules.md`, `REVIEW_quantitative.md`
- `outbox/research/PENDING-RESEARCH_v85_rules.md` (archive)
- `outbox/mockups/` — html, png, pdf (light + dark)

### Open for next session

| ID | Item | Owner |
|----|------|-------|
| — | Real race day: fresh YAML + operator pools → proposal | Kricke / Jonte |
| — | ATG auto-fetch spec (`pending/specs/atg-data-source.md`) | Povl |
| — | Expert / Quant generators — **on hold** until Jonte directs | Povl |
| OI-001 | Ingest S-009b Swedish *Spelregler Häst* when ATG updates PDF | Nisse |
| OI-004 | Spelstopp after Sept 2026 schedule change — TBD | Nisse |

### Notes

- Mockup working copies remain in `pending/mockups/`; canonical published versions in `outbox/mockups/`.
- No automated bet placement — proposals are operator-transcribed artifacts only.