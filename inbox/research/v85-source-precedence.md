# V85 source precedence and staleness

| Field | Value |
|-------|-------|
| **Last audited** | 2026-07-06 |
| **AIRUP phase** | I (Inbox) |
| **Owner** | Nisse |

## Precedence (highest first)

Use the **highest row that covers the topic** for race-day rules from **2026-07-02** onward.

| Rank | ID | Covers | Valid from |
|------|-----|--------|------------|
| 1 | S-009b | Formal *Spelregler Häst* (SV) — when updated PDF exists | TBD (not yet re-ingested) |
| 2 | **S-013 + N-004** | **2026 payout pools and jackpot thresholds** | **2026-07-02** |
| 3 | S-009a | V-betting mechanics, reserves, dead heat, disqualification | 2025-10-20 (payout % stale) |
| 4 | S-001–S-008 | Kundservice guides (mixed freshness) | See staleness table |
| 5 | S-010 | SHR marketing page | No pool/jackpot detail |

**Rule:** When S-001 or S-009a conflict with S-013/N-004 on **pool % or jackpot**, use S-013/N-004.

## Staleness register

Re-checked live on **2026-07-06**. ATG has **not** updated kundservice or SHR regulations PDF since the 2026-07-02 rule change.

| ID | Status | Stale fields | Use instead |
|----|--------|--------------|-------------|
| **S-001** | **STALE** (payout) | Pools 35/15/15/35; jackpot 5 SEK all pools; reduced-stake text says "1 system" in one bullet (contradicts S-002); spelstopp 16:10 | S-013, N-004 for §3; S-002 for reduced stake |
| S-002 | OK | — | Current for reduced stake (3 coupons, 4000 rows) |
| S-003–S-007 | OK | — | Reserves, dead heat, limits unchanged by 2026 payout |
| **S-008** | **PARTIAL** | Carry-over to highest pool OK; no 2026 pool-specific jackpot rules | N-004, S-014 |
| **S-009a** | **STALE** (payout) | Pools 35/15/15/35 in PDF (valid-from 2025-10-20) | S-013, N-004 for §3 |
| **S-009b** | **NOT INGESTED** | No local copy; SPA download page | Nisse browser download when updated |
| **S-010** | **LIMITED** | No pool % or jackpot rules | S-013, N-004 |
| S-011, S-013 | OK | SPA shells for game pages; S-013 meta verified | N-004 for full text |
| **S-014** | OK | Dubbeljackpot definition; points to atg.se/aktuellt/jackpot for per-game rules | Complements N-004 |

## Authoritative 2026 payout snapshot (project)

Canonical until spelregler PDF updates — from [v85-2026-payout-verification.md](./v85-2026-payout-verification.md):

| Correct | Pool | Jackpot |
|---------|------|---------|
| 8 | 30% | Threshold unchanged in principle → next ordinary round |
| 7 | 20% | — |
| 6 | 15% | &lt; 7 SEK → jackpot / dubbeljackpot |
| 5 | 35% | **No jackpot**; &lt; 5 SEK → top-up to 6-correct pool |

## Re-check triggers

Re-audit S-001, S-009a, S-009b when:

- ATG publishes updated *Spelregler Häst*
- SHR download index lists a regulations PDF after 2025-10-20
- Kundservice "Vad är V85?" shows 30/20/15/35