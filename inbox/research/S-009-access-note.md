# S-009 access issue — workaround for Nisse

| Field | Value |
|-------|-------|
| **Date** | 2026-07-06 |
| **Issue** | Original S-009 URL returns `403 Access Denied` (CloudFront/S3) |

## Blocked URL (do not use)

```
https://assets.ctfassets.net/hkip2osr81id/.../ATG_spelregler_ha..._2025__1_.pdf
```

## Replacement sources

| ID | Source | Access | Notes |
|----|--------|--------|-------|
| **S-009a** | [Betting Regulations EN (valid 2025-10-20)](https://www.swedishhorseracing.com/media/oqte5h0t/betting-regulations-english-version-valid-from-20251020.pdf) | **OK** (200) | Downloaded to `inbox/research/ATG-betting-regulations-en-20251020.pdf` |
| **S-009b** | [ATG regler och villkor](https://www.atg.se/hjalp/regler-och-villkor) | Browser | Swedish *Spelregler Häst* — authoritative per ATG; SPA page, download via logged-in browser |
| **S-009c** | [Download documents (SHR)](https://www.swedishhorseracing.com/for-partners/download-documents) | **OK** | Index page for regulations PDFs |

## Important caveat

The English PDF (S-009a) states:

> *All bets are governed by the applicable Swedish version ("Spelregler Häst") at www.atg.se.*

Pool distribution in the PDF (35/15/15/35) reflects **2025-10-20** rules.

**Supersession (verified 2026-07-06):** From **2026-07-02**, payout pools and jackpot thresholds are governed by **S-013 + N-004** (atg.se + ATG press). S-009a remains valid for V-betting **mechanics** (reserves §4–§6, dead heat §10, result §20) but **not** for current pool % or jackpot rules.

SHR download index (S-009c) still lists only the 2025-10-20 PDF — no newer regulations file published yet.

## Nisse review workflow

1. Review downloaded EN PDF for V-betting §4–§13 and V85 §1–§4 (mechanics).
2. Cross-check Swedish *Spelregler* via atg.se (S-009b) when updated PDF is available.
3. Use [v85-source-precedence.md](./v85-source-precedence.md) for payout/jackpot from 2026-07-02.