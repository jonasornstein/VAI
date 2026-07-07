# Trotting fundamentals (Swedish trav)

| Field | Value |
|-------|-------|
| **Owner** | Nisse |
| **Status** | DRAFT |
| **Last updated** | 2026-07-06 |

Core concepts for agents and developers working on ATG betting systems.

---

## 1. What is trotting?

**Trotting** (*trav*) is harness racing: horses pull a two-wheeled cart called a **sulky** (*vagn*). In Sweden, trotting is governed by [ST](https://www.travsport.se/) (Svensk Travsport) and bet on through **ATG** (AB Trav och Galopp).

---

## 2. Race basics

| Concept | Description |
|---------|-------------|
| **Start number** | The number a horse carries in a race (used in betting systems) |
| **Distance** | Often 1640m, 2140m, 2640m, etc. |
| **Start method** | Auto start (*voltstart*) or line start (*autostart*) |
| **Class** | Ability/handicap grouping (e.g. class levels, qualifications) |

---

## 3. Key Swedish terms

| Swedish | English | Notes |
|---------|---------|-------|
| Trav | Trotting | |
| Avdelning | Leg / division | In multi-race pools |
| Spik | Banker / single pick | One horse locked in a leg |
| Gardering | Coverage | Multiple horses in a leg |
| System | Combination bet | Product across legs |
| Utdelning | Dividend / payout | |
| Struken | Scratched | Horse withdrawn |
| Km-tid | Kilometer time | Performance measure |

---

## 4. What affects race outcomes (high level)

*Nisse to expand — this is a stub for agents.*

- Form and recent results
- Driver (*kusk*) and trainer
- Starting position and distance
- Equipment changes (shoes, sulky type)
- Track condition and weather
- Class and handicap changes

---

## 5. ATG multi-leg pools

ATG runs several **multi-leg** games where the same principles apply: pick winners across multiple races, pay by combinations.

| Game | Legs | Notes |
|------|------|-------|
| V85 | 8 | Priority for this project |
| ~~V75~~ | 7 | **Discontinued** at ATG (no longer offered) |
| V86 | 8 | Variant schedule — TBD |
| V64 | 6 | Smaller pool — TBD |

---

## 6. Open research (Nisse backlog)

- [ ] Disqualification and betting settlement
- [ ] Reserve horse rules per ST/ATG
- [x] V75 discontinued — no separate v75.md planned
- [ ] 2026 jackpot rule changes

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-07-06 | Initial stub |