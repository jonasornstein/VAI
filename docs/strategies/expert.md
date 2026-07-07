# Expert strategy

| Field | Value |
|-------|-------|
| **Mode** | `expert` |
| **Owner** | Nisse (patterns), Povl (cost/math constraints) |
| **Status** | DRAFT |
| **Last updated** | 2026-07-06 |

---

## 1. Purpose

Generate systems based on **professional trotting experts' betting patterns** — typical spik/gardering structures, leg prioritization, and published or internal system templates used by experienced Swedish trav players.

## 2. Concept

Expert systems often:

- **Spik** (lock) legs perceived as high confidence
- **Gardera** (cover) legs perceived as open
- Allocate budget unevenly across legs (more horses where uncertainty is higher)
- Follow recurring templates (e.g. "3 spikar + 5 garderingar")

## 3. Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Race card | Yes | Eligible horses per leg |
| Expert template ID | No | Named pattern from catalog |
| Manual picks | No | Override per leg (Kricke/Jonte) |
| `target_cost_sek` | No | Budget guidance |

## 4. Template catalog (TBD — Nisse)

| Template ID | Description | Status |
|-------------|-------------|--------|
| `T-001` | Example: 4 spik + 4 garderingar | TBD |
| `T-002` | Example: budget gardering | TBD |

*Nisse to populate from real expert practice.*

## 5. Leg analysis (TBD — Nisse)

Document how experts classify legs:

- **Spikleg** — criteria for single-horse lock
- **Halvleg** — 2–3 horses
- **Öppen leg** — wide gardering

## 6. Outputs

Standard proposal format plus:

```yaml
mode: expert
template_id: <string or null>
leg_classification:
  1: spik
  2: gardering
  ...
rationale: <per-leg short notes>
```

## 7. Open requirements

- [ ] Template catalog (Nisse)
- [ ] Integration with quantitative odds as tie-breaker (Povl)
- [ ] Expert source attribution policy

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-07-06 | Initial draft |