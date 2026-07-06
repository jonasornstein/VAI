3# V85 research sources (raw inbox)

| Field | Value |
|-------|-------|
| **Ingested** | 2026-07-06 |
| **Updated** | 2026-07-06 (staleness audit) |
| **AIRUP phase** | I (Inbox) |
| **Task** | Phase 1 — V85 rules research |

**Precedence and staleness:** [v85-source-precedence.md](./v85-source-precedence.md)

## Primary sources (ATG official / kundservice)

| ID | Source | URL | Status |
|----|--------|-----|--------|
| S-001 | Vad är V85? (ATG kundservice) | https://atg-extern.kb.kundo.se/guide/information-angaende-v85 | **STALE** (payout) — still 35/15/15/35, 5 SEK jackpot; use S-013/N-004 |
| S-002 | Spela V85 med sänkt insats | https://atg-extern.kb.kundo.se/guide/spela-v85-med-sankt-insats | OK — 3 coupons, 4000 rows |
| S-003 | Struken häst (V-spel) | https://atg-extern.kb.kundo.se/guide/vad-galler-nar-en-hast-blir-struken | OK |
| S-004 | Reserver | https://atg-extern.kb.kundo.se/guide/vad-ar-reserver | OK |
| S-005 | Dött lopp | https://atg-extern.kb.kundo.se/guide/vad-innebar-dott-lopp | OK |
| S-006 | Inställda tävlingar | https://atg-extern.kb.kundo.se/guide/vad-galler-vid-installda-tavlingar | OK |
| S-007 | Maxgränser system | https://atg-extern.kb.kundo.se/guide/vilka-maxgranser-finns-for-antal-system | OK |
| S-008 | Jackpotfördelning | https://atg-extern.kb.kundo.se/guide/jackpotfordelning | **PARTIAL** — carry-over OK; no 2026 V85 pool rules |
| S-014 | Vad är en Jackpot? (kundservice) | https://atg-extern.kb.kundo.se/guide/vad-ar-en-jackpot | OK — Dubbeljackpot, MultiJackpot; links to atg.se/aktuellt/jackpot |
| ~~S-009~~ | ~~ATG spelregler PDF (ctfassets)~~ | *(see S-009a)* | **BLOCKED** (403) |
| **S-009a** | **Betting Regulations EN (2025-10-20)** | https://www.swedishhorseracing.com/media/oqte5h0t/betting-regulations-english-version-valid-from-20251020.pdf | **STALE** (payout) — local: `ATG-betting-regulations-en-20251020.pdf`; mechanics OK |
| **S-009b** | **Spelregler Häst (SV, authoritative)** | https://www.atg.se/hjalp/regler-och-villkor | **NOT INGESTED** — no newer PDF on SHR index (checked 2026-07-06) |
| **S-009c** | SHR download index | https://www.swedishhorseracing.com/for-partners/download-documents | OK — latest regulations PDF still 2025-10-20 |

See [S-009-access-note.md](./S-009-access-note.md) for blocked-URL details.

## Press / news (rule changes)

| ID | Source | Date | Topic |
|----|--------|------|-------|
| N-001 | ATG press — sänkt insats utökad | 2026-04-07 | 3 kuponger, 4000 rader |
| N-002 | ATG press — vinstpooler (första tillkännagivande) | 2026-05-29 | Pool 30/20/15/35, jackpotgränser; datum TBD |
| **N-004** | **atg.se nyhet + ATG press (bekräftelse)** | **2026-06-29** | **Effekt 2026-07-02; full regeltext** |
| N-003 | Svensk Galopp / ATG press | 2025-06-08 | V85 premiär, radpris 50 öre |
| N-005 | Aftonbladet Trav365 — jackpottregler | 2026-07-02 effekt | Corroborates N-004 |

**N-004 URLs:**

- atg.se: https://www.atg.se/nyheter/260629-ny-vinstfordelning-pa-v85-fran-sprintermastaren-2-juli (S-013)
- ATG press: https://www.mynewsdesk.com/se/atg/pressreleases/ny-vinstfoerdelning-paa-v85-r-fraan-sprintermaestaren-2-juli-3456325

Verification note: [v85-2026-payout-verification.md](./v85-2026-payout-verification.md)

## Secondary

| ID | Source | URL | Status |
|----|--------|-----|--------|
| S-010 | Swedish Horse Racing — V85 (EN) | https://www.swedishhorseracing.com/our-games/v85 | **LIMITED** — no pool/jackpot detail |
| S-011 | atg.se/v85 | https://www.atg.se/v85 | OK — SPA game page |
| **S-013** | **atg.se — V85 vinstfördelning 2026** | https://www.atg.se/nyheter/260629-ny-vinstfordelning-pa-v85-fran-sprintermastaren-2-juli | **OK** — authoritative payout (with N-004) |
| S-012 | Fullständiga regler (kundservice pointer) | https://atg-extern.kb.kundo.se/guide/var-hittar-jag-fullstandiga-regler-och-villkor-for-hast | OK — pointer to S-009b |

## Ingested locally

| File | Source |
|------|--------|
| `ATG-betting-regulations-en-20251020.pdf` | S-009a (884 KB) |

## Not yet ingested

- [ ] Swedish *Spelregler Häst* PDF via S-009b (awaiting ATG update; Nisse browser download → `inbox/research/`)
- [x] English regulations PDF (S-009a) — downloaded (payout sections superseded by S-013/N-004 from 2026-07-02)

## Stale on ATG side (re-checked 2026-07-06)

ATG has not updated these live sources post–2026-07-02. Project uses S-013/N-004 until they catch up.

| ID | Still shows | Correct (2026-07-02+) |
|----|-------------|------------------------|
| S-001 | 35/15/15/35; 5 SEK jackpot all pools | 30/20/15/35; no 5-correct jackpot; 7 SEK on 6-correct |
| S-009a | 35/15/15/35 (valid-from 2025-10-20) | Same as above |
| S-009c index | Only 2025-10-20 PDF listed | — |