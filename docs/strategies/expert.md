# Expert strategy (expert betslips)

| Field | Value |
|-------|-------|
| **Mode** | `expert` |
| **Owner** | Nisse (roster / tip fidelity), ornstein (operator UX), Povl (cost) |
| **Status** | APPROVED |
| **Version** | 0.3 |
| **Last updated** | 2026-07-15 |
| **Spec** | [expert-v1.md](../../outbox/specs/expert-v1.md) |
| **Use case** | [UC-12](../requirements/use-cases/UC-12-expert-mode.md) |
| **Research** | [2026-07-15-experts-travet.md](../../inbox/research/2026-07-15-experts-travet.md) |
| **Machine roster** | [experts.yaml](../../src/vai/strategies/experts.yaml) |

---

## 1. Purpose

Help the operator **use professional experts’ published V85 systems** (complete betslips). VAI does not invent the system; it **lists, loads, costs, and documents** a tip the operator chooses.

Systems appear in four shapes (research snapshot mid-2026):

1. Free text/video (full rad)
2. Podcast builds (live system)
3. Andelsspel (share of expert’s rad)
4. Paid tip services

---

## 2. Concept

1. Tips are **transcribed** into YAML under `inbox/expert-tips/` (AIRUP Inbox).
2. Operator opens **Expert** mode for a race day.
3. Operator **selects** a tip from the list.
4. Slip fills with that expert’s horses; cost follows ATG formula.
5. Operator may override legs, then review (UC-20) and enter at ATG (UC-22).

Use `expert_id` from the roster when writing tip YAML.

---

## 3. Free weekly outlets (start here)

| Outlet | What you get | Link |
|--------|----------------|------|
| **Travstugan** | Free analyses, skrällar, ready-made systems | https://travstugan.se/v85 |
| **Travcash** | Free ranking/systems + podd; Referenten builds live | https://travcash.se/v85-tips/ |
| **Trav.se** | “Stora” + “lilla” systems with motivation | https://trav.se/ |
| **Rekatochklart** | Free systems (Leboff m.fl.) | https://www.rekatochklart.com/trav/v85-tips/ |
| **Travmaskinen** | AI ranking + system by budget | https://travmaskinen.se/v85-tips |
| **Trava På!** | Hub of V85 tips, poddar, systems | https://www.travapa.se/ |
| **Gratistravtips.se** | Aggregates poddar/video | https://www.gratistravtips.se/ |

**Best single index of links:** https://www.travapa.se/

---

## 4. Expert roster (v0.3)

Canonical IDs for tip files (`expert_id`). Full metadata: `src/vai/strategies/experts.yaml`.

### 4.1 Priority for free full-system transcription

| expert_id | Display name | Product / outlet |
|-----------|--------------|------------------|
| `referenten` | Albin “Referenten” Engdahl | Travcash / Travcashpodden |
| `albin-kjellberg` | Albin Kjellberg | Travcash |
| `leboff` | Leboff | Rekatochklart |
| `travstugan` | Travstugan (team) | travstugan.se/v85 |
| `trav-se` | Trav.se | Stora / Lilla systemet |
| `travmaskinen` | Travmaskinen | travmaskinen.se |
| `systemet-podd` | Jonas Noreen & Eskil Hellberg | Expressen **Systemet** |
| `bjorn-goop` | Björn Goop | Björnkollen (ATG) — often analysis > full rad |
| `krillekrukan` | Christer “Krillekrukan” Eriksson | KorsDragaren (ATG) |
| `thomas-uhrberg` | Thomas Uhrberg | thomasuhrberg.se |
| `sportbladet-trav365` | Sportbladet Trav365 | Aftonbladet |

### 4.2 ATG / mainstream mix

| expert_id | Display name |
|-----------|--------------|
| `atg-mixen` | ATG V85 Mixen |
| `fem-tippar` | Fem Tippar V85 |
| `vass-eller-kass` | Vass eller Kass |

### 4.3 Andelsspel / paid (transcribe only if operator has access)

| expert_id | Display name | Outlet |
|-----------|--------------|--------|
| `stridbeck` | Stridbeck (Stora/Lilla) | Travstugan |
| `helena-holm`, `oliver-pihlstrom`, `johan-sunnanangs`, `grakka` | Travcash andelsteam | Travcash |
| `niclas-carlson`, `johan-sjostrom`, `david-norismaa`, `fredrik-berglund`, `jimmy-simonsson`, `anders-svensson`, `bosse-eklof`, `johan-ulvestal` | MinAndel spelläggare | minandel.se |
| `travtjansten` | Travtjänsten | Paid packages |

### 4.4 Synthetic

| expert_id | Notes |
|-----------|--------|
| `fixture` | Tests / UI demo only |

### Travstugan team (examples for `travstugan` tips)

Andreas Stenberg, Christian Sandholm, Jimmie Nordberg, Martin Engström, Emil Andersson, Jonas Harrysson, Kim Lagerhem, Erika Pajari, David Dabescovic, Tobias Romander, Mattias Karlsson, Felix Berggren, Jimmy Westberg, Jonatan Östlund — use specific names in `source_note` when known.

---

## 5. Andelsspel marketplaces

| Site | Focus |
|------|--------|
| https://travcash.se/andelsspel/ | Travcash experts |
| https://minandel.se/ | Many named spelläggare |
| https://travstugan.se/andelsspel | Stridbeck + Travstugan |
| https://kopandel.se/ | 50+ lag; multi-game |
| https://andelstorget.se/ | Expert directory |

VAI still needs a **full rad** (horse numbers per leg) to load a tip — andel share alone is not enough unless the full system is published.

---

## 6. Tip storage

```
inbox/expert-tips/
  README.md
  <YYYY-MM-DD>-<track-slug>/
    <tip_id>.yaml
```

Schema: [expert-v1.md](../../outbox/specs/expert-v1.md) §3.

When transcribing, set:

```yaml
expert_id: referenten   # from roster
expert_name: Albin "Referenten" Engdahl
product_name: Travcash
source_url: https://travcash.se/v85-tips/
```

---

## 7. Outputs

```yaml
mode: expert
tip_id: …
expert_id: …
expert_name: …
product_name: …
source_url: …
source_note: …
```

---

## 8. Attribution and use policy

- Tips are for **private operator decision support**.
- Always keep **source_url** / **source_note** when transcribed.
- Do not present tips as VAI-originated picks.
- No claim of guaranteed return or superior EV.
- Past wins / “vinstrikaste” marketing are **not** edge.

---

## 9. Open requirements

- [x] Expand roster from Travet experts research (2026-07-15)
- [x] `GET /api/v1/experts` + Expert UI roster (free filter, has_tip for date)
- [ ] Optional UI filter by outlet
- [ ] Optional future ATG tips fetch (ToS review)
- [ ] Andelssystem / reduced-row tips (if experts publish non-full matrix)

---

## Change log

| Version | Date | Change |
|---------|------|--------|
| 0.3 | 2026-07-15 | Roster from [experts-travet research](../../inbox/research/2026-07-15-experts-travet.md); free outlets + named spelläggare |
| 0.2 | 2026-07-15 | Redefined as expert betslip catalog (supersedes pattern templates) |
| 0.1 | 2026-07-06 | Initial draft (pattern templates — obsolete) |
