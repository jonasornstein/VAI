# V85 2026 payout rules — atg.se verification

| Field | Value |
|-------|-------|
| **Verified** | 2026-07-06 |
| **AIRUP phase** | I (Inbox) |
| **Reviewer** | Nisse (sign-off pending) |

## Summary

**Confirmed:** V85 payout pool and jackpot rules changed effective **2026-07-02** (Sprintermästaren, Halmstad).

| Correct | Pool share (new) | Previous |
|---------|------------------|----------|
| 8 | **30%** | 35% |
| 7 | **20%** | 15% |
| 6 | **15%** | 15% |
| 5 | **35%** | 35% |

Five percentage points moved from 8-correct to 7-correct pool.

### Jackpot rules (from 2026-07-02)

| Pool | Rule |
|------|------|
| **5 correct** | **No jackpot.** If payout &lt; 5 SEK → funds move **up to 6-correct pool** |
| **6 correct** | Jackpot threshold raised **5 SEK → 7 SEK**. If payout &lt; 7 SEK (after any 5-correct top-up) → **jackpot / dubbeljackpot** |
| **8 correct** | Unchanged principle: no winners or payout below threshold → jackpot to next ordinary round |

## Sources checked

### S-013 — atg.se news (primary for this verification)

| Field | Value |
|-------|-------|
| URL | https://www.atg.se/nyheter/260629-ny-vinstfordelning-pa-v85-fran-sprintermastaren-2-juli |
| Published | 2026-06-29 |
| Status | **OK** (SSR meta; SPA body not machine-readable) |

**og:title:** Ny vinstfördelning på V85® – från Sprintermästaren 2 juli

**og:description (verbatim):**

> Ingen jackpot på fem rätt och ny fördelning mellan vinstpoolerna på V85®.
> Nyheterna börjar gälla från och med omgången i samband med Sprintermästaren som avgörs i Halmstad nu på torsdag 2 juli.
> – Målet är att förändringarna över tid ska bidra till något färre jackpotomgångar och bättre betalt för sex och sju rätt, säger Lina Wallin, hästspelschef på ATG®

### N-004 — ATG press release (full rule text)

| Field | Value |
|-------|-------|
| URL | https://www.mynewsdesk.com/se/atg/pressreleases/ny-vinstfoerdelning-paa-v85-r-fraan-sprintermaestaren-2-juli-3456325 |
| Published | 2026-06-29 09:16 |
| Status | **OK** — mirrors atg.se article; includes pool % and jackpot thresholds |

Same headline and lead as S-013. Adds explicit pool table and jackpot mechanics (see Summary above).

### N-002 — ATG press (original announcement)

| Field | Value |
|-------|-------|
| URL | https://www.mynewsdesk.com/se/atg/pressreleases/atg-r-foeraendrar-vinstpoolerna-paa-v85-r-och-infoer-ny-starttid-fraan-5-september-3450977 |
| Published | 2026-05-29 |
| Status | **OK** — announced changes; date TBD at time of release |

## Stale sources (re-checked 2026-07-06)

ATG has **not** updated these live sources. Status recorded in [v85-source-precedence.md](./v85-source-precedence.md).

| ID | Issue | Project handling |
|----|-------|------------------|
| S-001 | Kundservice still **35/15/15/35**, **5 SEK** jackpot all pools; reduced-stake text inconsistent (1 vs 3 systems) | Mark **STALE**; use S-013/N-004 + S-002 |
| S-009a | EN PDF (2025-10-20) still **35/15/15/35** | Mark **STALE** (payout); mechanics still valid |
| S-009b | Not ingested; SHR index has no newer PDF | **NOT INGESTED** — await ATG update |
| S-008 | Carry-over to highest pool OK; no 2026 pool-specific rules | **PARTIAL** |
| S-010 | SHR V85 page has no pool/jackpot detail | **LIMITED** |

**Nisse:** Treat **S-013 + N-004** as authoritative for payout rules from **2026-07-02** until spelregler PDF and kundservice catch up.

## Verification gaps

| ID | Gap | Status |
|----|-----|--------|
| VG-001 | atg.se `/V85/om-v85` and `/aktuellt/jackpot` are SPA shells | Open — use N-004 + S-014 |
| VG-002 | Kundservice jackpot guides (S-008, S-014) | **Closed** — S-014 defines Dubbeljackpot; per-game rules at atg.se/aktuellt/jackpot (SPA) |
| VG-003 | Formal *Spelregler Häst* PDF update | Open — no post-2025-10-20 file on SHR index |

## Closes

- **OI-001b** — 2026-07-02 pool rules supersede PDF 35/15/15/35: **verified** (pending Nisse sign-off)