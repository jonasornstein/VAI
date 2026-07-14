# VAI — Project Roster

| Field | Value |
|-------|-------|
| **Version** | 0.2 |
| **Status** | DRAFT |
| **Last updated** | 2026-07-06 |

This roster tracks **who** is involved and **what** they own.

---

## 1. Team members

| ID | Name | Role(s) | Status | Notes |
|----|------|---------|--------|-------|
| M-001 | **Nisse** | Trotting domain expert, rules researcher, documentation (betting) | Active | 40+ years: owner, trainer, gambler in Swedish trotting |
| M-002 | **Povl** | Bookmaker, quant analyst, strategy requirements | Active | 50+ years: odds, system math, trotting gambling |
| M-003 | **Kricke** | Operator / gambler | Active | Enters systems manually at ATG |
| M-004 | **ornstein** | Operator / gambler, project owner | Active | Enters systems manually at ATG; drives priorities |
| M-005 | Assistant | Implementation, scaffolding, documentation drafting | Active | Does not approve rules or place bets |

---

## 2. Roles and responsibilities

| Role | Description | Assignee |
|------|-------------|----------|
| **Product owner** | Vision, priorities, acceptance | ornstein (M-004) |
| **Trotting authority** | ATG rules, race logic, trotting docs | Nisse (M-001) |
| **Quant authority** | Odds math, model requirements, expert-system constraints | Povl (M-002) |
| **Operators** | Use proposals on race day; feedback on usability | Kricke (M-003), ornstein (M-004) |
| **Developer** | Code, tests, tooling | M-005 (interim) |

---

## 3. Ownership matrix

| Area | Primary | Backup |
|------|---------|--------|
| `docs/betting/` | Nisse | ornstein |
| `docs/strategies/expert.md` | Nisse + Povl | ornstein |
| `docs/strategies/quantitative.md` | Povl | Nisse |
| `docs/strategies/random.md` | Povl (constraints) | M-005 |
| `docs/SRS.md` | ornstein | Povl |
| `docs/VISION.md` | ornstein | Nisse |
| `src/` generators | M-005 | Povl (quant review) |
| `inbox/`, `pending/`, `outbox/` (AIRUP) | ornstein | M-005 |
| `outbox/proposals/` acceptance | Kricke, ornstein | M-005 |
| `docs/AIRUP.md` methodology | ornstein | M-005 |
| `.grok/rules/`, `.grok/skills/` | M-005 | ornstein |

---

## 4. Decision rights

| Decision | Who decides |
|----------|-------------|
| ATG rule interpretation | Nisse |
| Mathematical model assumptions | Povl |
| Feature priority | ornstein |
| Proposal format acceptance | Kricke, ornstein |
| Release / phase complete | ornstein against SRS success criteria |

---

## 5. AIRUP review assignments

| `pending/` folder | Reviewer | On APPROVED → |
|-------------------|----------|---------------|
| `pending/research/` | Nisse | `outbox/research/` + `docs/betting/` |
| `pending/specs/` | Povl | `outbox/` + `docs/strategies/` |
| `pending/proposals/` | Kricke / ornstein | `outbox/proposals/` |

---

## 6. Documentation map

| Document | Owner |
|----------|-------|
| [AIRUP.md](./AIRUP.md) | ornstein |
| [TRACE-LOG.md](./TRACE-LOG.md) | ornstein |
| [VISION.md](./VISION.md) | ornstein |
| [SRS.md](./SRS.md) | ornstein |
| [ROSTER.md](./ROSTER.md) | ornstein |
| [betting/v85.md](./betting/v85.md) | Nisse |
| [betting/trotting-fundamentals.md](./betting/trotting-fundamentals.md) | Nisse |
| [strategies/*.md](./strategies/) | Povl (quant), Nisse (expert) |

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.2 | 2026-07-06 | AIRUP review assignments; path updates |
| 0.1 | 2026-07-06 | Initial roster |