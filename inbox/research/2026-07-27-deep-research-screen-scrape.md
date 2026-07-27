# 2026-07-27 — Deep research: screen-scrape expert tip

| Field | Value |
|-------|-------|
| **AIRUP phase** | I (Inbox) |
| **Status** | Partial (coverage gaps noted) |
| **Topic** | Screen-scraping vs manual ingest of free V85 expert systems |
| **Reviewer** | Nisse (ToS / tip outlets); Povl (ingest policy) if scope expands |
| **Source** | `/deep-research screen-scrape expert tip` workflow |

## Summary

**VAI does not screen-scrape expert tips.** Expert v1 ingests free full systems only by **manual transcription** of horse numbers into YAML under `inbox/expert-tips/`. ATG tip scraping is a **non-goal**; no scraper ships in v1. ATG account terms and several tip outlets forbid automated extraction, so any optional future ATG tips fetch remains gated on ToS review and is not implemented.

## Legal and robots constraints

### ATG (primary)

From **1 January 2026**, ATG account terms forbid using automated systems or software to copy or extract any data from ATG’s websites (scraping), and also forbid bypassing security, overloading sites, and obtaining material not intentionally made available. The same terms reserve all IP (copyright, trademarks, database rights) and forbid copying, distributing, transmitting, or selling ATG information, software, products, or services.

- **Source PDF:** [ATG Allmänna Villkor fr.o.m. 1 januari 2026](https://assets.ctfassets.net/hkip2osr81id/2xz0S91MO59bAzEpvDSXya/33246c540576eab06f0257e130044ae8/ATG_Allma%C3%8C_nna_Villkor_fr.o.m_1_januari_2026.pdf)
- **robots.txt** (`https://www.atg.se/robots.txt`): for `User-agent *` disallows only selected paths (`/konto/`, `/kod/*`, `/ratta/*`, `/preview/`) and lists a sitemap — no blanket disallow of public pages.
- **Project requirement:** compliance for any automated ATG data fetch is operator responsibility (UC-09 / SUP-C-003 / atg-data-source).

### Third-party tip outlets

| Outlet | robots / ToS notes |
|--------|-------------------|
| **Travcash** | `Allow: /`; signals `search=yes, ai-train=no, use=reference`; disallows major AI/training crawlers (GPTBot, ClaudeBot, Google-Extended, Bytespider, CCBot) |
| **Rekatochklart** | `Allow: /` for `User-Agent *`; disallows `/endpoints/`, `/spelbok/`, `/r/`; extra path rules for `/profil/`, `/blogg/`; membership terms reserve IP |
| **Travmaskinen** | Terms forbid bots/scrapers against the service and commercial redistribution of tips/analyses without permission; content may not be copied, distributed, or resold without written permission |
| **Travstugan / Trav.se** | No inspected användarvillkor page that expressly bans scrapers of free tip content; robots mainly restrict affiliate/admin paths |

## Where free full systems appear (HTML, not APIs)

VAI’s approved expert strategy starts with free weekly V85 outlets: Travstugan, Travcash, Trav.se, Rekatochklart, Travmaskinen, plus hubs Trava På! and Gratistravtips.se. See also [2026-07-15-experts-travet.md](./2026-07-15-experts-travet.md).

| Outlet | Format of free full system | Notes |
|--------|----------------------------|--------|
| **Travcash (Referenten)** | HTML tables Avd → Hästar | Complete 8-leg systems; e.g. “Samtliga åtta startande” for a leg |
| **Trav.se** | HTML “Spelförslag” numbered lists per leg | Includes total rows/cost (e.g. “2.940 rader som kostar 1.470 kronor”) |
| **Rekatochklart (Leboff)** | HTML “V85-Förslag” 8-leg grids | Explicit cost line (e.g. “Insats: 3024 Rader x 0.50 = 1512 Kr”) |
| **Travmaskinen** | Per-leg AI rankings + HTML system builder `/spel/V85` | No documented public tips JSON API |
| **ATG public pages** | SPA/JS shells | Body not machine-readable via simple fetch |

**No primary source** among Travcash, Trav.se, Rekatochklart, Travstugan, or Travmaskinen published a stable, documented free public JSON/REST API for expert 8-leg horse selections.

### Example pages checked (Bollnäs 25/7)

- Travcash: https://travcash.se/v85-tips/v85-tips-lordag-bollnas-25-7-jackpott/
- Trav.se: https://trav.se/speltips/40-miljoner-jackpot-pa-v85-bollnas-257
- Rekatochklart: https://www.rekatochklart.com/trav/v85-tips/v85-tips-bollnas-25-7/
- Travmaskinen: https://travmaskinen.se/v85-tips

## VAI ingestion path (manual YAML)

Operators open the expert’s published system and copy horse numbers per V85 leg into:

```text
inbox/expert-tips/<YYYY-MM-DD>-<track-slug>/<tip_id>.yaml
```

| Layer | Location |
|-------|----------|
| Schema / inbox policy | [inbox/expert-tips/README.md](../expert-tips/README.md) |
| Implementation spec | [outbox/specs/expert-v1.md](../../outbox/specs/expert-v1.md) |
| Strategy policy | [docs/strategies/expert.md](../../docs/strategies/expert.md) |
| Parser | `src/vai/io/expert_tips.py` |

### Required fields

`tip_id`, `expert_id`, `expert_name`, `game`, `date`, `track`, `legs`

### Optional attribution

`source_url`, `source_note`, `fetched_at`, `product_name`, `status`, `rationale`

### Rules

- `expert_id` must be a roster key (e.g. `referenten`, `leboff`).
- `legs` maps 1–8 to non-empty integer horse lists; parser requires all eight legs, rejects empty lists and duplicates, sorts horses per leg.
- Keep `source_url` / `source_note` for private operator use; **do not present tips as VAI-originated picks**.
- Status stays **DRAFT** until double-checked against official tip and race card (Bollnäs 2026-07-25 production examples remain DRAFT pending that check).
- With race card: every selected horse must be eligible and not scratched → else `INVALID_HORSE` / `SCRATCHED_HORSE`.
- **Andelsspel alone is not enough** — VAI needs a full rad (horse numbers per leg) unless the full system is published.
- From paywalled content: store **horse numbers + metadata only**; do not commit full-text paywalled articles.

## Project decision (current)

| Question | Answer |
|----------|--------|
| Ship a tip scraper in v1? | **No** |
| ATG tip scraping? | **Non-goal**; ToS-gated if ever reconsidered |
| Supported ingest | Manual YAML under `inbox/expert-tips/` |
| Why not scrape free HTML? | Legal risk (ATG + outlet ToS), SPA/HTML fragility, policy already matches manual path |

## Coverage and uncertainty

- ATG help “robotspel” addresses automated **pool-playing** strategies, not website tip scraping.
- Whether ATG’s scraping ban applies to unauthenticated public race-card/API hits vs only account holders was not carved out separately in the inspected PDF §4.1 text.
- Travstugan hub articles may expose complete rad mainly via ATG andel links rather than always embedding a full 8-leg matrix in article HTML.
- Rekatochklart: text extraction can show program numbers 1–15 under each leg; which are selected may depend on HTML/CSS state not fully visible in plain text (operator YAML + Insats line confirm fixed systems in practice).
- Travmaskinen Next.js may call private/client JSON endpoints for the system builder; those were not captured.
- SPA evidence is strongest for **atg.se**; third-party tip pages are not all documented as JS blockers in-repo.
- Priority free full-system list is a mid-2026 snapshot and may change.

## Sources (primary)

| ID | Source |
|----|--------|
| S1–S2 | ATG Allmänna Villkor fr.o.m. 1 januari 2026 (PDF) |
| S3 | https://www.atg.se/robots.txt |
| S4 | https://travmaskinen.se/villkor |
| S5 | https://travcash.se/robots.txt |
| S6 | https://www.rekatochklart.com/villkor/ ; robots.txt |
| S7 | docs/strategies/expert.md |
| S8–S11 | Free tip pages (Travcash, Trav.se, Rekatochklart, Travmaskinen) — Bollnäs 25/7 |
| S12–S21 | inbox/expert-tips/README.md; outbox/specs/expert-v1.md; src/vai/io/expert_tips.py; expert.md |
| S22 | docs/strategies/expert.md (ToS gate) |
| S23 | UC-09; supplementary SUP-C-003 |
| S24 | inbox/research/v85-2026-payout-verification.md (ATG SPA note) |

## Related artifacts

- [2026-07-15-experts-travet.md](./2026-07-15-experts-travet.md) — free systems directory
- [inbox/expert-tips/README.md](../expert-tips/README.md) — transcription schema
- [docs/strategies/expert.md](../../docs/strategies/expert.md) — expert mode policy
- [outbox/specs/expert-v1.md](../../outbox/specs/expert-v1.md) — implementation spec
