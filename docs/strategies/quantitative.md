# Quantitative strategy

| Field | Value |
|-------|-------|
| **Mode** | `quantitative` |
| **Owner** | Povl |
| **Status** | APPROVED |
| **Version** | 0.3 |
| **Last updated** | 2026-07-06 |
| **Review** | [REVIEW_quantitative.md](../../outbox/reviews/REVIEW_quantitative.md) |
| **Rules baseline** | [v85.md](../betting/v85.md) v1.0 APPROVED |

---

## 1. Purpose

Generate systems using **mathematical models** — probability estimates, odds comparison, expected value, and optionally **Monte Carlo simulation** of race outcomes across legs.

Quantitative proposals must use the **same cost and payout mechanics** as ATG. Game rules: Nisse ([v85.md](../betting/v85.md)). This document: Povl (math).

---

## 2. V85 parameters (2026-07-02+)

Canonical rules: [docs/betting/v85.md](../betting/v85.md). Use **historical** pool split only for rounds before **2026-07-02**.

| Parameter | Symbol | Value |
|-----------|--------|-------|
| Legs | \(L\) | 8 |
| Ordinary row price | \(s\) | 0.50 SEK |
| Return to players (RTP) | \(\rho\) | 0.65 |
| Win tax (on dividends) | — | 35% (operator payout; exclude from pool math unless modelling net-to-player) |
| Reduced-stake factors | \(\alpha\) | 0.30, 0.50, 0.70 |

### 2.1 Pool shares (current)

Fraction of **player return** allocated to each winning tier (8 / 7 / 6 / 5 correct):

| Tier \(k\) | Share \(f_k\) | Notes |
|------------|---------------|-------|
| 8 | 0.30 | Jackpot if no winners or dividend \< 5 SEK |
| 7 | 0.20 | — |
| 6 | 0.15 | Jackpot if dividend \< 7 SEK (after 5→6 top-up) |
| 5 | 0.35 | No jackpot; if dividend \< 5 SEK → top-up to 6-pool |

\(\sum_k f_k = 1.00\)

**Historical (2025-10-25 – 2026-07-01):** \(f_8=0.35, f_7=0.15, f_6=0.15, f_5=0.35\); jackpot threshold **5 SEK** on all tiers.

### 2.2 Jackpot thresholds (modelling)

| Tier | Condition | Model treatment (v1) |
|------|-----------|-------------------|
| 5 | Dividend \< 5 SEK | Funds **reallocated to tier 6** (not jackpot) |
| 6 | Dividend \< 7 SEK | Treat as **jackpot carry** to next ordinary round |
| 8 | No winners or \< 5 SEK | Jackpot carry to next ordinary round |

**v1 simplification:** Unless historical jackpot inputs are provided (`inbox/`), assume **no jackpot overlay** and use nominal pool shares \(f_k\). Flag `jackpot_assumption: nominal_pools` in proposal metadata.

### 2.3 System limits (constraints)

| Constraint | Value |
|------------|-------|
| Max systems / account / round | 5 000 |
| Max rows / coupon (reduced stake) | 4 000 |
| Max coupons / customer (reduced stake) | 3 |

---

## 3. System cost

Per FR-013 / FR-014.

### 3.1 Row count

For leg \(i = 1..L\), let \(n_i\) = horses marked in leg \(i\).

```
N = ∏ n_i
```

**Dead heat:** If multiple horses tied for 1st are **all marked**, each counts as a winner; \(n_i\) already reflects marked horses. Dividend share for a row that hits multiple dead-heat winners in a leg uses the **product rule** (ATG V-betting §10) — affects **payout per winning row**, not \(N\).

### 3.2 Ordinary cost

```
C = N × s = N × 0.50 SEK
```

### 3.3 Reduced stake (*sänkt insats*)

Mathematical systems only. Stake factor \(\alpha \in \{0.30, 0.50, 0.70\}\):

```
C_α = N × s × α
```

If dividend at ordinary stake would be \(D\), reduced-stake dividend:

```
D_α = D × α
```

**Example:** \(D = 1{,}000{,}000\) SEK → \(D_{0.30} = 300{,}000\) SEK.

---

## 4. Hit probability (leg independence)

**Assumption (v1):** Leg outcomes are **independent** given model probabilities. Document in every proposal.

For leg \(i\), let \(W_i\) = set of marked horses, \(p_i = P(\text{winner} \in W_i)\).

### 4.1 Exact tier probability

Probability of **exactly** \(k\) correct legs (standard inclusion over subsets):

\[
P(\text{exactly } k) = \sum_{S \subseteq \{1..L\}, |S|=k} \left( \prod_{i \in S} p_i \cdot \prod_{j \notin S} (1 - p_j) \right)
\]

### 4.2 At-least tier

\[
P(\geq k) = \sum_{j=k}^{L} P(\text{exactly } j)
\]

### 4.3 All legs correct

\[
P(8) = \prod_{i=1}^{L} p_i
\]

### 4.4 From win probabilities per horse

If horse \(h\) in leg \(i\) has model probability \(\pi_{i,h}\) and \(W_i\) is the marked set:

\[
p_i = \sum_{h \in W_i} \pi_{i,h}
\]

**Caveat:** If two horses in \(W_i\) are mutually exclusive winners, sum is correct. Correlated outcomes (same trainer tactics, track bias) violate independence — disclose in limitations.

---

## 5. Payout pool mathematics

Let \(T\) = total pool turnover (all tickets), \(\rho T\) = player return. Tier \(k\) pool:

\[
P^{\text{pool}}_k = f_k \cdot \rho T
\]

For a given round, ATG divides \(P^{\text{pool}}_k\) among **winning rows** at tier \(k\). If \(W^{\text{global}}_k\) = count of winning rows across all bettors:

\[
D_k \approx \frac{P^{\text{pool}}_k}{W^{\text{global}}_k} \quad \text{(SEK per row at ordinary stake)}
\]

### 5.1 Modelling expected return (sketch)

For **your** system with \(N\) rows and stake \(s\) (or \(s \cdot \alpha\)):

\[
\text{EV} \approx \sum_{k=5}^{8} P_{\text{you}}(k) \cdot E[\text{dividend}_k \mid \text{win at } k]
\]

where \(P_{\text{you}}(k)\) = probability **your** system wins at tier \(k\) (from §4).

**v1:** Without full-market \(W^{\text{global}}_k\) and turnover \(T\), implementations may use:

| Approach | Input needed |
|----------|----------------|
| **Hit-rate only** | Report \(P(\geq k)\); no SEK EV |
| **Scaled pool** | Estimated \(T\) from ATG omsättning + estimated \(W_k\) |
| **Historical dividend** | Past V85 utdelning at tier \(k\) as proxy |

**Must disclose** which approach is used in proposal metadata.

### 5.2 Turnover contribution

Your contribution to turnover: \(N \cdot s\) (or \(N \cdot s \cdot \alpha\)). Share of tier pool is **not** proportional to your rows alone — depends on global \(W^{\text{global}}_k\).

### 5.3 Consolation structure

V85 pays **8, 7, 6, and 5** correct. Quant models should support evaluating **multiple tiers**, not only \(P(8)\).

---

## 6. Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Race card | Yes | Eligible horses per leg |
| Win probabilities or odds | Yes | Per horse per leg → \(\pi_{i,h}\) |
| `effective_date` | Yes | Select pool split pre/post 2026-07-02 |
| `stake_factor` | No | 1.0 (ordinary) or 0.30 / 0.50 / 0.70 |
| `max_cost_sek` | No | Budget cap on \(C\) or \(C_\alpha\) |
| `max_rows` | No | Default min(4000, budget-implied) for reduced stake |
| `simulation_runs` | No | Monte Carlo iterations |
| `pool_turnover_sek` | No | For EV mode only |
| Model config | No | See §8 |

---

## 7. High-level pipeline

```
1. Load v85.md parameters for effective_date
2. Ingest odds/probabilities → π_{i,h}
3. Normalize / de-overround (method configurable)
4. Build selections per leg → n_i, p_i
5. Compute N, C (or C_α)
6. Compute P(exactly k), P(≥k) for k = 5..8
7. Optionally estimate EV if turnover / W_k available
8. Optionally Monte Carlo validate independence model
9. Emit proposal with model metadata
```

---

## 8. Model assumptions

| Assumption | v1 default | Notes |
|------------|------------|-------|
| Leg independence | **Yes** | Required disclosure |
| Win probability source | Input odds or manual | Source in metadata |
| Overround removal | **Proportional** | **Approved v1 default**; see §8.1 |
| Objective function | **Maximize P(≥7)** under budget | **Approved v1 default**; alt: P(8), weighted EV |
| Jackpot overlay | **Ignored** unless data provided | See §2.2 |
| Pool turnover | **Unknown** unless ingested | EV mode optional |

### 8.1 Overround (draft)

For leg \(i\) with implied probabilities \(\tilde{\pi}_{i,h}\) from odds:

\[
Z_i = \sum_h \tilde{\pi}_{i,h} \quad (\text{typically } > 1)
\]

Proportional normalization:

\[
\pi_{i,h} = \frac{\tilde{\pi}_{i,h}}{Z_i}
\]

**Open:** Shin / power method for favourite–longshot bias — Povl to specify if v1.1.

---

## 9. Monte Carlo (optional)

If enabled:

1. For each run, draw winner per leg from \(\{\pi_{i,h}\}\) (mutually exclusive per leg).
2. Count correct legs per row in system (up to \(N\) rows or sample).
3. Aggregate tier hit rates; compare to §4 analytic results.

**Specify:** `simulation_runs` default **10 000**; seed parameter for reproducibility (FR-022).

---

## 10. Outputs

Standard proposal format (see [03-documentation.md](../../.grok/rules/03-documentation.md)) plus:

```yaml
mode: quantitative
model_version: "0.3"
effective_date: "2026-07-06"
rules_baseline: "docs/betting/v85.md v1.0"
stake_factor: 1.0          # or 0.30 / 0.50 / 0.70
rows: 48
cost_sek: 24.00
pool_shares: {8: 0.30, 7: 0.20, 6: 0.15, 5: 0.35}
hit_probability:
  exactly_8: 0.0012
  exactly_7: 0.0089
  at_least_7: 0.0101
  at_least_6: 0.042
objective: maximize_p_ge_7
assumptions:
  leg_independence: true
  jackpot_assumption: nominal_pools
  overround_method: proportional
probabilities_source: atg_odds
per_leg_summary:
  1:
    selected: [3, 7]
    n_horses: 2
    p_winner_in_set: 0.42
```

---

## 11. Limitations (disclose in proposals)

- Past performance and model error
- Odds movement before race time
- Leg independence may not hold
- EV estimates require turnover / winner-row counts not in v1 core
- No guarantee of positive expected value
- Win tax (35%) not deducted in gross dividend formulas above

---

## 12. Open requirements (Povl)

- [x] V85 pool % and jackpot thresholds (2026-07-02+)
- [x] Row/cost formula — 0.50 SEK, FR-013/FR-014
- [x] Reduced-stake payout scaling
- [ ] Probability input format (`inbox/` schema)
- [x] Default objective function — maximize P(≥7) under budget (v1)
- [x] Overround method — proportional (v1); Shin deferred to v1.1
- [ ] Monte Carlo spec detail (FR-041)
- [ ] EV mode: turnover ingestion path
- [ ] Pre-2026-07-02 round selector in code
- [ ] Dead-heat payout multiplier in simulation

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.3 | 2026-07-06 | AIRUP review APPROVE; notation fix §5; v1 defaults locked |
| 0.2-draft | 2026-07-06 | Phase 2 — V85 pool math, cost, hit probability, EV sketch |
| 0.1 | 2026-07-06 | Initial draft |