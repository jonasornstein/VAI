# 2026-08-07 — Deep research: ATG andelsspel screen-scrape (V85 gameId)

| Field | Value |
|-------|-------|
| **AIRUP phase** | I (Inbox) |
| **Status** | Partial (coverage gaps noted) |
| **Topic** | Can VAI screen-scrape V85 systems from ATG andelsspel for a given gameId? |
| **Target URL** | https://www.atg.se/andelsspel?gameId=V85_2026-08-08_33_5 |
| **Reviewer** | Nisse (ATG rules / ToS); ornstein (operator policy) |
| **Source** | `/deep-research` workflow (gameId andelsspel scrape check) |
| **Related** | [2026-07-27-deep-research-screen-scrape.md](./2026-07-27-deep-research-screen-scrape.md) |

## Summary

**No — VAI cannot screen-scrape usable V85 systems from the andelsspel listing URL.**

Unauthenticated non-JS fetch of  
`https://www.atg.se/andelsspel?gameId=V85_2026-08-08_33_5`  
returns only the ATG SPA shell (empty title/body): no share listings, no horse selections.

Full per-leg systems are **not** the content of that listing route. When horse matrices appear at all, they live on individual **butik** product pages (`/butik/<shop>/spel/<shareId>_<gameId>`), which are also SPA shells under simple HTTP fetch. ATG account terms forbid automated scraping of ATG websites. VAI Expert v1 remains **manual YAML only**.

## Findings

### 1. What the gameId andelsspel URL returns

| Path | Result (unauthenticated simple fetch) |
|------|----------------------------------------|
| `/andelsspel?gameId=V85_2026-08-08_33_5` | SPA shell only — no machine-readable body |
| `/andelsspel`, `/tillsammans` (related) | Same — shell text, no listings |

The andelsspel UI is SPA-driven. It is **not** static HTML and **not** the public racinginfo games payload.

### 2. Listing metadata vs full systems

Indexed/general catalog snippets for andelsspel expose **product metadata** only:

- Offer counts, titles, prices, share counts
- Tags such as BESTÄMD RAD
- Shop / spelläggare labels

**Not** Avd → Hästar coupon grids.

In ATG butiksandelar practice:

- A **preliminary** coupon may be optional and changeable before submission
- The **definitive** system appears on the submitted receipt under **Mina spel**
- Buying andelar / receiving that spelkvitto requires ATG account + login (e.g. BankID)

Unauthenticated automation cannot follow the normal consumer receipt path.

### 3. Where horse matrices appear (and why scrape still fails)

| Location | Content |
|----------|---------|
| `/andelsspel?gameId=…` listing | Share catalog UI — not full rads |
| `/butik/<shopSlug>/spel/<shareId>_<gameId>` | Individual share pages — where complete 8-leg systems can show in a **browser** |
| Same butik URLs via non-JS fetch | SPA shell only — no embedded horse matrix |

Prior VAI practice already used butik/spel pages as **manual transcription** sources (e.g. Referenten Bollnäs tip with `source_url` pointing at a butik spel page) — not automated extract.

### 4. Public racinginfo API (race card, not andel systems)

For the same gameId:

```text
https://www.atg.se/services/racinginfo/v1/api/games/V85_2026-08-08_33_5
```

Returns official V85 race-card JSON: races, starters, names/numbers, pool turnover, system counts.

Does **not** return:

- Andelsspel share listings
- Share horse selections

VAI’s shipped fetch helpers and `atg-data-source` call only racinginfo products/games URLs. No andelsspel or butik marketplace APIs are documented.

### 5. Legal and project policy

**ATG Allmänna Villkor (fr.o.m. 1 januari 2026)** forbid using automated systems/software to copy or extract data of any type from ATG websites (scraping), obtaining material not intentionally made available, and unauthorized copying/distribution of ATG information (IP reservation).

- **PDF:** [ATG Allmänna Villkor fr.o.m. 1 januari 2026](https://assets.ctfassets.net/hkip2osr81id/2xz0S91MO59bAzEpvDSXya/33246c540576eab06f0257e130044ae8/ATG_Allma%C3%8C_nna_Villkor_fr.o.m_1_januari_2026.pdf)
- **robots.txt:** `User-agent: *` does not disallow `/andelsspel` (only `/konto/`, `/kod/*`, `/ratta/*`, `/preview/`) — robots allowance does **not** override contractual terms.

**VAI policy (unchanged):**

| Rule | Source |
|------|--------|
| No live scrape of ATG/media expert tips in v1 | UC-12, expert-v1, expert.md |
| Manual YAML under `inbox/expert-tips/` only | Expert ingest path |
| Read-only racinginfo schedule/card/odds OK | atg-data-source, VISION non-goals |
| No automated ATG login or bet placement | AGENTS.md, VISION |

A marketplace listing alone is insufficient for Expert ingest: a **full rad** (horses on all eight legs) is required, and many andel products do not publish that as a free complete system.

## Recommendation (operator)

1. **Do not** implement an andelsspel / butik scraper.
2. Continue **manual transcription** when a free tip or visible butik rad is available in the browser.
3. Use racinginfo only for race cards/odds (already shipped).
4. Optional future marketplace ingest remains gated on explicit ToS review and is out of v1 scope.

## Coverage gaps / uncertainty

- Backend XHR/API path that populates `/andelsspel?gameId=…` was not recovered (trial share endpoints empty / access denied).
- Investigation did not run a full browser JS runtime for live share-card contents of this specific omgång.
- Not every share product shows full horse numbers before purchase (BESTÄMD RAD / preliminär kupong vs post-submission only).
- No public OpenAPI for ATG andelsspel APIs found; racinginfo remains the only clearly public JSON service verified for gameId race data.
- Exact rate limits not published; scraping ban scope for unauthenticated visitors vs konto-holders is not separately carved out in the inspected account-holder terms PDF.

## Sources (selected)

| ID | Source |
|----|--------|
| S1 | Live fetch: andelsspel gameId URL (SPA shell) |
| S2 | atg.se/andelsspel catalog / indexed snippets |
| S3–S4 | Butik spel detail pages (browser vs non-JS fetch) |
| S5/S7 | racinginfo `/api/games/V85_2026-08-08_33_5` |
| S6/S24 | Prior project note [2026-07-27-deep-research-screen-scrape.md](./2026-07-27-deep-research-screen-scrape.md) |
| S8 | `src/vai/atg_fetch.py`, atg-data-source |
| S10–S11 | Referenten Bollnäs tip YAML (manual butik transcription) |
| S12–S14 | Travcash / ATG kundservice on butiksandelar |
| S15/S19–S20 | ATG Allmänna Villkor fr.o.m. 1 januari 2026 |
| S21 | atg.se/robots.txt |
| S22–S23 | UC-12, expert.md, VISION non-goals |

---

*Logged 2026-08-07 — AIRUP Inbox. Does not change Expert v1 non-goal (no ATG tip scraper).*
