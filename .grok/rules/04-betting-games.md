# Betting Games — Overview

## Priority: V85

**V85®** is ATG's Saturday Pick8 pool for trotting — pick the winner in **8 predetermined races**.

| Attribute | Value |
|-----------|-------|
| Schedule | Saturdays, various Swedish tracks |
| Legs | 8 |
| Type | Pick8 / system game |
| Min stake | 0.50 SEK per combination |
| Cost | ∏(horses selected per leg) × 0.50 SEK |
| Payouts | 8 correct = main pool; consolation for 7, 6, 5 correct |

Full rules: [docs/betting/v85.md](../../docs/betting/v85.md) (Nisse-maintained).

## Future games (not yet specified)

| Game | Legs | Status |
|------|------|--------|
| V75 | 7 | Planned — doc TBD |
| V86 | 8 | Planned — doc TBD |
| V64 | 6 | Planned — doc TBD |
| DD (Daily Double) | 2 | Planned — doc TBD |

When adding a game:

1. Nisse authors `docs/betting/<game>.md`
2. Povl adds strategy constraints if needed
3. Add generator module under `src/` and skill variant if warranted
4. Update this file and AGENTS.md

## ATG official references

- [atg.se/v85](https://www.atg.se/v85)
- [Swedish Horse Racing — V85](https://www.swedishhorseracing.com/our-games/v85)
- [ATG betting regulations](https://www.swedishhorseracing.com/our-games/betting-regulations) (download official PDF)

Agents must treat official ATG regulations as superseding project docs when they conflict. Flag discrepancies for Nisse to reconcile.