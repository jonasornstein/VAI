# Review — PENDING-RESEARCH_v85_rules.md

| Field | Value |
|-------|-------|
| **Artifact** | `pending/research/PENDING-RESEARCH_v85_rules.md` v0.5-draft |
| **Reviewer** | Nisse (agent lens) + Povl (math) + Operator (ornstein) |
| **Review type** | Agent review — not substitute for human expert sign-off on S-009b |
| **Date** | 2026-07-06 |
| **Verdict** | **APPROVE** (with caveats) |

---

## Nisse — trotting / ATG rules

### Approved

- [x] **§1 Overview** — legs, radpris 0.50 SEK, 65% return, premiere date match S-001/S-009a context
- [x] **§2 How to play** — spik/gardering, terminology correct
- [x] **§3.1 Payout pools (2026-07-02+)** — 30/20/15/35 confirmed via S-013 + N-004; supersedes stale S-001/S-009a payout text
- [x] **§3.1 Jackpot** — no jackpot on 5-correct; &lt;5 SEK → 6-correct pool; 6-correct threshold 7 SEK; ordering matches N-004
- [x] **§3.2 Historical** — 35/15/15/35 for 2025-10-25 – 2026-07-01 correct
- [x] **§3.3 Carry-over** — S-008 highest-pool rule; Dubbeljackpot/MultiJackpot from S-014 correctly scoped
- [x] **§4 Reduced stake** — 30/50/70% scaling; limits per N-001/S-002 (3 coupons, 4000 rows)
- [x] **§5 System limits** — 5000 max per S-007
- [x] **§6 Reserves** — S-009a §4–§6 + kundservice S-003/S-004; two reserves, priority order, established order
- [x] **§7.1 Dead heat** — S-009a §10 multiplier; each tied horse wins
- [x] **§7.2 Disqualification** — S-009a §20 definitive result; acceptable for proposals
- [x] **§7.3 Cancelled** — S-006 24h rule
- [x] **§8 Schedule** — 2026-07-02 pools, 2026-04-11 reduced stake, 2026-09-05 start 15:00 per N-002/N-004
- [x] **Source precedence** — stale-source handling documented; agents won't read wrong pools from S-001

### Caveats (document, do not block publish)

- [ ] **S-009b** — Swedish *Spelregler Häst* not ingested; EN S-009a used for mechanics. Reconcile when ATG publishes updated PDF.
- [ ] **§8 Spelstopp** — post–2026-09-05 time not confirmed; keep **TBD** (pre-change: 16:10 per S-001).
- [ ] **§3.1 8-correct jackpot threshold** — N-004 silent; assume **5 SEK** unchanged (launch rules). Add explicitly to canonical doc.
- [ ] **OI-006 Boost** — deferred; not required for proposal format.

### Required changes applied in v0.6

1. Inline "Nisse: Confirm" removed from §7.1/§7.2 — content approved per S-009a
2. 8-correct jackpot threshold (5 SEK) stated in §3.1
3. Open items updated — OI-001b closed; OI-002/003/005 closed at draft level

---

## Povl — math / quant

- [x] Pool shares sum to **100%** (30+20+15+35)
- [x] Cost formula `∏(horses) × 0.50` correct
- [x] Reduced-stake payout scales linearly (30/50/70%)
- [x] Historical vs current pool split clearly separated — safe for EV modelling handoff

**Handoff:** Pool % and jackpot thresholds ready for `docs/strategies/quantitative.md` (Phase 2).

---

## Operator — Kricke / ornstein

- [x] §10 entry steps match atg.se workflow
- [x] §11 proposal requirements — 8 legs, start numbers, cost, track/date, scratch reminder
- [x] No ambiguous selection rules that would block manual entry

---

## Verdict rationale

Core V85 rules are **sufficient for race-day proposals** from 2026-07-02 onward. Remaining gaps (S-009b PDF, spelstopp post-Sept) are **documented caveats**, not blockers. Stale ATG kundservice correctly overridden by S-013/N-004.

**Action:** Publish to `outbox/research/` and promote to `docs/betting/v85.md` as **APPROVED**.