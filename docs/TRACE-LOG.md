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
| **SL-*** | **v1 scope lock** — approve `pending/specs/scope-lock-v1-random.md` | Jonte |
| — | Step 2: `pending/specs/random-v1.md` (close Povl open items in `random.md`) | Povl |
| — | Step 3–4: `src/atg/` random vertical slice + sample YAML + golden test | Dev |
| — | Step 5: Mockup — Random default; Expert/Quant disabled (*Kommer senare*) | Jonte |
| OI-001 | Ingest S-009b Swedish *Spelregler Häst* when ATG updates PDF | Nisse |
| OI-004 | Spelstopp after Sept 2026 schedule change — TBD | Nisse |
| — | Commit remaining project scaffold (`.grok/`, `AGENTS.md`, `src/`, etc.) | Jonte |
| — | ATG auto-fetch spec (`pending/specs/atg-data-source.md`) — **deferred post-v1** | Povl |
| — | Expert / Quant generators — **on hold** until Jonte directs | Povl |
| — | First race-day proposal via `/generate-proposal` or `/v85-system` | Kricke / Jonte |

### Notes

- Mockup working copies remain in `pending/mockups/`; canonical published versions in `outbox/mockups/`.
- No automated bet placement — proposals are operator-transcribed artifacts only.