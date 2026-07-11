# Local UI — v1.1 spec (Option B)

| Field | Value |
|-------|-------|
| **Version** | 0.2 |
| **Status** | APPROVED |
| **AIRUP phase** | R → P |
| **Reviewer** | ornstein |
| **Last updated** | 2026-07-07 |
| **Parent** | [scope-lock-v1-random.md](./scope-lock-v1-random.md) |
| **Related** | [random-v1.1.md](./random-v1.1.md), [atg-data-source.md](./atg-data-source.md) |

---

## 1. Purpose

Wire the **ATG mockup** to the **Hari (random) generator** via a local HTTP API, with live ATG schedule and race cards.

## 2. Architecture

```
Browser (mockup HTML + JS)  →  localhost:8765  →  atg.server
                              GET  /api/v1/schedule/v85
                              GET  /api/v1/race-cards
                              GET  /api/v1/race-cards/{id}
                              POST /api/v1/generate/random
```

- **Stack:** Python `http.server` (stdlib), `generate_random_v1`, ATG fetch helpers.
- **Race cards:** ATG `game_id` (primary) or `inbox/race-cards/*.yaml`
- **Mockup:** `outbox/mockups/v85-proposal-ux-mockup-atg.html`

## 3. API

### GET `/api/v1/schedule/v85`

Schedule dates and rounds (`game_id`, track, `default_date`).

### GET `/api/v1/race-cards/{id}`

Full card JSON. ATG ids include optional `leg_distributions` for F-052.

### POST `/api/v1/generate/random`

```json
{
  "race_card_id": "V85_2026-07-11_31_5",
  "pools": {"1": [], "2": [5], "...": "..."},
  "budget": 500,
  "seed": 42,
  "frozen_legs": [3]
}
```

Success `200`: selections, `cost_sek`, `cost_breakdown`, optional `hit_summary`.

Error `400`: `BUDGET_NOT_MET` may include `suggested_stake_sek`, `suggested_combinations`.

## 4. UX behaviour (v1.1)

1. On load: fetch V85 schedule; populate DATUM/BANA; load race card.
2. Horse toggles: optional operator marks (orange); random fill on generate.
3. **Frys avd.** — frozen legs require marks.
4. **Generera system** — exact SYSTEMKOSTNAD; nearest-stake confirm on failure.
5. **Träffsannolikhet** — bars when `leg_distributions` present.
6. **Hari** tab active; Expert/Kvant disabled.
7. **Skriv ut spelkvitto** / **Öppna ATG/{spelform}** — manual entry only.

## 5. Run

```powershell
pip install -e .
python -m atg serve
# Open http://127.0.0.1:8765/
```

## 6. Out of scope

- Expert / quant modes
- Other spelform (V75 discontinued at ATG; V86/V64 TBD)
- Hosted deployment / auth
- Automated bet placement

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.2 | 2026-07-07 | ATG schedule/cards, Hari UX, exact budget, hit summary, nearest stake |
| 0.1 | 2026-07-07 | Initial spec — Option B |