# Expert tips (AIRUP Inbox)

Raw **professional betslip** transcriptions for Expert mode (UC-12).

## Layout

```
expert-tips/
  <YYYY-MM-DD>-<track-slug>/
    <tip_id>.yaml
```

Example: `2026-07-18-axevalla/fixture-axevalla-2026-07-18.yaml`

## How to add a tip

### UI (preferred for race day)

1. Open the local UI (`python -m vai serve`) → **Expert** tab.
2. Choose **Datum** and **Bana**.
3. Click the small form icon to the left of **Gratis** / **Andel/betald** on the expert’s roster card.
4. Enter horse numbers per avdelning (e.g. `2, 3, 5`), optional **Produkt / systemnamn**, source URL / note, then **Spara**.
5. The tip is written under this directory; the card shows **Redo** (or **N tips**) when tip(s) exist for the omgång.

**Multiple systems per expert** are supported for the same date/track (e.g. Stora + Lilla). Use **+ Nytt tips** in the form to add another; each gets its own `tip_id` (`expert-date`, `expert-date-2`, …). Distinguish them with `product_name`. Editing always updates the selected tip only.

First open for that expert + date + track is empty; later opens list existing tips. **Avbryt** discards changes.

### Manual YAML

1. Open the expert’s published system (e.g. Björnkollen on atg.se).
2. Copy horse numbers per V85 leg into a new YAML file (schema below).
3. Set `source_url` and `source_note` for attribution.
4. Keep status `DRAFT` until double-checked against the official tip and race card.

## Schema (required fields)

```yaml
tip_id: my-tip-id
expert_id: bjorn-goop
expert_name: Björn Goop
product_name: Björnkollen
game: v85
date: "2026-07-18"
track: Axevalla
source_url: "https://www.atg.se/..."
source_note: "Transcribed by ornstein"
fetched_at: "2026-07-18T10:00:00Z"
status: DRAFT
legs:
  1: [3]
  2: [1, 5]
  3: [2]
  4: [4, 7, 9]
  5: [1]
  6: [8, 11]
  7: [2, 3, 6]
  8: [5]
rationale: "Optional note"
```

## Expert roster

Use `expert_id` from the **effective roster** (UI Expert tab, or API `GET /api/v1/experts`):

- Working copy (if customized): [inbox/experts/roster.yaml](../experts/roster.yaml)
- Shipped defaults: [src/vai/strategies/experts.yaml](../../src/vai/strategies/experts.yaml)
- Human catalog: [docs/strategies/expert.md](../../docs/strategies/expert.md) §4
- Add/remove experts in UI: [inbox/experts/README.md](../experts/README.md)

Research directory of outlets/experts:

- [inbox/research/2026-07-15-experts-travet.md](../research/2026-07-15-experts-travet.md)

**Priority free sources for transcription:** Travcash (Referenten), Travstugan, Trav.se, Rekatochklart (Leboff), Travmaskinen, Expressen Systemet, ATG Björnkollen.

## Policy

- Private operator use only.
- Attribute the expert and product.
- Do not commit paywalled full-text articles — horse numbers + metadata only.
