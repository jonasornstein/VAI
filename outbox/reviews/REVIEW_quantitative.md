# Review — quantitative.md

| Field | Value |
|-------|-------|
| **Artifact** | `docs/strategies/quantitative.md` v0.2-draft |
| **Reviewer** | Povl (agent lens) + Nisse (rules cross-check) |
| **Review type** | Agent review |
| **Date** | 2026-07-06 |
| **Verdict** | **APPROVE** (with notation fix) |

---

## Povl — math / quant

### Approved

- [x] **§2 Pool shares** — 30/20/15/35 sum to 1.00; matches [v85.md](../betting/v85.md) v1.0
- [x] **§2 Historical split** — 35/15/15/35 pre-2026-07-02 documented
- [x] **§2 Jackpot modelling** — v1 `nominal_pools` simplification explicit; 5→6 top-up correct
- [x] **§3 Cost** — \(N = \prod n_i\), \(C = Ns\), reduced \(C_\alpha = Ns\alpha\), \(D_\alpha = D\alpha\) — matches FR-013/FR-014
- [x] **§4 Hit probability** — exactly-\(k\) and at-least-\(k\) formulas correct under independence
- [x] **§4.4** — \(p_i = \sum_{h \in W_i} \pi_{i,h}\) with mutual-exclusivity caveat
- [x] **§5 Pool math** — \(P^{\text{pool}}_k = f_k \rho T\), \(D_k \approx P^{\text{pool}}_k / W^{\text{global}}_k\) structurally sound
- [x] **§5.1 EV modes** — hit-rate-only default for v1 appropriate without turnover data
- [x] **§8 Assumptions** — independence, jackpot ignore, proportional overround stated
- [x] **§9 Monte Carlo** — 10 000 runs default, seed for reproducibility (FR-022)
- [x] **§10 Output schema** — sufficient for implementation and operator transparency
- [x] **§11 Limitations** — win tax, EV data gaps disclosed

### Fixed in v0.3

1. **§5.1 notation** — \(P_k\) overloaded (pool vs. hit probability). Renamed to \(P^{\text{pool}}_k\) and \(P_{\text{you}}(k)\).

### Deferred (v1.1+, documented in §12)

- [ ] Shin / power overround
- [ ] Full EV with live turnover / \(W_k\)
- [ ] Dead-heat multiplier in Monte Carlo
- [ ] Probability input schema in `inbox/`

---

## Nisse — rules alignment

- [x] Pool %, jackpot thresholds, reduced-stake scaling align with v85.md v1.0
- [x] Dead heat note (§3.1) consistent with S-009a §10 — payout effect, not row count
- [x] System limits match approved rules
- [x] `effective_date` selector for historical pools — correct

No rule conflicts found.

---

## Operator — proposal usability

- [x] Output YAML includes `rows`, `cost_sek`, `stake_factor` — matches ATG entry verification
- [x] Hit probabilities aid race-day rationale without requiring EV

---

## SRS coverage

| ID | Status |
|----|--------|
| FR-013 / FR-014 | Covered §3 |
| FR-040 | Covered §6, §8 |
| FR-041 | Covered §9 (draft detail sufficient for v1) |
| FR-042 | Covered §11 |
| FR-043 | Covered §8 objective + §7 pipeline |
| FR-051 | Consolation tiers §5.3 |

---

## Verdict rationale

Phase 2 quant spec is **implementation-ready for v1** (hit-rate optimisation under budget). EV and advanced overround remain optional extensions with clear open items.

**Action:** Mark `quantitative.md` **APPROVED** v0.3; archive review to `outbox/reviews/`.