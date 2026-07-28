# 2026-07-27 — Deep research: V85 experts & full systems

| Field | Value |
|-------|-------|
| **AIRUP phase** | I (Inbox) |
| **Status** | Partial (coverage gaps noted) |
| **Topic** | Online experts sharing V85 tips / whole 8-leg systems |
| **Reviewer** | Nisse (outlets / tip fidelity); ornstein (roster priority) |
| **Source** | `/deep-research` — experts sharing V85 tips, whole systems, all 8 legs |
| **Baseline** | [2026-07-15-experts-travet.md](./2026-07-15-experts-travet.md), [experts.yaml](../../src/vai/strategies/experts.yaml), [expert.md](../../docs/strategies/expert.md) |

## Summary

Live re-check (mid-2026 / July 2026) of free and paid sources that publish **complete eight-leg V85 systems** (horse numbers + cost) or related tips. **Main free full-system outlets match VAI’s existing priority list:** Travcash, Rekatochklart (Leboff), Trav.se, Travstugan, Travmaskinen, plus hubs Trava På! and Gratistravtips.se. Mainstream ATG/TV content is common but often **partial**. Paid packages and andelsspel sell shares of full expert rads.

**Net:** research is a **validation**, not a roster overhaul. Small deltas only (named tipsters, flag nuances).

## Free weekly full-system outlets

| Outlet | What | Named people (this pass) | VAI |
|--------|------|--------------------------|-----|
| **Travcash** | Free Saturday systems; email / YouTube / podd / Facebook; andelsspel | Referenten (Albin Engdahl), **Eddie Östlund**, Oliver Pihlström | `referenten`, `albin-kjellberg`; Pihlström as andel (`free: false`); **Östlund not in roster** |
| **Rekatochklart** | V85-Förslag grids V85-1…8; stake line (rader × 0.50 SEK) | Leboff | `leboff` · full · free |
| **Trav.se** | Stora + lilla systemförslag; ~24h before spelstopp; 8 legs + rows/cost | BelminK, Manfred Kåvestam, Jens Lönnaeus | `trav-se` (outlet-level only) |
| **Travstugan** | Free tips/system analysis + video/podd; andelsspel | Martin Engström, Christian Sandholm, Johan Karlsson | `travstugan` · full · free; team list in expert.md |
| **Travmaskinen** | AI rankings all 8 legs + budget builder (~50–10 000 kr) | (product/AI) | `travmaskinen` · full · free |
| **Trava På!** | Link hub | — | expert.md §3 |
| **Gratistravtips.se** | Aggregates poddar/video | — | expert.md §3 |

As of this snapshot, those five free weekly outlets plus the two hubs remain the main public sources of ready-made eight-leg systems or tips.

### Example pages checked (Bollnäs 25/7)

- Travcash: https://travcash.se/v85-tips/v85-tips-lordag-bollnas-25-7-jackpott/
- Trav.se: https://trav.se/speltips/40-miljoner-jackpot-pa-v85-bollnas-257
- Rekatochklart: https://www.rekatochklart.com/trav/v85-tips/v85-tips-bollnas-25-7/
- Team Uhrberg: https://thomasuhrberg.se/v85-bollnas-25-juli/
- Travstugan: free V85 pages (full matrix confirmed on checked tidiga article — e.g. 640 rader / 320 kr)

## Media, ATG, aggregators

| Product / outlet | Notes | VAI |
|------------------|-------|-----|
| Aftonbladet Trav365 | V85-KOLLEN, V85-KRÖNIKAN, UNIKA V85-TIPSEN; Nicklasson, Carlsson | `sportbladet-trav365` · partial |
| Björnkollen (Goop) | Often analysis-heavy | `bjorn-goop` · partial |
| Vass eller Kass, Fem Tippar, ATG tip hub | Mix / partial | roster IDs match |
| KorsDragaren (Krillekrukan) | Early system angles | `krillekrukan` · partial |
| Expressen Systemet | Noreen & Hellberg; full format not fully verified this pass | `systemet-podd` · full · free |
| Thomas Uhrberg | Full “Thomas system” for Bollnäs 25/7 | `thomas-uhrberg` · **partial** (may lag “not always”) |

**Best single index:** https://www.travapa.se/

## How systems are packaged

Same four shapes as VAI expert strategy:

1. Free text/video (HTML grids)
2. Live podcast builds
3. Andelsspel (share of expert rad)
4. Paid tip services

ATG/mainstream often partial rather than a full rad.

## Paid & andelsspel

| Channel | Notes | VAI |
|---------|-------|-----|
| Travtjänsten | Rank & Spel, Slutspelet, etc. | `travtjansten` |
| Travcash andelsspel | Pairs free tips with sold andelar | Holm, Pihlström, Sunnanängs, Grakka |
| Travstugan / Stridbeck | Andelar | `stridbeck` |
| MinAndel, Kopandel, Andelstorget | Marketplaces | MinAndel names in yaml; markets in expert.md §5 |

## Comparison vs VAI (scorecard)

| Category | Result |
|----------|--------|
| Free full-system **outlets** (5 + 2 hubs) | **100% already in VAI** |
| Core free **expert_ids** | **Match** |
| ATG / mainstream partial products | **Match** |
| Andel marketplaces | **Match**; VAI has more MinAndel names |
| **Net-new roster candidate** | **Eddie Östlund** (Travcash free tipster) |
| **Enrich notes only** | Trav.se writers; Trav365 Nicklasson/Carlsson; channels (email/FB) |
| **Flag review (optional)** | `thomas-uhrberg` partial vs full on 25/7; Travmaskinen builder vs fixed free matrix |
| VAI-only (not re-listed this pass) | Eight MinAndel spelläggare, fixture, Albin Kjellberg emphasis |

## Coverage / uncertainty

- ATG tip product pages often need JS; confirmed mainly via hubs/secondary sources.
- Whether every andelsspel spelläggare also publishes free public tips not fully verified per person.
- Frequency claims from multi-week archives visible July 2026, not exhaustive long-run schedules.
- Print/paywall (V85-Guiden, Travronden, Expressen Premium) not fully inspected.
- Travmaskinen: rankings + builder confirmed; single fixed free whole-system matrix not always on landing page.
- Social (Facebook/Discord/X) full-system dumps not sampled systematically.
- Not an exhaustive global catalogue; URLs change.

## Follow-ups (not done this session)

- [ ] Optional: add `eddie-ostlund` (or similar) to `experts.yaml` if free Travcash tips are transcribed regularly
- [ ] Optional: note Trav.se writers / Trav365 columnists in `source_note` when transcribing
- [ ] Optional: clarify `thomas-uhrberg` / Travmaskinen `publishes_full_system` semantics
- [ ] No auto-scrape — see [2026-07-27-deep-research-screen-scrape.md](./2026-07-27-deep-research-screen-scrape.md)

## Related

- Expert strategy: [docs/strategies/expert.md](../../docs/strategies/expert.md)
- Machine roster: [src/vai/strategies/experts.yaml](../../src/vai/strategies/experts.yaml)
- Prior directory: [2026-07-15-experts-travet.md](./2026-07-15-experts-travet.md)
- Ingest policy: [2026-07-27-deep-research-screen-scrape.md](./2026-07-27-deep-research-screen-scrape.md)
