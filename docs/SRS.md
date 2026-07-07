# ATG — Software Requirements Specification (Index)

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Status** | DRAFT |
| **Last updated** | 2026-07-06 |
| **Model** | IBM RUP — monolithic SRS split into three artifacts |
| **Owner** | Jonte (M-004) |

The traditional SRS is **decomposed** per IBM RUP. This file is the **index and traceability hub** — not the primary home for new requirements.

---

## 1. RUP requirements trilogy

| Artifact | Document | Content |
|----------|----------|---------|
| **Vision** | [VISION.md](./VISION.md) | Problem, scope, stakeholders, goals, non-goals, roadmap |
| **Use-Case Model & Specifications** | [requirements/use-case-model.md](./requirements/use-case-model.md) + [requirements/use-cases/](./requirements/use-cases/) | Actors, diagram, step-by-step functional narratives |
| **Supplementary Specification** | [requirements/supplementary-specification.md](./requirements/supplementary-specification.md) | FURPS+ non-functional, interfaces, regulatory |

Package overview and AIRUP workflow: [requirements/README.md](./requirements/README.md).

---

## 2. Where to add new requirements

| Type | Draft in | Publish to | Reviewer |
|------|----------|------------|----------|
| Vision / scope change | `pending/requirements/` | `docs/VISION.md` | Jonte |
| New use case or function | `pending/requirements/use-cases/` | `docs/requirements/use-cases/` | Per UC (see README) |
| NFR, interface, constraint | `pending/requirements/` | `docs/requirements/supplementary-specification.md` | Jonte / Povl / Nisse |
| Implementation detail | `pending/specs/` | `src/` (after review) | Povl |

**Do not** add new `FR-*` or `NFR-*` rows here. Use `UC-*` and `SUP-*` IDs in the RUP artifacts.

---

## 3. Traceability

### 3.1 Functional requirements (legacy FR → UC)

| Legacy ID | Summary | Use case |
|-----------|---------|----------|
| FR-000 | AIRUP workflow mandatory | UC-02 |
| FR-001a | Raw inputs in `inbox/` | UC-01 |
| FR-001b | Drafts in `pending/` with status | UC-02, UC-20 |
| FR-001c | Only APPROVED → `outbox/` | UC-21 |
| FR-001d | Log in TRACE-LOG | UC-02 |
| FR-001 | Maintain `docs/betting/v85.md` | UC-30 |
| FR-002 | Maintain `docs/strategies/` | UC-31 |
| FR-003 | Version major docs | SUP-S-004 |
| FR-010–016 | Proposal generation common | UC-10, UC-14 |
| FR-020–022 | Random mode | UC-11 |
| FR-030–032 | Expert mode | UC-12 |
| FR-040–043 | Quantitative mode | UC-13 |
| FR-050–051 | V85-specific legs / consolation | UC-30, SUP-F-003, SUP-F-005 |

### 3.2 Non-functional requirements (legacy NFR → SUP)

| Legacy ID | Summary | Supplementary ID |
|-----------|---------|------------------|
| NFR-001 | Readable in &lt; 2 min | SUP-U-001 |
| NFR-002 | Offline-capable generation | SUP-R-001 |
| NFR-003 | Agent context from AGENTS.md | SUP-S-002 |
| NFR-004 | Extensible game structure | SUP-S-001, SUP-D-004 |
| NFR-005 | AIRUP skills available | SUP-S-003, SUP-F-006 |

---

## 4. Acceptance criteria (v1)

1. Three modes each produce a valid V85 proposal for a sample race card. *(UC-10, UC-11–13)*
2. Nisse signs off on `docs/betting/v85.md`. ✓
3. Povl signs off on quantitative requirements. ✓ — [quantitative.md](./strategies/quantitative.md) v0.3
4. Kricke or Jonte confirms one real Saturday proposal is enterable at ATG. *(UC-22)*
5. Core use-case specifications completed beyond DRAFT skeleton. ✓ — all UCs APPROVED v1.0 (2026-07-07)

---

## 5. Deprecated sections

The following former SRS sections now live only in RUP artifacts:

| Former section | New location |
|----------------|--------------|
| §1 Introduction | [VISION.md](./VISION.md) §1–2, §8 |
| §2 Stakeholders | [VISION.md](./VISION.md) §3, [ROSTER.md](./ROSTER.md) |
| §3 Functional requirements | [use-case-model.md](./requirements/use-case-model.md) |
| §4 Non-functional requirements | [supplementary-specification.md](./requirements/supplementary-specification.md) |
| §5 External interfaces | Supplementary §8 |
| §7 Open items | Supplementary §10; per-UC open items |

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-06 | RUP decomposition; SRS becomes index + traceability |
| 0.2 | 2026-07-06 | AIRUP workflow requirements (§3.0) |
| 0.1 | 2026-07-06 | Initial monolithic SRS |