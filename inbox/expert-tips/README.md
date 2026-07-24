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

Use `expert_id` from:

- [docs/strategies/expert.md](../../docs/strategies/expert.md) §4
- [src/vai/strategies/experts.yaml](../../src/vai/strategies/experts.yaml)

Research directory of outlets/experts:

- [inbox/research/2026-07-15-experts-travet.md](../research/2026-07-15-experts-travet.md)

**Priority free sources for transcription:** Travcash (Referenten), Travstugan, Trav.se, Rekatochklart (Leboff), Travmaskinen, Expressen Systemet, ATG Björnkollen.

## Policy

- Private operator use only.
- Attribute the expert and product.
- Do not commit paywalled full-text articles — horse numbers + metadata only.
