# Source code

**v1 status:** Random mode vertical slice implemented per [random-v1.md](../pending/specs/random-v1.md).

## Layout

```
src/
├── atg/
│   ├── models/          # RaceCard, RandomResult, …
│   ├── io/              # YAML race card, pools, proposal markdown
│   ├── strategies/      # random.py (v1); expert/quant later
│   ├── cost.py          # F-060–F-062
│   └── cli.py           # CLI entry
tests/                   # pytest suite + golden seed test
```

## AIRUP for code

| Phase | Action |
|-------|--------|
| **A** | Requirement from SRS or user |
| **I** | Sample race cards in `inbox/race-cards/` |
| **R** | Design note in `pending/specs/` |
| **U** | Revise from Povl/M-005 review |
| **P** | Merged code + tests; proposal output to `outbox/` |

## Conventions

- Python 3.11+
- Type hints on public APIs
- No ATG API calls in v1