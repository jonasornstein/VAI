# ATG Trotting Betting Systems — Agent Instructions

You are working on **ATG**, a project that generates **betting system proposals** for Swedish trotting (trav) at [ATG](https://www.atg.se). Proposals are **manually entered** on the ATG website by gamblers **Kricke** or **Jonte** — this project does not automate placement of bets.

## Methodology: AIRUP (mandatory)

All work follows **AIRUP**: **A**nalyze → **I**nbox → **R**eview ⇄ **U**pdate → **P**ublish.

| Phase | Location | Purpose |
|-------|----------|---------|
| **A** Analyze | Task scope | Game, date, mode, reviewer |
| **I** Inbox | `inbox/` | Raw race cards, odds, research, requests |
| **R** Review | `pending/` | Drafts awaiting approval |
| **U** Update | `pending/` | Revisions from feedback |
| **P** Publish | `outbox/` | Approved artifacts for race day |

Full spec: [docs/AIRUP.md](docs/AIRUP.md). Rule summary: [.grok/rules/05-airup.md](.grok/rules/05-airup.md).

**Gate:** Never place unreviewed work in `outbox/`.

## Priority and scope

- **Primary game:** V85 (8-race Pick8 pool, Saturdays).
- **Future games:** V75, V86, V64, DD — add via AIRUP research path.
- **Three proposal modes:** `random`, `expert`, `quantitative` — see `docs/strategies/`.

## Domain experts (personas)

| Persona | Domain | AIRUP reviewer for |
|---------|--------|-------------------|
| **Nisse** | Trotting rules, ATG mechanics | `pending/research/`, betting docs |
| **Povl** | Odds, quant models, system math | `pending/specs/`, quantitative proposals |
| **Kricke / Jonte** | Manual ATG entry | `pending/proposals/` |

When rules conflict: Nisse wins on trotting/ATG rules; Povl wins on math/odds; Kricke/Jonte win on usability.

## Documentation map

| Document | Purpose |
|----------|---------|
| [docs/AIRUP.md](docs/AIRUP.md) | **Methodology (read first)** |
| [docs/VISION.md](docs/VISION.md) | RUP Vision — scope, goals, stakeholders |
| [docs/SRS.md](docs/SRS.md) | Requirements index + traceability |
| [docs/requirements/](docs/requirements/) | RUP use cases + supplementary spec (FURPS+) |
| [docs/ROSTER.md](docs/ROSTER.md) | Team and ownership |
| [docs/TRACE-LOG.md](docs/TRACE-LOG.md) | Decision audit trail |
| [docs/betting/v85.md](docs/betting/v85.md) | V85 rules (Nisse) |
| [docs/strategies/](docs/strategies/) | Random, expert, quantitative |

## Project layout

```
ATG/
├── inbox/          # I — raw inputs
├── pending/        # R, U — drafts
├── outbox/         # P — approved artifacts
├── docs/           # Published baseline (SRS, rules, AIRUP)
├── src/            # Implementation
└── .grok/
    ├── rules/      # Auto-loaded agent context
    └── skills/     # AIRUP-aware workflows
```

## Skills

| Skill | Purpose |
|-------|---------|
| `/airup` | Orchestrate full AIRUP cycle |
| `/airup-review` | Review and approve pending items |
| `/generate-proposal` | Proposal draft → pending → outbox |
| `/v85-system` | V85 race-day systems |
| `/research-trotting` | Nisse rules research |

## Working conventions

1. **AIRUP always** — analyze before acting; inbox raw inputs; draft in pending; publish only when approved.
2. **Proposals are artifacts, not bets** — Kricke/Jonte transcribe to ATG manually.
3. **Mark uncertainty** — `DRAFT` / `TBD` until Nisse or Povl approves.
4. **Cost formula (V85):** ∏(horses per leg) × 0.50 SEK.
5. **Log significant updates** in `docs/TRACE-LOG.md`.
6. **Extend, don't duplicate** — update canonical docs.

## Implementation (when coding)

- Python for quantitative work (Monte Carlo, odds).
- Modular strategies; shared V85 leg model.
- Code changes follow AIRUP: spec in `pending/specs/` → review (Povl) → implement → review.

## Non-goals

- Automated bet placement on ATG
- Unapproved artifacts in `outbox/`
- Financial advice or guaranteed-return claims