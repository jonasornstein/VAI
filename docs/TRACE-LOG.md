# ATG — Trace Log

| Field | Value |
|-------|-------|
| **Version** | 0.1 |
| **Owner** | Jonte |
| **Last updated** | 2026-07-07 |

Optional audit trail of significant project decisions and AIRUP **Update** events. Jonte requests entries; agents suggest but do not append without direction.

---

## Format

| Date | AIRUP phase | Actor | Summary | Artifact / link |
|------|-------------|-------|---------|-----------------|
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