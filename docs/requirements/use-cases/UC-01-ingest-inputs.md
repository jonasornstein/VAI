# UC-01 — Ingest inputs

| Field | Value |
|-------|-------|
| **ID** | UC-01 |
| **Status** | DRAFT |
| **Primary actor** | Operator, Agent, System |
| **Preconditions** | Raw material available, or UC-09 fetch triggered |

## Brief description

Capture inputs into `inbox/`. **Primary path:** system auto-collects race card from ATG (UC-09). **Fallback:** manual file or paste.

## Main success scenario — automatic (primary)

1. UC-09 invokes **F-007** `fetch_race_card_from_atg` (API preferred, website fallback **F-008**).
2. **F-004** `parse_race_card` and **F-005** `validate_race_card`.
3. **F-001** `store_race_card` → `inbox/race-cards/<date>-<track>.yaml` with `source: atg` and fetch timestamp.
4. Odds for quantitative mode: **F-009** `fetch_atg_odds` when available, else **F-002** manual `store_odds`.

## Main success scenario — manual (fallback)

1. Actor identifies input type: race card, odds, research, or request.
2. Actor prepares YAML per [race-card-schema.md](../race-card-schema.md) or uploads file.
3. Steps 2–3 of automatic path (parse, validate, store).

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 1a | ATG fetch fails | Notify operator; enable manual fallback |
| 3a | Duplicate date/track | Overwrite cache or version suffix |
| 4a | Odds fetch fails | Quantitative mode warns; operator may paste odds file |

## Functions invoked

F-001, F-002, F-003, F-004, F-005, F-007, F-008, F-009

## Special requirements

- [SUP-F-008](../supplementary-specification.md#1-functionality-cross-cutting)
- Glossary: [VISION.md §8 — Race card](../../VISION.md#8-glossary)