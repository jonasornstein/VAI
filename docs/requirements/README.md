# VAI — Requirements Package (RUP)

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Status** | APPROVED |
| **Reviewer** | ornstein |
| **Approved** | 2026-07-07 |
| **Last updated** | 2026-07-07 |
| **Methodology** | IBM RUP + [AIRUP](../AIRUP.md) |
| **Owner** | ornstein (M-004) |

The monolithic [SRS](../SRS.md) is split into three RUP artifacts. Each has a single concern; cross-references replace duplication.

---

## The three artifacts

| # | RUP artifact | File | Replaces (traditional SRS) | Owner |
|---|--------------|------|----------------------------|-------|
| 1 | **Vision** | [VISION.md](../VISION.md) | Introduction, scope, stakeholders, goals | ornstein |
| 2 | **Use-Case Model & Specifications** | [use-case-model.md](./use-case-model.md) + [use-cases/](./use-cases/) + [functions.md](./functions.md) | Functional requirements (`FR-*`) | ornstein / operators / Povl / Nisse |
| 3 | **Supplementary Specification** | [supplementary-specification.md](./supplementary-specification.md) | Non-functional requirements (`NFR-*`), interfaces, constraints | ornstein / Povl |

---

## AIRUP workflow for requirements

| Phase | Location | Activity |
|-------|----------|----------|
| **A** Analyze | Task scope | Identify which artifact(s) change; assign reviewer |
| **I** Inbox | `inbox/requests/` | Raw briefs, operator notes, new function ideas |
| **R** Review | `pending/requirements/` | Draft use cases, vision updates, supplementary changes |
| **U** Update | `pending/requirements/` | Revise from ornstein / Kricke / ornstein / Nisse / Povl feedback |
| **P** Publish | `docs/requirements/`, `docs/VISION.md` | Promote approved specs to `docs/` |

**Review gates:**

| Artifact | Default reviewer |
|----------|------------------|
| Vision | ornstein |
| Operator-facing use cases | Kricke or ornstein |
| Quant / simulation use cases | Povl |
| Rules / compliance use cases | Nisse |
| Supplementary (security, regulatory) | ornstein + Nisse |

---

## Traceability

- Legacy `FR-*` and `NFR-*` IDs map to use cases and supplementary sections in [SRS.md](../SRS.md#traceability).
- Implementation specs in `pending/specs/` SHALL reference use case IDs (`UC-*`).
- [TRACE-LOG.md](../TRACE-LOG.md) logs promotion of requirements to `docs/`.

---

## Supporting specs

| Document | Purpose |
|----------|---------|
| [functions.md](./functions.md) | System function catalog (`F-*`) |
| [race-card-schema.md](./race-card-schema.md) | Race card YAML format (auto-fetched from ATG) |
| [ux-workflow.md](./ux-workflow.md) | Operator UX: DATUM, BANA, horse picks, SYSTEMKOSTNAD |

## Status (2026-07-07)

RUP trilogy **APPROVED** for v1.1: Vision, use-case model + all UCs, functions catalog, supplementary spec, ux-workflow, race-card-schema.

**Next:** v1.2 specs (reduced-stake, disk cache); UC-12/13 implementation when modes enabled.