# Local UI — v1.1 spec (Option B)

| Field | Value |
|-------|-------|
| **Version** | 0.1 |
| **Status** | APPROVED |
| **AIRUP phase** | R → P |
| **Reviewer** | Jonte |
| **Last updated** | 2026-07-07 |
| **Parent** | [scope-lock-v1-random.md](../../outbox/specs/scope-lock-v1-random.md) |

---

## 1. Purpose

Wire the **v0.5 ATG mockup** to the **random v1 generator** via a local HTTP API — no ATG fetch, no expert/quant.

## 2. Architecture

```
Browser (mockup HTML + JS)  →  localhost:8765  →  atg.server
                              GET  /api/v1/race-cards
                              GET  /api/v1/race-cards/{id}
                              POST /api/v1/generate/random
                              GET  /mockup/…  (static files)
```

- **Stack:** Python `http.server` (stdlib only), existing `generate_random_v1`.
- **Race cards:** `inbox/race-cards/*.yaml`
- **Mockup:** `outbox/mockups/v85-proposal-ux-mockup-atg.html` (+ JS inline)

## 3. API

### GET `/api/v1/race-cards`

```json
{"race_cards": [{"id": "2026-07-05-halmstad", "date": "2026-07-05", "track": "Halmstad"}]}
```

### GET `/api/v1/race-cards/{id}`

Full card JSON (legs, horses, scratches, reserves).

### POST `/api/v1/generate/random`

```json
{
  "race_card_id": "2026-07-05-halmstad",
  "pools": {"1": [2, 3], "2": [1], "...": "..."},
  "budget": 500,
  "seed": 42
}
```

Success `200`: selections, combinations, cost_sek, cost_breakdown, shrink_steps_used.

Error `400`: `{ "error": { "code", "message", "hint" } }`.

## 4. UX behaviour (v1.1)

1. On load: list race cards; default first card.
2. Render leg grid from API (horse toggles, scratches disabled).
3. All horses **pool-selected** by default (full pool).
4. **Generera system** → POST → update slip + cost sidebar.
5. Expert/Kvant tabs remain disabled.

## 5. Run

```powershell
pip install -e .
python -m atg serve
# Open http://127.0.0.1:8765/
```

## 6. Out of scope

- ATG live fetch (UC-09)
- PDF export button
- Expert / quant modes
- Hosted deployment / auth

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-07-07 | Initial spec — Option B |