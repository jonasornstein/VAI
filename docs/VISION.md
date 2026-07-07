# ATG — Vision Document

| Field | Value |
|-------|-------|
| **Version** | 0.5 |
| **Status** | DRAFT |
| **Last updated** | 2026-07-06 |
| **RUP role** | Replaces SRS introduction and overall description |
| **Methodology** | IBM RUP + [AIRUP](./AIRUP.md) |
| **Owner** | Jonte (M-004) |

---

## 1. Positioning

### 1.1 Problem statement

Kricke and Jonte play multi-leg trotting pools at ATG — especially **V85** on Saturdays. Building a **system** (selecting multiple horses across 8 legs) is time-consuming and error-prone. They want **assisted generation** of system proposals they can review and manually enter at [atg.se](https://www.atg.se).

### 1.2 Product vision

A small, trustworthy toolkit that produces **clear, correct, transcribable betting system proposals** for Swedish trotting, grounded in:

- Real ATG rules (Nisse)
- Sound mathematical framing where used (Povl)
- Three complementary generation modes: random, expert, quantitative

The system is **decision support**, not an autopilot. Humans always place bets.

### 1.3 Elevator statement

*For Kricke and Jonte who need fast, correct V85 systems on race day, ATG Proposal Toolkit is a local decision-support generator that produces reviewable, cost-verified proposals — unlike manual spreadsheet work or opaque tip services, it documents every assumption through AIRUP and expert-reviewed rules.*

---

## 2. Scope

### 2.1 In scope

- Documentation of trotting and ATG betting rules
- Three proposal generation modes: random, expert, quantitative
- V85 as first supported game
- Human-readable proposal output for manual ATG entry
- **Automatic race card collection** from ATG website or API (read-only)
- Operator UX: DATUM → BANA / SPELFORM dropdowns; horse selection; SYSTEMKOSTNAD (default 500 SEK)
- System cost and combination count calculation; model hit probabilities
- AIRUP workflow for all artifacts
- RUP requirements package ([requirements/](./requirements/))

### 2.2 Out of scope

See **Non-goals** (§5). Detailed constraints in [supplementary-specification.md](./requirements/supplementary-specification.md).

---

## 3. Stakeholders and users

Full roster: [ROSTER.md](./ROSTER.md).

| Stakeholder | Interest |
|-------------|----------|
| **Kricke / Jonte** | Usable proposals on Saturdays; manual ATG entry |
| **Nisse** | Correct trotting and ATG rules |
| **Povl** | Sound quant requirements and cost math |
| **Agents / developers** | Clear use cases and traceable specs |

---

## 4. Goals

| ID | Goal |
|----|------|
| G-001 | Generate V85 proposals Kricke/Jonte can enter without rework |
| G-002 | Support random, expert, and quantitative generation modes |
| G-003 | Maintain authoritative, versioned trotting/betting documentation |
| G-004 | Compute system cost and combination count correctly |
| G-005 | Leave a clear audit trail via AIRUP and [TRACE-LOG.md](./TRACE-LOG.md) |
| G-006 | Follow AIRUP workflow for all artifacts (inbox → pending → outbox) |
| G-007 | Express requirements as RUP use cases + supplementary spec |

---

## 5. Non-goals

| ID | Non-goal |
|----|----------|
| NG-001 | Automated bet placement or ATG login automation |
| NG-002 | Promising profits or "sure systems" |
| NG-003 | Replacing Nisse's or Povl's judgment on race day |
| NG-004 | Automated **bet placement** or account login (read-only ATG data fetch is in scope) |

---

## 6. Success criteria (v1)

- [x] V85 doc approved by Nisse — [v85.md](./betting/v85.md) v1.0 APPROVED
- [ ] At least one working generator per strategy mode
- [ ] Sample proposals validated by Kricke or Jonte against ATG UI
- [ ] Cost formula verified against ATG for 3+ example systems
- [ ] Use-case specifications **reviewed** by operators (UC-10, UC-20, UC-22) — drafts complete

---

## 7. Roadmap (AIRUP-aligned)

| Phase | AIRUP focus | Deliverables |
|-------|-------------|--------------|
| **0 — Scaffold** | **P** methodology | AIRUP, inbox/pending/outbox, skills |
| **1 — V85 docs** | **I**→**R**→**P** rules | Nisse approves `docs/betting/v85.md` ✓ |
| **2 — Quant specs** | **I**→**R**→**P** specs | Povl approves `docs/strategies/quantitative.md` ✓ |
| **2b — Requirements** | **R** use cases | RUP trilogy; enter UC narratives *(current)* |
| **3 — Generators** | **R** code via `pending/specs/` | Random → expert → quantitative in `src/` |
| **4 — Race day** | **I** race cards → **P** proposals | Operators use `outbox/proposals/` |
| **5 — More games** | AIRUP per game | V75, V86, etc. |

---

## 8. Glossary

| Term | Definition |
|------|------------|
| **Proposal** | A complete multi-leg horse selection with metadata and cost |
| **Leg / avdelning** | One race within a pool (V85: 8 legs) |
| **Race card** | Official start information for a race day (Swedish: *startlista*). For V85: which 8 races form the pool and which start numbers are valid in each leg. **Collected automatically** from ATG (API or website) per UC-09; cached in `inbox/race-cards/`. Not the betting slip, not SYSTEMKOSTNAD. |
| **SYSTEMKOSTNAD** | Operator-entered target system budget (SEK). Default **500 SEK**. Model optimizes selections so computed cost ≤ budget. Distinct from per-row ATG radpris (0.50 SEK). |
| **System** | Product of selections across legs; each combination is one row |
| **Mode** | `random`, `expert`, or `quantitative` generation strategy |
| **AIRUP** | Analyze → Inbox → Review → Update → Publish |
| **Use case** | RUP narrative describing actor–system interaction (`UC-*`) |

---

## 9. Related documents

| Document | Purpose |
|----------|---------|
| [SRS.md](./SRS.md) | Requirements index and traceability |
| [requirements/use-case-model.md](./requirements/use-case-model.md) | Functional requirements (RUP) |
| [requirements/supplementary-specification.md](./requirements/supplementary-specification.md) | Non-functional requirements (FURPS+) |
| [AIRUP.md](./AIRUP.md) | Workflow methodology |

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.5 | 2026-07-06 | ATG auto-fetch scope; SYSTEMKOSTNAD; NG-004 narrowed |
| 0.4 | 2026-07-06 | Glossary: Race card definition |
| 0.3 | 2026-07-06 | RUP Vision structure; scope/glossary from SRS §1; G-007 |
| 0.2 | 2026-07-06 | AIRUP methodology adopted; roadmap aligned |
| 0.1 | 2026-07-06 | Initial vision — project scaffold |