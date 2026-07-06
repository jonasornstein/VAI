# V85 — Betting rules (research draft)

| Field | Value |
|-------|-------|
| **Status** | APPROVED |
| **AIRUP phase** | P (Publish) |
| **Target doc** | `docs/betting/v85.md` |
| **Reviewer** | Nisse (agent review 2026-07-06) |
| **Researched** | 2026-07-06 (agent, from ATG kundservice + press) |
| **Version** | 0.6-approved |

> **Nisse:** Source precedence in `inbox/research/v85-source-precedence.md`. **Payout/jackpot (2026-07-02+):** S-013 + N-004. **Mechanics:** S-009a (payout sections stale). **S-001 kundservice stale** on pools — do not use for §3. S-009b not yet ingested. See `inbox/research/S-009-access-note.md`.

---

## 1. Overview

**V85®** is ATG's flagship **Saturday Pick8** pool for trotting (*trav*). Bettors pick the **winner** in **8 predetermined races** (*avdelningar*). Payouts exist for **8, 7, 6, and 5** correct legs.

| Attribute | Value |
|-----------|-------|
| Legs | 8 |
| Sport | Trotting (harness racing) |
| Ordinary schedule | Saturdays (few exceptions) |
| Extra rounds | Some weekdays and Sundays |
| Row price (*radpris*) | **0.50 SEK** per combination |
| Premiere | 2025-10-25, Jägersro |
| Return to players | 65% |
| Win tax (*vinstavdrag*) | 35% |

**Official entry points:** [atg.se/v85](https://www.atg.se/v85) · [ATG kundservice — V85](https://atg-extern.kb.kundo.se/guide/information-angaende-v85)

---

## 2. How to play

### 2.1 Basic system

- Mark **one or more horses** per leg.
- **Spik** = one horse in a leg; **gardering** = multiple horses.
- You win if your selections include the **official winner** in each leg counted toward your prize level.

### 2.2 Cost formula (ordinary stake)

```
rows (combinations) = ∏ (horses marked in leg i)  for i = 1..8
cost (SEK)          = rows × 0.50
```

**Example:** 1 × 3 × 1 × 2 × 1 × 4 × 1 × 2 = **48 rows** → **24.00 SEK**.

### 2.3 Terminology (ATG)

| Swedish | English | Notes |
|---------|---------|-------|
| Rad | Row | One combination across 8 legs |
| System | System | Full set of rows on a coupon |
| Kupong | Coupon | Betting slip; may hold multiple systems |
| Avdelning | Leg | One of the 8 V85 races |

---

## 3. Payout pools and distribution

V85 has **four prize pools** (8 / 7 / 6 / 5 correct).

### 3.1 Current rules (from **2026-07-02**)

**Verified on atg.se** (S-013, 2026-06-29) and ATG press release (N-004). Effective from Sprintermästaren round **2026-07-02** (Halmstad).

> **Note:** S-001, S-009a marked **STALE** (payout) per staleness audit 2026-07-06. ATG has not updated kundservice or regulations PDF. See `inbox/research/v85-source-precedence.md`.

| Correct | Pool share | Jackpot behaviour |
|---------|------------|-------------------|
| **8** | **30%** | If no one has 8 correct, or payout **below 5 SEK** → jackpot (see §3.3; threshold unchanged per N-004) |
| **7** | **20%** | Was 15%; +5% moved from 8-correct pool |
| **6** | **15%** | Unchanged share; jackpot threshold changed (below) |
| **5** | **35%** | Unchanged share; **no jackpot** (below) |

**Jackpot changes (2026-07-02, N-004):**

- **No jackpot on 5 correct.** If 5-correct payout is **below 5 SEK**, funds move **up to the 6-correct pool** (not jackpot).
- **6-correct jackpot threshold** raised from **5 SEK → 7 SEK**. If payout remains **below 7 SEK** after any 5-correct top-up → **jackpot** (press release: *dubbeljackpot*).
- **8-correct** jackpot mechanics unchanged in principle (no winners / below threshold → carry to next ordinary round).

### 3.2 Previous rules (2025-10-25 – 2026-07-01)

For historical reference only:

| Correct | Pool share |
|---------|------------|
| 8 | 35% |
| 7 | 15% |
| 6 | 15% |
| 5 | 35% |

Jackpot threshold: **5 SEK** on all pools (per S-001).

### 3.3 Jackpot carry-over

Per ATG kundservice (S-008): on V85/V86/V65/V64, jackpot funds roll to the **highest prize pool** on the **next ordinary round**.

**Dubbeljackpot** (S-014): if no payout in **two** V85 pools, funds become a Dubbeljackpot (ordinary rounds). N-004 notes this can arise when 6-correct stays below 7 SEK after 5-correct top-up.

**MultiJackpot** (S-014): 20% of jackpots on ordinary V85 rounds + 100% on extra rounds fonderas; added to 8-correct pool when ATG decides.

S-008 does not reflect 2026 pool-specific rules — use N-004 for thresholds.

---

## 4. Reduced stake (*sänkt insats*)

Optional lower row price on **mathematical systems** only.

| Stake level | Cost | Payout if you win |
|-------------|------|-------------------|
| 30% | 30% of ordinary cost | 30% of ordinary dividend |
| 50% | 50% | 50% |
| 70% | 70% | 70% |

**Example:** 1 MSEK ordinary dividend → 300k / 500k / 700k at 30/50/70%.

### 4.1 Limits (from **2026-04-11**)

Per ATG press (N-001):

| Rule | Value |
|------|-------|
| Max coupons per customer per round | **3** (was 1 at launch) |
| Max rows per coupon | **4 000** (was 2 000) |
| Eligible play type | Mathematical system only |

### 4.2 Not eligible for reduced stake

- Butiksandelar (shop shares)
- Tillsammans
- Reduced systems (*reducerat spel*)
- Harry Boy
- Cannot mix reduced-stake own system with Tillsammans on same coupon pattern

---

## 5. System limits

| Limit | Value | Source |
|-------|-------|--------|
| Max systems per account / round / game | **5 000** | S-007 |
| Reduced-stake max rows / coupon | **4 000** | N-001 |
| Reduced-stake max coupons / customer | **3** | N-001 |

If own play exceeds max systems → **entire submission rejected**. Tillsammans/shop over-limit → accepted then **voided** with refund.

---

## 6. Reserves and scratched horses (*struken*)

### 6.1 Scratched horse (V85 = V-spel)

Per S-003 (kundservice summary) and **S-009a §4–§6** (V-betting, all V games including V85):

- Up to **two reserve selections** per leg may be marked.
- On withdrawal: customer's reserves apply **in priority order**; otherwise reserves from the **established reserve order** (unmarked program numbers).
- Same program number may be marked as **both regular and reserve** (counts as more winning combinations if both win — S-009a §5).
- Reserve order from digital Program at atg.se; if >50% horses deleted from order, Arranger publishes new order on atg.se.
- Kundservice: first reserve left, second reserve right on betting slip.

### 6.2 Choosing your own reserves

Per S-004 and S-009a §4:

- Optional **1st and 2nd reserve** per leg (ATG UI → *välj reserver*).
- If not chosen, ATG uses **established reserve order** (not only stake distribution — kundservice simplifies to "insatsfördelning" for auto-assigned reserves at bet time).

### 6.3 Operator note (Kricke/Jonte)

On race day: **check scratches** before start; reserves activate automatically on the ATG coupon. Proposals should note if specific reserves were planned.

---

## 7. Race result edge cases

### 7.1 Dead heat (*dött lopp*)

Per S-005 and **S-009a §21** (general) + **§10** (V-betting):

- Dead heat for **1st place**: **each tied horse is the winner**.
- **V-betting §10:** If dead heat for 1st in a leg, dividend shares for a customer who marked multiple dead-heat horses = **product of winning horses selected in each leg** (multiplier effect).
- If you marked **both** dead-heat winners in a leg → both count; combination math multiplies.

Per S-009a §10 (EN); reconcile with S-009b when Swedish PDF is updated.

### 7.2 Disqualification (*utkörning*)

Per **S-009a §20** (Result of Betting):

> Placing according to the race Arranger's **definitive result** determines the result of the betting.

Disqualified horses are typically reflected in the **definitive result** (not the provisional finish order). The leg winner for V85 is whoever the Arranger declares winner in the official result.

Standard ATG practice: provisional result may differ; betting follows **definitive result** after steward review.

### 7.3 Cancelled races / meetings

Per S-006:

- Races moved within **24 hours** of program time are **not** considered cancelled.
- If races or the game are **cancelled**, play is **void** — stakes and fees **refunded**.

---

## 8. Schedule notes (2026)

| Change | Effective | Detail |
|--------|-----------|--------|
| Jackpot / pool rules | 2026-07-02 | §3.1 |
| Reduced-stake limits | 2026-04-11 | §4.1 |
| V85 start time | From 2026-09-05 (Derby weekend) | **15:00** (70 min earlier); race day from **13:30**; last leg ~**17:35** (press) |
| Spelstopp Saturdays | **TBD** | S-001 states 16:10 pre-change; Nisse to confirm post-schedule shift |

---

## 9. Other V85 features

| Feature | Notes |
|---------|-------|
| **Boost** | Extra side game available (see ATG guide V85 Boost) |
| **Harry Boy** | Autofill — not compatible with reduced-stake own systems |
| **Filinlämning** | File submission for large systems |

---

## 10. Entry at ATG (operators)

1. Open [atg.se/v85](https://www.atg.se/v85) on race day.
2. Select the Saturday meeting.
3. Build system leg by leg; optionally set reserves.
4. Verify **row count** and **SEK cost** match proposal.
5. Submit manually — **this project does not automate placement**.

---

## 11. Proposal requirements (ATG project)

Every V85 proposal from this project must:

- Cover all **8 legs** with **start numbers**
- State **row count** and **total SEK cost** (ordinary 0.50 SEK rows unless reduced stake specified)
- Note **track, date**, and **mode**
- Remind operator to verify **scratches** and reserves on race day

---

## 12. Open items (post-review)

| ID | Item | Status |
|----|------|--------|
| OI-001 | S-009a EN PDF + S-009b Swedish spelregler | **Partial** — S-009a mechanics approved; S-009b await PDF update |
| OI-001b | 2026-07-02 pool rules supersede PDF | **Closed** — S-013/N-004 |
| OI-002 | Disqualification — definitive result | **Closed** — §7.2 per S-009a §20 |
| OI-003 | Dead heat §10 multiplier | **Closed** — §7.1 per S-009a §10 |
| OI-004 | Spelstopp after Sept 2026 schedule change | **Open** — TBD in §8 |
| OI-005 | Jackpot carry-over V85 wording | **Closed** (draft) — §3.3; formal PDF TBD |
| OI-006 | Boost rules for proposals | **Deferred** |

---

## 13. Handoff to Povl

| Topic | Action |
|-------|--------|
| Pool % and jackpot thresholds | Add to `docs/strategies/quantitative.md` if modelling EV |
| Reduced-stake payout scaling | Document in quant spec |
| Row/cost formula | Already in FR-013/FR-014 — confirm 0.50 SEK |

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.6-approved | 2026-07-06 | AIRUP review APPROVE; §7 clarified; 8-correct jackpot threshold; OI updates |
| 0.5-draft | 2026-07-06 | Staleness audit; S-001/S-009a marked STALE; S-014 added; precedence doc |
| 0.4-draft | 2026-07-06 | atg.se verification (S-013, N-004); OI-001b verified; jackpot ordering clarified |
| 0.3-draft | 2026-07-06 | S-009 blocked; S-009a PDF ingested; §10/§20/§4–6 from regulations |
| 0.2-draft | 2026-07-06 | Phase 1 research — ATG kundservice + 2026 press |
| 0.1 | 2026-07-06 | Initial stub in docs/betting/v85.md |

---

## Sources

See `inbox/research/v85-sources.md`.