# UC-31 — Maintain strategy specs

| Field | Value |
|-------|-------|
| **ID** | UC-31 |
| **Status** | DRAFT |
| **Primary actor** | Quant analyst |
| **Preconditions** | Strategy mode scope defined (random / expert / quantitative) |

## Brief description

Author and approve strategy specifications that drive UC-11, UC-12, UC-13 implementation.

## Main success scenario

1. Analyst identifies mode doc to update (`random`, `expert`, `quantitative`).
2. **F-102** `draft_strategy_spec` — inputs, algorithm, outputs, assumptions, open items.
3. Draft in `pending/specs/` or direct edit `docs/strategies/<mode>.md` with `DRAFT` status.
4. Povl reviews; quant proposals using model require **F-012** → `APPROVED`.
5. **F-103** `promote_strategy_spec` → `docs/strategies/<mode>.md`.
6. **F-081** review record if major version (e.g. quantitative v0.3).
7. Implementation in `src/atg/strategies/` references spec version in code comments.

## Extensions

| Step | Condition | Action |
|------|-----------|--------|
| 2a | Expert templates | Nisse co-authors expert.md catalog section |
| 4a | Expert-only pattern | Nisse review without full quant sign-off |

## Functions invoked

F-102, F-103, F-081, F-012, F-014

## Special requirements

- Quant gate in [AIRUP.md](../../AIRUP.md)
- Approved: [quantitative.md](../../strategies/quantitative.md) v0.3