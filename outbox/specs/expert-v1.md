# Expert mode — v1 implementation spec (expert betslips)

| Field | Value |
|-------|-------|
| **Version** | 0.1 |
| **Status** | APPROVED |
| **AIRUP phase** | P |
| **Reviewer** | ornstein (UX), Nisse (roster), Povl (cost) |
| **Author** | Assistant (plan approved 2026-07-15) |
| **Last updated** | 2026-07-15 |
| **Implements** | UC-12 v1.1, F-040–F-043 |
| **Product line** | Expert v1.0 / package **1.3.x** (v1.2 reserved for reduced-stake/cache) |

---

## 1. Purpose

Document Expert mode as **selection of professional published betslips**, not random fill and not pattern templates.

---

## 2. Resolved decisions

| ID | Topic | Decision |
|----|-------|----------|
| EX-001 | Product shape | List expert tips → select one → load slip |
| EX-002 | Ingestion | Manual YAML under `inbox/expert-tips/` (AIRUP I); no scraper in v1 |
| EX-003 | Budget | Tip defines cost; no exact SYSTEMKOSTNAD fill |
| EX-004 | Operator pools | Not required for load |
| EX-005 | Overrides | Optional per-leg horse list after select (F-043) |
| EX-006 | Attribution | Manifest + proposal cite expert, product, source_url/note |
| EX-007 | Privacy | Private operator use; attribute; no public rebroadcast of full tips |

---

## 3. Tip artifact schema

Path: `inbox/expert-tips/<YYYY-MM-DD>-<track-slug>/<tip_id>.yaml`

| Field | Required | Description |
|-------|----------|-------------|
| `tip_id` | Yes | Unique string |
| `expert_id` | Yes | Roster key e.g. `bjorn-goop` |
| `expert_name` | Yes | Display name |
| `product_name` | No | e.g. Björnkollen |
| `game` | Yes | `v85` |
| `date` | Yes | ISO date |
| `track` | Yes | Track name |
| `source_url` | No | Attribution URL |
| `source_note` | No | Transcription note |
| `fetched_at` | No | ISO timestamp |
| `status` | No | `DRAFT` \| `REVIEW` \| `READY` (default READY for list) |
| `legs` | Yes | Map `1`..`8` → list of horse numbers (≥1 each) |
| `rationale` | No | Short note |

List API may filter `status` to READY only, or include all non-invalid files (v1: all valid files).

---

## 4. Algorithm

1. Parse tip YAML; validate 8 legs, non-empty horse lists, unique numbers per leg.
2. If `race_card` provided: every horse ∈ eligible field; none in scratches.
3. Apply overrides (replace listed legs).
4. `combinations`, `cost_sek` via shared cost module (× 0.50 SEK).
5. Emit `ExpertResult` with manifest (`mode=expert`, tip/expert metadata).

### Error codes

| Code | When |
|------|------|
| `INVALID_TIP` | Schema/parse failure |
| `TIP_NOT_FOUND` | Unknown tip_id |
| `INVALID_HORSE` | Horse not on race card |
| `SCRATCHED_HORSE` | Horse scratched |
| `EMPTY_LEG` | Override or tip left a leg empty |
| `UNSUPPORTED_GAME` | game ≠ v85 |

---

## 5. API

### GET `/api/v1/expert-tips?date=YYYY-MM-DD&track=optional`

```json
{
  "tips": [
    {
      "tip_id": "…",
      "expert_id": "bjorn-goop",
      "expert_name": "Björn Goop",
      "product_name": "Björnkollen",
      "date": "2026-07-18",
      "track": "Axevalla",
      "combinations": 96,
      "cost_sek": 48.0,
      "cost_breakdown": "1×1×2×…",
      "source_url": null,
      "status": "READY"
    }
  ]
}
```

### POST `/api/v1/generate/expert`

```json
{
  "race_card_id": "…",
  "tip_id": "fixture-axevalla-2026-07-18",
  "overrides": { "3": [1, 2] }
}
```

Success: `selections`, `combinations`, `cost_sek`, `cost_breakdown`, expert fields, optional `hit_summary`.

---

## 6. CLI

```text
python -m vai expert list [--date DATE] [--track TRACK] [--tips-dir PATH]
python -m vai expert apply --tip TIP_ID --race-card PATH --out PATH [--overrides PATH]
```

---

## 7. Operator UX

| Control | Behaviour |
|---------|-----------|
| Expert tab | Enabled |
| Tip list | Shows experts for current date/track |
| Select tip | Loads horses into grid + slip |
| Generera / Ladda | POST generate/expert (or load on select) |
| Hari controls | Seed, Frys, exact budget fill hidden/disabled in Expert |
| Rationale | Expert name + product + tip_id |
| Kvantitativ | Still disabled |

---

## 8. Non-goals

- Pattern template engine (old UC-12)
- ATG tip scraping
- UC-13 quantitative
- Reduced-stake α

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-07-15 | Initial expert betslip spec |
