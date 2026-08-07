# VAI — Trace Log

| Field | Value |
|-------|-------|
| **Version** | 0.1 |
| **Owner** | ornstein |
| **Last updated** | 2026-08-07 |

Optional audit trail of significant project decisions and AIRUP **Update** events. ornstein requests entries; agents suggest but do not append without direction.

---

## Format

| Date | AIRUP phase | Actor | Summary | Artifact / link |
|------|-------------|-------|---------|-----------------|
| 2026-08-07 | P | Assistant | **Commit + push betslip SPARA/LADDA UPP** — `8705fd5` on `origin/master`; YAML save/load + Datum-Bana-Spelform naming; **prod deploy blocked** (sudo password). Run: `sudo bash /opt/vai/deploy/update-server.sh` | https://vai.ornstein.work/ ; [betslip.py](../../src/vai/io/betslip.py) |
| 2026-08-07 | U | Assistant | **Betslip SPARA / LADDA UPP** — YAML save/load beside print; file name `{datum}-{bana}-{spelform}[-n].yaml`; print title uses Datum+Bana+Spelform; API `POST /api/v1/betslips` + `/parse` | [betslip.py](../../src/vai/io/betslip.py), mockup `outbox/mockups/v85-proposal-ux-mockup-atg.html` |
| 2026-08-07 | P | ornstein | **End of session (O&O)** — activity stats IP lookup + app-served deploy live; session closed | See [§ End of session — 2026-08-07 (activity stats)](#end-of-session--2026-08-07-activity-stats) |
| 2026-08-07 | P | Assistant | **Activity stats part of app** — `4e9c572` on `origin/master`; app serves `/vai-stats.html` + `/activity.jsonl`; nginx aliases removed; update-server verifies Lookup IPs; **prod later live** at `dbe8ab9` | https://vai.ornstein.work/vai-stats.html |
| 2026-08-07 | P | Assistant | **Commit + push activity stats IP lookup** — `467a2f0` on `origin/master`; client_ip enrichment (hostname/country/city/org/type/risk) + CSV export; **prod deploy blocked** (sudo password). Run: `sudo bash /opt/vai/deploy/update-server.sh` (or `sudo cp ~/grok/vai/vai-stats.html /opt/vai/vai-stats.html`) | https://vai.ornstein.work/vai-stats.html |
| 2026-08-07 | P | ornstein | **End of session (O&O)** — andelsspel scrape research logged; no ATG tip scraper; session closed | See [§ End of session — 2026-08-07 (andelsspel scrape research)](#end-of-session--2026-08-07-andelsspel-scrape-research) |
| 2026-08-07 | I | Assistant | **Deep research: ATG andelsspel scrape** — `gameId=V85_2026-08-08_33_5` SPA shell only; no usable V85 systems; butik pages also SPA; ToS forbid scrape; Expert remains manual YAML | [2026-08-07-deep-research-andelsspel-scrape.md](../../inbox/research/2026-08-07-deep-research-andelsspel-scrape.md) |
| 2026-08-07 | P | ornstein | **End of session (O&O)** — Hari live betslip + Rensa alla clear shipped; session closed | See [§ End of session — 2026-08-07 (Hari live betslip)](#end-of-session--2026-08-07-hari-live-betslip) |
| 2026-08-07 | P | Assistant | **Commit + push Hari live betslip** — `4c5e4eb` on `origin/master`; horse select/deselect updates spelkvitto + cost under Hari; **Rensa alla** fully clears slip; **prod deploy blocked** (sudo password). Run: `sudo bash /opt/vai/deploy/update-server.sh` | https://vai.ornstein.work/ ; mockup `outbox/mockups/v85-proposal-ux-mockup-atg.html` |
| 2026-08-07 | U | Assistant | **Hari betslip live update** — RANDOM matches Expert: `onHorseGridChanged` → `refreshSlipFromGrid`; cost = ∏×0.50; clearSlip on Rensa alla / empty grid | `4c5e4eb` |
| 2026-07-31 | P | ornstein | **End of session (O&O)** — standalone activity stats page shipped; session closed | See [§ End of session — 2026-07-31 (activity stats)](#end-of-session--2026-07-31-activity-stats) |
| 2026-07-31 | P | Assistant | **Commit + push activity stats** — `a594e15` + docs `576a97f` on origin; standalone `vai-stats.html`; nginx locations in deploy/; **prod deploy blocked** (sudo password). Run: `sudo bash /opt/vai/deploy/update-server.sh` then `sudo bash /opt/vai/deploy/fix-nginx-https.sh` | https://vai.ornstein.work/vai-stats.html |
| 2026-07-31 | P | ornstein | **End of session (O&O)** — activity logging v1 shipped (F-110/F-111); AIRUP P complete; session closed | See [§ End of session — 2026-07-31 (activity logging)](#end-of-session--2026-07-31-activity-logging) |
| 2026-07-31 | P | Assistant | **Commit + push activity logging** — `7d36f44` on `origin/master`; **prod deploy blocked** (sudo password). Run: `sudo bash /opt/vai/deploy/update-server.sh` then `tail -f /opt/vai/logs/activity.jsonl` | https://github.com/jonasornstein/VAI ; [activity-logging-v1.md](../../outbox/specs/activity-logging-v1.md) |
| 2026-07-31 | P | Povl, ornstein | **activity-logging-v1 APPROVED** — published to outbox/specs; review recorded; pending stub → canonical; F-110/F-111 in functions.md | [activity-logging-v1.md](../../outbox/specs/activity-logging-v1.md), [REVIEW_activity-logging-v1.md](../../outbox/reviews/REVIEW_activity-logging-v1.md) |
| 2026-07-29 | P | ornstein | **expert-roster-manage-v1 APPROVED** — published to outbox/specs; review recorded; pending stub → canonical | [expert-roster-manage-v1.md](../../outbox/specs/expert-roster-manage-v1.md), [REVIEW_expert-roster-manage-v1.md](../../outbox/reviews/REVIEW_expert-roster-manage-v1.md) |
| 2026-07-29 | P | ornstein | **End of session (O&O)** — expert panel UX (counts, select-all, reorder, dark theme) shipped; session closed | See [§ End of session — 2026-07-29 (expert panel UX)](#end-of-session--2026-07-29-expert-panel-ux) |
| 2026-07-29 | P | Assistant | **Commit + push expert panel UX** — `879e1e6` + dark-theme `dd09fc3` on `origin/master`; prod deploy blocked (sudo password) | https://github.com/jonasornstein/VAI ; run `sudo bash /opt/vai/deploy/update-server.sh` |
| 2026-07-29 | U | Assistant | **Dark theme visibility controls** — Markera/Avmarkera alla + ↑/↓ use theme tokens (mörk mode) | `dd09fc3`; mockup Expert **VISA EXPERTER** |
| 2026-07-29 | U | Assistant | **Expert panel UX** — count `N synliga av M`; VISA EXPERTER Markera/Avmarkera alla; ↑/↓ reorder; API visibility + reorder + list counts | `879e1e6`; [expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md) v0.4 |
| 2026-07-29 | P | Assistant | **End of session** — Q&A **Redo** badge; close-out `cdca2c4` on origin; prod deploy still blocked (sudo) | See [§ End of session — 2026-07-29](#end-of-session--2026-07-29) |
| 2026-07-29 | I | Assistant | **Q: What is "REDO" in EXPERT panels?** — badge = tip exists for selected date (`has_tip`); Swedish “ready”, not undo/redo | mockup Expert panel; [inbox/expert-tips/README.md](../../inbox/expert-tips/README.md) |
| 2026-07-29 | P | Assistant | **Commit + push VISA EXPERTER** — `76a3906` on `origin/master`; prod deploy blocked (sudo password) | https://github.com/jonasornstein/VAI ; run `sudo bash /opt/vai/deploy/update-server.sh` |
| 2026-07-29 | U | Assistant | **VISA EXPERTER popup** — main Expert panel shows only `visible` experts; Återställ roster → **VISA EXPERTER** visibility panel with tick-boxes | `76a3906`; [expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md) v0.3 |
| 2026-07-29 | P | Assistant | **Commit + push soft-hide** — `df9fc83` on `origin/master`; prod deploy blocked (sudo password) | https://github.com/jonasornstein/VAI ; run `sudo bash /opt/vai/deploy/update-server.sh` |
| 2026-07-29 | U | Assistant | **Expert roster soft-hide** — never hard-delete rows; `visible` bool (default true); DELETE/Visa tick-box hides; full list retains hidden for re-show; Återställ still overwrites | `df9fc83`; [expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md) |
| 2026-07-28 | P | ornstein | **End of session (O&O)** — expert roster add/delete/reset shipped; session closed | See [§ End of session — 2026-07-28](#end-of-session--2026-07-28) |
| 2026-07-28 | U | Assistant | **Expert roster manage** — add / delete / full reset to defaults; working copy `inbox/experts/roster.yaml`; API + Expert tab UI; tips not cascade-deleted (F-044–048) | `585af6d`; [expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md), [inbox/experts/](../../inbox/experts/) |
| 2026-07-27 | P | ornstein | **End of session (O&O)** — V85 experts deep research logged & compared to roster; session closed | See [§ End of session — 2026-07-27 (experts research)](#end-of-session--2026-07-27-experts-research) |
| 2026-07-27 | I | Assistant | **Deep research: V85 experts / full systems** — free outlets re-validated vs VAI roster; Eddie Östlund candidate; comparison scorecard | [2026-07-27-deep-research-v85-experts.md](../../inbox/research/2026-07-27-deep-research-v85-experts.md) |
| 2026-07-27 | P | ornstein | **End of session (O&O)** — screen-scrape deep research logged; session closed | See [§ End of session — 2026-07-27](#end-of-session--2026-07-27) |
| 2026-07-27 | I | Assistant | **Deep research: screen-scrape expert tip** — no scraper in v1; manual YAML only; ATG ToS + outlet constraints | [2026-07-27-deep-research-screen-scrape.md](../../inbox/research/2026-07-27-deep-research-screen-scrape.md) |
| 2026-07-27 | P | ornstein | **End of session (O&O)** — Experttips form shipped; session closed | See [§ End of session — 2026-07-27](#end-of-session--2026-07-27) |
| 2026-07-27 | U | Assistant | **Experttips form** — enter/edit/delete tip YAML from Expert roster (form icon left of Gratis/Andel/betald); PUT/lookup/DELETE API; list refresh after save/delete | `79b640d`, `b4ceaf9`, `70e64ba`; [inbox/expert-tips/](../../inbox/expert-tips/) |
| 2026-07-25 | P | ornstein | **End of session** — Mac SSH + tunnel OK; session closed | See [§ End of session — 2026-07-25](#end-of-session--2026-07-25) |
| 2026-07-25 | U | ornstein | **Mac verified** — SSH + port tunnel from Mac Terminal works well; browser to dev UI OK (same flow as PC) | [deploy-hetzner.md](./deploy-hetzner.md#browse-dev-ui-from-your-pc-ssh-tunnel) |
| 2026-07-25 | I | ornstein | **Expert tips Bollnäs 2026-07-25** — five real betslips transcribed to inbox (Goop, Travstugan, Referenten, Leboff, Uhrberg) | See [§ Expert tips — Bollnäs 2026-07-25](#expert-tips--bollnäs-2026-07-25) |
| 2026-07-24 | P | ornstein | **End of session** — Expert v1.3.0 live on production; TRACE-LOG closed | See [§ End of session — 2026-07-24](#end-of-session--2026-07-24) |
| 2026-07-24 | P | ornstein | **Production deploy v1.3.0** — Expert mode on https://vai.ornstein.work/ (`update-server.sh` as root) | `fa09597`, See [§ Release v1.3.0](#release-v130--2026-07-24) |
| 2026-07-24 | P | Assistant | **Release commit + push** — `fa09597` Expert betslip catalog (UC-12) on `origin/master` | https://github.com/jonasornstein/VAI |
| 2026-07-15 | I | ornstein | **Experts Travet research** — directory of free V85 systems, named spelläggare, andelsspel markets | [2026-07-15-experts-travet.md](../../inbox/research/2026-07-15-experts-travet.md) |
| 2026-07-15 | U | Assistant | **Expert roster expanded** from Travet research → `experts.yaml` + expert.md v0.3 | [experts.yaml](../../src/vai/strategies/experts.yaml), [expert.md](./strategies/expert.md) |
| 2026-07-15 | P | Assistant | **UC-12 Expert betslips v1.3** — list/select professional tips (YAML inbox); API + CLI + Expert tab; F-040–043 remapped; fixture tip Axevalla | [expert-v1.md](../../outbox/specs/expert-v1.md), [expert.md](./strategies/expert.md) |
| 2026-07-15 | P | ornstein | **V85 Axevalla 2026-07-18 proposal APPROVED** — Hari seed 42, 500 SEK, 1 000 rader; race-day UC-22 Saturday | [proposal.md](../../outbox/proposals/v85/2026-07-18-axevalla/proposal.md) |
| 2026-07-15 | U | ornstein | **Exit PC to test Mac** — leaving Windows PC session; next verify SSH + tunnel (`-L 8766:…`) and browser from Mac Terminal | [deploy-hetzner.md](./deploy-hetzner.md#browse-dev-ui-from-your-pc-ssh-tunnel) |
| 2026-07-15 | U | ornstein | **SSH tunnel from PC** — usual case: `ssh -L 8766:127.0.0.1:8766 ornstein@168.119.155.11` then open http://127.0.0.1:8766/ in PC browser (dev serve binds localhost only) | [deploy-hetzner.md](./deploy-hetzner.md#browse-dev-ui-from-your-pc-ssh-tunnel) |
| 2026-07-15 | P | ornstein | **Release v1.1.4** — horse buttons pool%+odds; slip odds; dark-theme meta colors; production deploy | Tag `v1.1.4`, See [§ Release v1.1.4](#release-v114--2026-07-15) |
| 2026-07-15 | U | ornstein | **Horse odds UX** — option A buttons (V85 pool% + vinnare odds); slip chips with odds; API `leg_odds` from ATG | `outbox/mockups/…`, `atg_race_card.extract_leg_odds`, server race-card payload |
| 2026-07-15 | P | ornstein | **Release v1.1.3** — bet slip: operator numbers bold, system numbers italic, five-space gaps | Tag `v1.1.3`, See [§ Release v1.1.3](#release-v113--2026-07-15) |
| 2026-07-15 | U | ornstein | **Bet slip UX** — operator horse numbers **bold**, system/random numbers *italic*; five-space gap between numbers (nbsp + inner span so flex keeps gaps) | `outbox/mockups/v85-proposal-ux-mockup-atg.html` |
| 2026-07-15 | U | ornstein | **Ready on new dev machine** — Hetzner Ubuntu as `ornstein`; Grok CLI; clone `~/grok/vai`; GitHub SSH push works (`fd20da0`); ship path documented | See [§ Workstation migration plan — 2026-07-15](#workstation-migration-plan--2026-07-15) |
| 2026-07-15 | U | ornstein | **Workstation Phase 3** — `deploy-hetzner.md` local-vs-prod refresh (dev `~/grok/vai` / prod `/opt/vai`); related notes in `deploy/README.md` | [deploy-hetzner.md](./deploy-hetzner.md), See [§ Workstation migration plan — 2026-07-15](#workstation-migration-plan--2026-07-15) |
| 2026-07-15 | U | ornstein | **Workstation Phase 2 complete** — `which grok` → `~/.grok/bin/grok`; 0.2.101; clone + 38 tests; PATH fixed | See [§ Workstation migration plan — 2026-07-15](#workstation-migration-plan--2026-07-15) |
| 2026-07-15 | U | ornstein | **Workstation Phase 2** — dev clone `/home/ornstein/grok/vai` @ `0223f67`; venv; 38 tests pass; Grok CLI 0.2.101 installed | See [§ Workstation migration plan — 2026-07-15](#workstation-migration-plan--2026-07-15) |
| 2026-07-15 | U | ornstein | **Workstation migration RESUMED** — Phase 0 pushed (`0223f67`); Phase 1 user `ornstein` + SSH; Phase 2 clone | See [§ Workstation migration plan — 2026-07-15](#workstation-migration-plan--2026-07-15) |
| 2026-07-15 | U | ornstein | **GitHub check status** — historical Vercel red checks left on old SHAs (cannot scrub in UI); ignore; new `master` HEAD clean after push; no history rewrite | See [§ GitHub cleanup — 2026-07-15](#github-cleanup--2026-07-15) |
| 2026-07-15 | U | ornstein | **GitHub cleanup** — default branch `master`; remote `main` deleted; Vercel GitHub integration disconnected and VAI project deleted at Vercel; Hetzner-only | See [§ GitHub cleanup — 2026-07-15](#github-cleanup--2026-07-15) |
| 2026-07-15 | U | ornstein | **Workstation plan (logged)** — Windows → Hetzner Ubuntu SSH; user `ornstein` (sudo); dev `~/grok/vai`; prod stays `/opt/vai` (not `/var/www/html`); Grok CLI + GitHub only; no daily root | See [§ Workstation migration plan — 2026-07-15](#workstation-migration-plan--2026-07-15) |
| 2026-07-14 | P | ornstein | **End of session (O&O)** — production live at https://vai.ornstein.work/; Hetzner deploy; Vercel removed | See [§ End of day — 2026-07-14](#end-of-day--2026-07-14) |
| 2026-07-14 | P | ornstein | **Hetzner production** — `dev-server` 168.119.155.11; nginx + Let's Encrypt; systemd `vai.service` | [deploy-hetzner.md](./deploy-hetzner.md), [`deploy/`](../deploy/) |
| 2026-07-14 | P | ornstein | **GitHub VAI public** — repo renamed `jonasornstein/VAI`; `master` canonical; `main` synced | https://github.com/jonasornstein/VAI |
| 2026-07-14 | U | ornstein | **Vercel deploy removed** — deleted `vercel.json`, `api/`, `requirements.txt`, `[tool.vercel]`; Hetzner-only hosting | `9102c4e` |
| 2026-07-14 | U | ornstein | **Project rename ATG → VAI** — package `src/vai/`, `VaiRequestHandler`, UI branding; operator integration (`atg_fetch`, `ATG_UNAVAILABLE`) unchanged | `pyproject.toml`, `AGENTS.md`, mockup |
| 2026-07-11 | U | ornstein | **Operator rename** — persona Jonte → ornstein across docs, specs, proposals, rules, skills; `docs/ornsteinDocs/` | ROSTER M-004 |
| 2026-07-11 | P | ornstein | **Release v1.1.2** — strukna hästar synliga (röda, ej valbara); spik-namn i betslip; `horse_names` i race card API | Tag `v1.1.2` |
| 2026-07-08 | R | ornstein | **Träffsannolikhet** — F-052 basic formula reference (pool-share proxy, independent-leg DP) | See [§ Träffsannolikhet](#träffsannolikhet-f-052-basic) |
| 2026-07-08 | P | ornstein | **End of session** — UC-15 race info in leg headers; operator verified in local UI | See [§ End of day — 2026-07-08](#end-of-day--2026-07-08) |
| 2026-07-08 | P | Nisse, ornstein | **UC-15 race info shipped** — F-029 leg headers; ATG metadata; scratches fix | [UC-15-race-info.md](./requirements/use-cases/UC-15-race-info.md), [race-info-v1.md](../../outbox/specs/race-info-v1.md) |
| 2026-07-07 | P | ornstein | **End of session** — v1.1 Hari shipped; RUP trilogy APPROVED; Phase 2b complete; race day Årjäng 2026-07-11 next | See [§ End of day — 2026-07-07](#end-of-day--2026-07-07) |
| 2026-07-07 | P | ornstein, Povl, Nisse | **supplementary-specification APPROVED** — FURPS+ v1.0; v1.1 NFR alignments | [supplementary-specification.md](./requirements/supplementary-specification.md), [REVIEW_supplementary-specification.md](../../outbox/reviews/REVIEW_supplementary-specification.md) |
| 2026-07-07 | P | Povl, ornstein | **functions.md APPROVED** — v1.0 F-* catalog; shipped vs deferred; module map | [functions.md](./requirements/functions.md), [REVIEW_functions.md](../../outbox/reviews/REVIEW_functions.md) |
| 2026-07-07 | P | ornstein, Povl, Nisse | **All use cases APPROVED** — 13 UCs v1.0; Phase 2b complete; UC-12/13 spec-only | [use-cases/](./requirements/use-cases/), [REVIEW_use-cases_v1.0.md](../../outbox/reviews/REVIEW_use-cases_v1.0.md) |
| 2026-07-07 | U | Assistant | **functions.md refreshed** — v0.4 shipped vs deferred; v1.1 ATG fetch, F-052 basic, module map | [functions.md](./requirements/functions.md) |
| 2026-07-07 | P | Povl, Nisse | **race-card-schema APPROVED** — v1.0; ATG primary ingestion, validation rules, source enum | [race-card-schema.md](./requirements/race-card-schema.md), [REVIEW_race-card-schema.md](../../outbox/reviews/REVIEW_race-card-schema.md) |
| 2026-07-07 | P | ornstein | **ux-workflow APPROVED** — operator UX workflow v1.0; Hari v1.1 flow, ATG fetch, nearest stake | [ux-workflow.md](./requirements/ux-workflow.md), [REVIEW_ux-workflow.md](../../outbox/reviews/REVIEW_ux-workflow.md) |
| 2026-07-07 | P | Povl, ornstein | **UC-11 APPROVED** — Random mode (Hari) use case v1.0; exact-budget fill, frozen legs, nearest stake | [UC-11-random-mode.md](./requirements/use-cases/UC-11-random-mode.md), [REVIEW_UC-11_random-mode.md](../../outbox/reviews/REVIEW_UC-11_random-mode.md) |
| 2026-07-07 | U | ornstein | **V75 removed** — game discontinued at ATG; spelform dropdown V85-only in mockup | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | P | Povl | **Random v1.1 + ATG data source APPROVED** — exact-budget Hari, nearest stake, F-052 basic | [random-v1.1.md](../../outbox/specs/random-v1.1.md), [atg-data-source.md](../../outbox/specs/atg-data-source.md) |
| 2026-07-07 | P | ornstein | **V85 Årjäng 2026-07-11 proposal APPROVED** — Hari seed 42, 500 SEK, 1 000 rader | [proposal.md](../../outbox/proposals/v85/2026-07-11-arjang/proposal.md) |
| 2026-07-07 | P | ornstein | **V75 spelform v1.1** — selector enabled for title/ATG link; V85 schedule API unchanged until `docs/betting/v75.md` | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | R | Assistant | **Random v1.1 spec + ATG data source** — exact-budget Hari, nearest stake, F-052 basic; docs and UX workflow updated | [random-v1.1.md](../../pending/specs/random-v1.1.md), [atg-data-source.md](../../pending/specs/atg-data-source.md) |
| 2026-07-07 | R | Assistant | **Race-day draft** — Årjäng 2026-07-11 inbox card + pending proposal (seed 42, 500 SEK) | [pending/proposals/v85/2026-07-11-arjang/](../../pending/proposals/v85/2026-07-11-arjang/) |
| 2026-07-07 | U | ornstein | **Hästar labels** — legend `Slumpens hästar`; stat `Antal hästar tillagda`; rationale uses `hästar till budget` (seed help unchanged) | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | U | ornstein | **Rationale text** — default `Slumpmässigt urval ur operatörens kandidatpool per avdelning.`; after generate appends `Markerade hästar låses. Slumpen fyller på med x hästar till budget.` | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | U | ornstein | **Hari mode + action buttons** — Random tab renamed `Hari`; `GENERERA SYSTEM` and `ÖPPNA ATG/V85` matched size via `.btn-action` | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | U | ornstein | **Innan spel checklist wired** — `F-071` items update from generated system + race card (legs, cost, scratches, reserves) | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | U | ornstein | **Dynamic title verified** — headline, page title, and logo tooltip update to `VAI` + spelform on change (e.g. V85 → V75) | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | U | ornstein | **VAI branding** — logo badge `VAI`; headline `VAI` + spelform; PDF export button removed; print-only slip export | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | P | ornstein | **Genererat spel betslip APPROVED** — layout matches `inbox/betslip.png`; 8-leg V85, footer `x` format, no title bar | [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html) |
| 2026-07-07 | P | ornstein | **v1 close-out** — specs + canonical docs; random.md v0.2 APPROVED | [outbox/specs/](../../outbox/specs/) |
| 2026-07-07 | P | Assistant | **v1.1 local UI** — `atg serve` API + mockup wiring | [local-ui-v1.1.md](../../outbox/specs/local-ui-v1.1.md) |
| 2026-07-07 | P | ornstein | **UX mockup v0.5** published — Random default; Expert/Kvant disabled | [outbox/mockups/](../../outbox/mockups/) |
| 2026-07-07 | P | ornstein | **First random v1 proposal APPROVED** — Halmstad 2026-07-05 → `outbox/proposals/` | [proposal.md](../../outbox/proposals/v85/2026-07-05-halmstad/proposal.md) |
| 2026-07-07 | R | Assistant | **Operator review** sample proposal Halmstad 2026-07-05 — READY FOR OPERATOR | [REVIEW_proposal_2026-07-05-halmstad.md](../../pending/reviews/REVIEW_proposal_2026-07-05-halmstad.md) |
| 2026-07-07 | R | Assistant | **UX mockup v0.5:** Random default; Expert/Kvant disabled (*Kommer senare*) | [pending/mockups/](../../pending/mockups/) |
| 2026-07-07 | R | Assistant | **Random v1 implementation:** `src/atg/` vertical slice + CLI + 13 tests; sample proposal | [src/](../../src/) |
| 2026-07-07 | R | ornstein + Assistant | **Random v1 spec:** dynamic max_horses_per_leg = pool size; greedy shrink; uniform draw | [random-v1.md](../../pending/specs/random-v1.md) |
| 2026-07-07 | R | ornstein + Assistant | **v1 scope lock:** Random-only implementation; manual YAML race cards; Expert/Quant UX-only (deferred) | [scope-lock-v1-random.md](../../pending/specs/scope-lock-v1-random.md) |
| 2026-07-06 | P | Assistant | RUP requirements package (UC-01–UC-31, F-001–F-103, UX workflow) → `docs/requirements/` | [requirements/](./requirements/) |
| 2026-07-06 | P | Assistant | UX mockup v0.4 (ATG fetch UX, horse pools, SYSTEMKOSTNAD, logo) → `outbox/mockups/` | [outbox/mockups/](../../outbox/mockups/) |
| 2026-07-06 | R | Assistant | UC-09 ATG auto-fetch; UX workflow; SYSTEMKOSTNAD default 500 SEK | [ux-workflow.md](./requirements/ux-workflow.md) |
| 2026-07-06 | R | Assistant | Use cases UC-01–UC-31 narratives + functions F-001–F-103 + race card schema | [requirements/](./requirements/) |
| 2026-07-06 | P | Assistant | SRS decomposed to IBM RUP trilogy; AIRUP v1.1 requirements workflow | [requirements/](./requirements/) |
| 2026-07-06 | P | Assistant | V85 proposal UX mockups v0.1–v0.3 (ATG branding, dark mode) → `outbox/mockups/` | [outbox/mockups/](../../outbox/mockups/) |
| 2026-07-06 | I | Assistant | S-009 blocked; replaced with S-009a EN PDF + access note | [S-009-access-note.md](../../inbox/research/S-009-access-note.md) |
| 2026-07-06 | P | Assistant | Quantitative strategy APPROVED v0.3 (Phase 2) | [REVIEW_quantitative.md](../../outbox/reviews/REVIEW_quantitative.md) |
| 2026-07-06 | P | Assistant | V85 rules APPROVED → `outbox/` + `docs/betting/v85.md` v1.0 | [REVIEW_v85_rules.md](../../outbox/reviews/REVIEW_v85_rules.md) |
| 2026-07-06 | R | Assistant | Phase 1 V85 rules research draft → `pending/research/` | [PENDING-RESEARCH_v85_rules.md](../../pending/research/PENDING-RESEARCH_v85_rules.md) |
| 2026-07-06 | I | Assistant | V85 source bibliography ingested | [inbox/research/v85-sources.md](../../inbox/research/v85-sources.md) |
| 2026-07-06 | P | ornstein | AIRUP methodology adopted; scaffold restructured | [AIRUP.md](./AIRUP.md) |
| 2026-07-06 | P | Assistant | Initial project scaffold (pre-AIRUP) | AGENTS.md, docs/, skills |

---

## When to log

- Methodology or requirements changes
- Nisse / Povl / operator approvals
- Promotion of `pending/` → `outbox/` or `docs/`
- Rejected proposals or superseded rules

## When not to log

- Routine agent edits, typo fixes, or exploratory drafts still in `pending/`

---

## Träffsannolikhet (F-052 basic)

**UI:** `#hit-summary-help-btn` in [v85-proposal-ux-mockup-atg.html](../../outbox/mockups/v85-proposal-ux-mockup-atg.html)  
**Code:** [hit_summary.py](../../src/atg/hit_summary.py) · **Spec:** [random-v1.1.md §6](../../outbox/specs/random-v1.1.md)

### Data

- ATG `starts[].pools.V85.betDistribution` ÷ 10 000 → fraction per horse per leg

### Per leg i = 1..8

\(p_i = \min(1,\ \sum_{h \in \text{selection}_i} \text{distribution}_{i,h}\)\)

Interpretation: sum of V85 pool shares on your picks ≈ P(win leg i). **Proxy only** — not true win odds.

### Across legs (independence assumption)

Dynamic programming over k = 0..8:

- P(exactly k correct) after each leg: wrong leg adds mass at k; right leg at k+1
- Outputs: P(8), P(≥7), P(≥6), P(≥5) → sidebar bars after **Generera system**

### Limitations

- Legs treated as independent (simplified)
- Not utdelning, EV, or guaranteed return
- Full quantitative model deferred to UC-13
- Hidden when `leg_distributions` missing (manual YAML / no ATG bet %)

---

## GitHub cleanup — 2026-07-15

**AIRUP:** Update  
**Actor:** ornstein (+ assistant for remote `main` delete)

### Done

| Item | Result |
|------|--------|
| Default branch | Set to **`master`** on GitHub |
| Remote branch `main` | **Deleted** (`git push origin --delete main`); local `main` removed |
| Remote branches remaining | **`master` only** |
| Vercel GitHub integration | **Disconnected** |
| Vercel project | **VAI project deleted** at Vercel |
| Production host | Unchanged — Hetzner https://vai.ornstein.work/ via `/opt/vai` |

### Notes

- Failed Vercel status on older commits may remain in history; new pushes should not create Vercel checks.
- Deploy path unchanged: `origin/master` → `deploy/update-server.sh`.
- Repo artifact removal for Vercel was earlier (`9102c4e`); this entry is integration + branch hygiene.

### Check status (commit checks UI)

| Decision | Detail |
|----------|--------|
| **Historical Vercel “Deployment has failed”** | Stored on old commit SHAs; **no bulk delete** in GitHub UI after disconnect |
| **Policy** | **Ignore** red checks on past commits — archaeological only; do not force-push history to scrub |
| **Going forward** | New commits on `master` must not get Vercel checks (integration + project already removed) |
| **Practical clean tip** | Next normal push to `master` makes **HEAD** the day-to-day view; empty checks on tip is fine |
| **Also verify manually** | Apps / webhooks / branch-protection required checks / Deployments list — remove Vercel leftovers if any |
| **Not done** | History rewrite, re-adding Vercel to “pass” checks |

---

## Workstation migration plan — 2026-07-15

**Status:** **COMPLETE — ornstein ready to work on new dev machine** (Phase 0–3 + GitHub SSH).  
**AIRUP:** Update (ops / workstation; production path unchanged).

### Decisions locked

| Topic | Choice |
|-------|--------|
| Daily SSH user | **`ornstein`** (group `sudo`); not root |
| Service user | **`vai`** (unchanged; owns `/opt/vai`) |
| Development path | `/home/ornstein/grok/vai` |
| Production path | **`/opt/vai`** — do **not** use `/var/www/html/vai` |
| Deploy bridge | GitHub `master` → `sudo bash /opt/vai/deploy/update-server.sh` |
| Tools on new workstation | Grok Build CLI + Git + SSH only (no Cursor/Vercel/Obsidian) |
| Same VM for dev+prod | Yes, with path and user separation |

### Why not `/var/www/html`

VAI is `python -m vai serve` behind nginx proxy, not static files. Existing install/systemd paths assume `/opt/vai`.

### Why not daily root

Blast radius, ownership fights under `/opt/vai`, Grok CLI running as unrestricted root, SSH attack surface.

### Progress

| Phase | Item | Status |
|-------|------|--------|
| 0 | Git gate — TRACE-LOG + `.gitignore` (`mcps/`) on GitHub | **Done** — `0223f67` |
| 0 | `docs/Rename-ATG-to-VAI.md` | Left untracked on Windows (optional) |
| 1 | Linux user `ornstein` + sudo | **Done** (`ornstein` in group `sudo`) |
| 1 | SSH as ornstein from Windows | **Done** (key login works) |
| 2 | Clone `/home/ornstein/grok/vai` | **Done** — `master` @ `0223f67` |
| 2 | Python venv + `pip install -e '.[dev]'` | **Done** (Python 3.12.3) |
| 2 | `pytest -q` | **Done** — **38 passed** |
| 2 | Grok Build CLI install | **Done** — 0.2.101 at `~/.grok/bin/grok` |
| 2 | PATH / `which grok` | **Done** — operator verified `/home/ornstein/.grok/bin/grok` |
| 2 | Grok CLI session auth | Operator confirmed CLI runs; complete login in TUI if prompted |
| 3 | `deploy-hetzner.md` local-vs-prod refresh | **Done** — v1.1; also `deploy/README.md` primary vs fallback |
| 4 | GitHub SSH as `ornstein` + push | **Done** — `ssh -T git@github.com` OK; remote `git@…/VAI.git`; `2819d2e..fd20da0` on `master` |
| — | **ornstein ready on new dev machine** | **Yes** — daily work on Hetzner Ubuntu (`dev-server`) |

### Day-to-day (locked)

1. Develop in `~/grok/vai` as `ornstein` with `grok`.  
2. Ship: `git push origin master` then `sudo bash /opt/vai/deploy/update-server.sh` when prod should match.  
3. Production URL: https://vai.ornstein.work/ (unchanged; `/opt/vai` as user `vai`).

---

## End of session — 2026-08-07 (activity stats)

**Session owner:** ornstein  
**Status:** **Closed (O&O)**  
**Dev:** `/home/ornstein/grok/vai` @ `4e9c572` / `dbe8ab9` (+ this TRACE-LOG close-out)  
**Production:** https://vai.ornstein.work/vai-stats.html — **live** (prod git `dbe8ab9`; app serves stats + activity JSONL)

### Completed this session

| Item | Status | Artifact |
|------|--------|----------|
| IP lookup columns (client_ip only) | Done | Hostname, country, city, org, type, risk via ipapi.is + DoH PTR |
| CSV export shown / all | Done | `vai-stats.html` |
| Stats page part of app | Done | `server.py` GET `/vai-stats.html`, `/activity.jsonl` |
| Nginx no static alias (no stale file) | Done | `deploy/nginx-*.conf`, `fix-nginx-https.sh` |
| Deploy verify Lookup IPs | Done | `deploy/update-server.sh` |
| Tests | Done | `test_server` stats + JSONL; classify `serve_stats` |
| Commit + push | Done | `467a2f0`, `4e9c572`, `dbe8ab9` → origin |
| Prod deploy | **Live** | Operator sudo after agent blocked; app 200 + Lookup IPs |

### Operator notes

- URL: **https://vai.ornstein.work/vai-stats.html** (also `/activity.jsonl`)
- Enrichment: **client_ip only** (not peer_ip); private IPs → local; cache in browser localStorage
- Future deploys: `sudo bash /opt/vai/deploy/update-server.sh` — fails if Lookup IPs viewer missing

### Carry-over

- None for activity stats.
- Next race-day: V85 Hari/Expert entry (UC-22) as usual.

---

## End of session — 2026-08-07 (andelsspel scrape research)

**Session owner:** ornstein  
**Status:** **Closed (O&O)**  
**Dev:** `/home/ornstein/grok/vai` (+ this TRACE-LOG close-out)  
**Production:** unchanged — research/docs only

### Completed this session

| Item | Status | Artifact |
|------|--------|----------|
| Deep research: scrape V85 from andelsspel gameId URL | Done | No usable systems via unauthenticated fetch |
| Inbox research note | Done | [2026-08-07-deep-research-andelsspel-scrape.md](../../inbox/research/2026-08-07-deep-research-andelsspel-scrape.md) |
| Policy reaffirmed | Done | Expert v1 = manual YAML only; no ATG tip scraper |
| Aligns with prior research | Confirmed | [2026-07-27-deep-research-screen-scrape.md](../../inbox/research/2026-07-27-deep-research-screen-scrape.md) |

### Decision

**Do not screen-scrape** `https://www.atg.se/andelsspel?gameId=…` (or butik SPA detail pages) for Expert tips.

| Why | Detail |
|-----|--------|
| Technical | SPA shell; listings lack Avd/Hästar grids; full rads only on butik/spel (also non-JS shell) |
| API | racinginfo games JSON = race card only, not andel systems |
| Legal | ATG Allmänna Villkor fr.o.m. 2026-01-01 forbid automated scraping |
| Product | UC-12 / expert-v1 non-goal; manual `inbox/expert-tips/` remains the path |

### Operator notes

- Target checked: `V85_2026-08-08_33_5` andelsspel listing.
- Free or visible systems: open in browser → transcribe to YAML (as today).
- Carry-over from earlier close-out still open: `sudo bash /opt/vai/deploy/update-server.sh` (Hari live betslip).

### Carry-over

- No code change required.
- Optional later: ToS-gated marketplace research only if product scope expands (out of v1).

---

## End of session — 2026-08-07 (Hari live betslip)

**Session owner:** ornstein  
**Status:** **Closed (O&O)**  
**Dev:** `/home/ornstein/grok/vai` @ `4c5e4eb` / `b6e7cae` (+ this TRACE-LOG close-out)  
**Production:** https://vai.ornstein.work/ — **deploy blocked** (agent shell has no sudo password)

### Completed this session

| Item | Status | Artifact |
|------|--------|----------|
| Hari live slip on horse toggle | Done | Select/deselect rebuilds spelkvitto + cost (∏×0.50 SEK) |
| Rensa alla avdelningar clears slip | Done | `clearSlip()` — empty grid, null cost/stats |
| Expert parity preserved | Done | Tip load + edit still auto-updates slip |
| Commit + push `master` | Done | `4c5e4eb`, `b6e7cae` → origin |
| Prod deploy | **Blocked** (sudo password) | Operator: see below |

### Operator notes

- UI file: `outbox/mockups/v85-proposal-ux-mockup-atg.html` (served at `/` by `vai serve`)
- After generate (or manual marks): click horses → slip and cost update immediately; **justerad** when grid differs from last generate
- **Rensa alla avdelningar** fully empties the slip (not 8 empty `—` rows)
- Unrelated local WIP left uncommitted: `vai-stats.html`

### Carry-over

```bash
sudo bash /opt/vai/deploy/update-server.sh
curl -sI https://vai.ornstein.work/ | head -5
```

- Deploy when convenient so prod matches Hari live-slip behavior.
- Next race-day: V85 Hari/Expert entry (UC-22).

---

## End of session — 2026-07-31 (activity stats)

**Session owner:** ornstein  
**Status:** **Closed (O&O)**  
**Dev:** `/home/ornstein/grok/vai` @ `a594e15` / `7fa9e08` (+ this TRACE-LOG close-out)  
**Production:** https://vai.ornstein.work/ — **deploy blocked** (agent shell has no sudo password)

### Completed this session

| Item | Status | Artifact |
|------|--------|----------|
| Standalone activity viewer | Done | `vai-stats.html` (sort, filter, summary cards; not wired into Python app) |
| Nginx static locations | Done | `/vai-stats.html`, `/activity.jsonl` in `deploy/nginx-*.conf`, `fix-nginx-https.sh` |
| Deploy docs | Done | [deploy/README.md](../../deploy/README.md) |
| Commit + push `master` | Done | `a594e15`, `576a97f`, `7fa9e08` → origin |
| Prod deploy | **Blocked** (sudo password) | Operator: see below |

### Operator notes

- Page is **static only** — load via nginx or **Load JSONL** in the browser; no VAI API dependency.
- Target URL after deploy: **https://vai.ornstein.work/vai-stats.html**
- Raw log alias: **https://vai.ornstein.work/activity.jsonl** → `/opt/vai/logs/activity.jsonl`
- Schema: [activity-logging-v1.md](../../outbox/specs/activity-logging-v1.md)

### Carry-over

```bash
sudo bash /opt/vai/deploy/update-server.sh
sudo bash /opt/vai/deploy/fix-nginx-https.sh
curl -sI https://vai.ornstein.work/vai-stats.html | head -5
```

- Next race-day: V85 Hari/Expert entry (UC-22).

---

## End of session — 2026-07-31 (activity logging)

**Session owner:** ornstein  
**Status:** **Closed (O&O)**  
**Dev:** `/home/ornstein/grok/vai` @ `7d36f44` / `705a477` (+ this TRACE-LOG close-out)  
**Production:** https://vai.ornstein.work/ — operator may already have updated `/opt/vai`; agent shell cannot sudo

### Completed this session

| Item | Status | Artifact |
|------|--------|----------|
| Deep research → inbox | Done | [2026-07-31-activity-logging-deep-research.md](../../inbox/research/2026-07-31-activity-logging-deep-research.md) |
| Spec I→R→P (Povl + ornstein) | **APPROVED** | [activity-logging-v1.md](../../outbox/specs/activity-logging-v1.md), [REVIEW](../../outbox/reviews/REVIEW_activity-logging-v1.md) |
| F-110 / F-111 catalogued | Done | [functions.md](./requirements/functions.md) v1.4 |
| Implementation JSONL + XFF IP | Done | `src/vai/activity_log.py`, `server.py`, `cli.py` |
| Default log path | Done | `logs/activity.jsonl` (gitignored) |
| Tests | Done | 92 passed (incl. `test_activity_log`, server XFF) |
| Commit + push `master` | Done | `7d36f44`, `705a477` → origin |
| Prod deploy | Operator / optional | `sudo bash /opt/vai/deploy/update-server.sh` then `tail -f /opt/vai/logs/activity.jsonl` |

### Operator notes

- Each HTTP response → one JSONL event: `ts`, `client_ip`/`peer_ip`, `operation`/`function`, `status`.
- No bodies/seeds in logs. Distinct from TRACE-LOG / F-014.
- View: `tail -f logs/activity.jsonl` (dev) or under `/opt/vai` after deploy.
- Disable: `python -m vai serve --activity-log none` or `VAI_ACTIVITY_LOG=none`.

### Carry-over

- Confirm prod service writes `/opt/vai/logs/activity.jsonl` after `update-server.sh` if not already deployed.
- Next race-day: V85 Hari/Expert entry (UC-22).

---

## End of session — 2026-07-29 (expert panel UX)

**Session owner:** ornstein  
**Status:** **Closed (O&O)**  
**Dev:** `/home/ornstein/grok/vai` @ `dd09fc3` (+ this TRACE-LOG close-out)  
**Production:** https://vai.ornstein.work/ — deploy still **blocked** (agent shell has no sudo password)

### Completed this session

| Item | Status | Artifact |
|------|--------|----------|
| Count `N synliga av M · K med tip …` | Done | `879e1e6`; list API `counts` |
| **Markera alla** / **Avmarkera alla** | Done | `PUT /api/v1/experts/visibility` |
| ↑/↓ display order (roster YAML order) | Done | `PUT /api/v1/experts/reorder` |
| Dark theme for visibility controls | Done | `dd09fc3` |
| Spec v0.4, UC-12 1.5, README | Done | [expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md) |
| Tests | Done | 26 pass (`test_experts_roster`, `test_server`) |
| Commit + push `master` | Done | `879e1e6`, `dd09fc3` → origin |
| Prod deploy | **Blocked** (sudo password) | Operator: `sudo bash /opt/vai/deploy/update-server.sh` |

### Operator notes

- Main panel shows only **visible** experts; order follows `inbox/experts/roster.yaml` (or defaults).
- Manage visibility + order in **VISA EXPERTER**; hard-refresh after deploy.
- Soft-hide + VISA EXPERTER (`76a3906`) and this UX ship together when prod is updated.

### Carry-over

- Prod deploy: `sudo bash /opt/vai/deploy/update-server.sh` (soft-hide → VISA EXPERTER → counts/select-all/reorder/dark theme)
- ~~Promote expert-roster-manage-v1~~ — **APPROVED** → [outbox/specs/expert-roster-manage-v1.md](../../outbox/specs/expert-roster-manage-v1.md)
- Next race-day: V85 Hari/Expert entry (UC-22)

---

## Ship — expert panel UX (counts, select-all, reorder) — 2026-07-29

**Session owner:** ornstein  
**Dev:** `/home/ornstein/grok/vai`  
**Production:** https://vai.ornstein.work/

### Completed

| Item | Status | Artifact |
|------|--------|----------|
| Count + API `counts` | Done | `879e1e6` |
| Bulk visibility + reorder API/UI | Done | `879e1e6` |
| Dark theme Markera/Avmarkera + ↑/↓ | Done | `dd09fc3` |
| Spec v0.4 / UC-12 1.5 | Done | [expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md) |
| Commit + push `master` | Done | `879e1e6`…`dd09fc3` → origin |
| Prod deploy | **Blocked** (sudo password in agent shell) | Operator: `sudo bash /opt/vai/deploy/update-server.sh` |

### Operator notes

- After deploy: hard-refresh Expert tab — count line, **VISA EXPERTER** bulk buttons, ↑/↓ order, mörk-mode controls.
- Reorder persists in working `inbox/experts/roster.yaml`; reset API restores default order/visibility.

### Carry-over

- Prod deploy when ready: `sudo bash /opt/vai/deploy/update-server.sh`
- ~~Promote expert-roster-manage-v1~~ — **APPROVED** → [outbox/specs/](../../outbox/specs/expert-roster-manage-v1.md)

---

## End of session — 2026-07-29

**Session owner:** ornstein  
**Status:** **Closed**  
**Dev:** `/home/ornstein/grok/vai` @ `cdca2c4`  
**Production:** https://vai.ornstein.work/ — deploy still **blocked** (agent shell has no sudo password)

### Completed this session

| Item | Status | Artifact |
|------|--------|----------|
| Q&A: **Redo** on Expert roster cards | Done | badge = `has_tip` for selected datum (“ready”) |
| Commit (feature code) | N/A — no code changes | feature HEAD was `1488e38` |
| TRACE-LOG close-out + push | Done | `cdca2c4` → origin/master |
| Prod deploy | **Blocked** (sudo password) | Operator: `sudo bash /opt/vai/deploy/update-server.sh` |

### Operator notes

- **Redo** ≠ undo/redo; ≠ roster reset. Means a transcribed tip exists for the selected race date.
- After deploy: hard-refresh Expert tab for **VISA EXPERTER** + soft-hide UI (`76a3906` still pending on prod if last deploy was before that).

### Carry-over

- Prod deploy: `sudo bash /opt/vai/deploy/update-server.sh` (ships soft-hide + VISA EXPERTER if not yet on prod)
- Promote [expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md) to `outbox/specs/` when operator APPROVED
- Next race-day: V85 Hari/Expert entry (UC-22)

---

## Ship — expert roster soft-hide + VISA EXPERTER — 2026-07-29

**Session owner:** ornstein  
**Dev:** `/home/ornstein/grok/vai`  
**Production:** https://vai.ornstein.work/

### Completed

| Item | Status | Artifact |
|------|--------|----------|
| Soft-hide (`visible`) | Done | `df9fc83` |
| **VISA EXPERTER** popup; main panel = visible only | Done | `76a3906` |
| Spec v0.3, UC-12 1.4 | Done | [expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md) |
| Commit + push `master` | Done | `76a3906` → origin |
| Prod deploy | **Blocked** (sudo password in agent shell) | Operator: `sudo bash /opt/vai/deploy/update-server.sh` |

### Operator notes

- After deploy: hard-refresh Expert tab (**VISA EXPERTER**; no per-card Visa; no trash).
- Soft-hide keeps rows in working `inbox/experts/roster.yaml`; tips under `inbox/expert-tips/` stay.
- Full reset is API-only (`POST /api/v1/experts/reset`); toolbar button is **VISA EXPERTER**.

### Carry-over

- Prod deploy when ready: `sudo bash /opt/vai/deploy/update-server.sh`
- Promote [expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md) to `outbox/specs/` when operator APPROVED

---

## End of session — 2026-07-28

**Session owner:** ornstein  
**Status:** **Closed (O&O)**  
**Dev:** `/home/ornstein/grok/vai` · serve **8766**  
**Production:** https://vai.ornstein.work/ (deploy: `sudo bash /opt/vai/deploy/update-server.sh` if not yet applied)

### Completed this session

| Item | Status | Commits / artifact |
|------|--------|--------------------|
| Plan + ship **add / delete experts** + **restore default set** | Done | `585af6d` |
| Working roster full copy | Done | `inbox/experts/roster.yaml` (after first edit); defaults stay `src/vai/strategies/experts.yaml` |
| API: POST/PUT/DELETE `/api/v1/experts`, POST `/api/v1/experts/reset` | Done | `src/vai/server.py`, `io/experts_roster.py` |
| Expert tab: Lägg till expert, trash → later Visa soft-hide | Done | `585af6d`; soft-hide `df9fc83` |
| Full reset = overwrite working with shipped defaults | Done | product decision ER-005 |
| Spec F-044–048, UC-12 alternate, tests | Done | [expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md) |
| Commit + push `master` | Done | `585af6d` → origin |

### Operator notes

- **Lägg till expert** → working roster under `inbox/experts/` (prod: `/opt/vai/inbox/experts/`).
- Soft-hide (2026-07-29): **Visa** tick-box; tip files under `inbox/expert-tips/` remain.
- **Återställ roster** restores the shipped default set (customs gone; tips still kept).
- Hard-refresh Expert tab after deploy to pick up mockup HTML.

### Carry-over

- Prod deploy: `sudo bash /opt/vai/deploy/update-server.sh`
- Promote [expert-roster-manage-v1.md](../../pending/specs/expert-roster-manage-v1.md) to `outbox/specs/` when operator APPROVED
- Optional: add Eddie Östlund via UI (or defaults) when transcribed regularly
- Next race-day: V85 Hari/Expert entry (UC-22)

---

## End of session — 2026-07-27 (experts research)

**Session owner:** ornstein  
**Status:** **Closed (O&O)**  
**Dev:** `/home/ornstein/grok/vai`

### Completed this session

| Item | Status | Artifact |
|------|--------|----------|
| `/deep-research` V85 experts sharing full 8-leg systems | Done (Partial) | workflow deep-research |
| Inbox research note + comparison vs roster | Done | [2026-07-27-deep-research-v85-experts.md](../../inbox/research/2026-07-27-deep-research-v85-experts.md) |
| Free full-system outlets re-validated (5 + 2 hubs) | Match VAI | Travcash, Rekatochklart, Trav.se, Travstugan, Travmaskinen; Trava På!, Gratistravtips.se |
| Scorecard: net-new vs enrich vs flag review | Logged | same research note |

### Research takeaway (experts / full systems)

- VAI free-priority list and hubs **already correct** — research is validation, not overhaul.
- **Only clear roster candidate:** Eddie Östlund (Travcash free tipster).
- Enrich later if useful: Trav.se writers (BelminK, Kåvestam, Lönnaeus); Trav365 Nicklasson/Carlsson.
- Optional flag review: `thomas-uhrberg` (full system on Bollnäs 25/7 vs `partial`); Travmaskinen builder vs fixed free matrix.
- Manual tip transcription remains the path (see screen-scrape research).

### Carry-over

- Optional: add `eddie-ostlund` via Expert roster UI when/if transcribed regularly
- Optional: Nisse review if roster notes should land in `docs/strategies/expert.md`
- Next race-day: V85 Hari/Expert entry (UC-22)

---

## End of session — 2026-07-27

**Session owner:** ornstein  
**Status:** **Closed (O&O)**  
**Dev:** `/home/ornstein/grok/vai` · serve **8766**  
**Production YAML path:** `/opt/vai/inbox/expert-tips/<YYYY-MM-DD>-<track-slug>/<tip_id>.yaml`

### Completed this session

| Item | Status | Commits / artifact |
|------|--------|--------------------|
| Experttips form UI — form icon left of Gratis / Andel/betald | Done | `79b640d` |
| Empty form when no YAML; prefill when tip exists; Avbryt / Spara | Done | `79b640d` |
| Save → `inbox/expert-tips/` (PUT API + IO helpers) | Done | `79b640d` |
| Refresh **Tips för omgången** after save (optimistic + cache-bust) | Done | `b4ceaf9` |
| **Radera** — only enabled when tip YAML already saved; DELETE API | Done | `70e64ba` |
| **/deep-research screen-scrape expert tip** — logged to inbox research | Done | [2026-07-27-deep-research-screen-scrape.md](../../inbox/research/2026-07-27-deep-research-screen-scrape.md) |
| Decision: **no tip scraper in v1**; manual YAML only; ATG ToS gate | Logged | same research note |
| Push to GitHub | Done | `79b640d`…this close-out |

### Research takeaway (screen-scrape)

- Expert tips stay **manual transcription** → `inbox/expert-tips/`.
- ATG terms (from 2026-01-01) forbid automated extraction; several tip outlets also restrict bots/redistribution.
- Free full systems are HTML (Travcash, Trav.se, Rekatochklart, …) — no public tips JSON API found.

### Operator notes

- Form writes/reads production tips under **`/opt/vai/inbox/expert-tips/`** when serving prod (`vai.service`).
- Dev clone uses **`~/grok/vai/inbox/expert-tips/`**.
- Hard-refresh Expert tab after deploy to pick up mockup HTML.

### Carry-over

- Run prod deploy if not yet applied: `sudo bash /opt/vai/deploy/update-server.sh`
- Next race-day: V85 Hari/Expert entry (UC-22)
- Optional: Nisse/Povl review of screen-scrape research if policy text should land in `docs/strategies/expert.md`

---

## End of session — 2026-07-25

**Session owner:** ornstein  
**Status:** **Closed** — Mac access verified; operator signed off.

### Completed

| Item | Status |
|------|--------|
| Mac Terminal SSH as `ornstein@168.119.155.11` | OK |
| Port tunnel `-L 8766:127.0.0.1:8766` + browser on Mac | OK |
| Same tunnel flow as Windows PC | Confirmed |
| Operator note | “Mac works good” → close session |

### Carry-over (unchanged)

- Production: https://vai.ornstein.work/ (Expert v1.3.0+ as last deployed)
- Dev: `~/grok/vai`, serve on **8766**; tunnel docs in [deploy-hetzner.md](./deploy-hetzner.md#browse-dev-ui-from-your-pc-ssh-tunnel)
- Next race-day: V85 Hari/Expert entry (UC-22)

---

## End of session — 2026-07-24

**Session owner:** ornstein  
**Git:** `origin/master` @ `fa09597` (Expert release); TRACE-LOG close-out may be a follow-up commit  
**Production:** https://vai.ornstein.work/ — **v1.3.0** deployed (ornstein as root + `update-server.sh`)  
**Dev:** `/home/ornstein/grok/vai` · serve default port **8766** (prod uses **8765**)

### Completed this arc (Expert / UC-12)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| A / product | Expert = **select published betslips** (not spik/halvleg pattern engine) | Done |
| I | Travet experts research inbox → `inbox/research/2026-07-15-experts-travet.*` | Done |
| R | UC-12 rewrite, `expert-v1.md`, `docs/strategies/expert.md` v0.3 | Done |
| Code | Tip YAML I/O, `generate_expert_v1`, CLI `expert list/apply` | Done |
| API | `GET /api/v1/experts`, `GET /api/v1/expert-tips`, `POST /api/v1/generate/expert` | Done |
| UX | Expert tab: roster, tips list, load tip, **edit horses**, live cost/slip, dark theme | Done |
| Roster | ~30 experts in `experts.yaml` (Goop, Referenten, Travstugan, Leboff, …) | Done |
| Ops | SSH tunnel docs verified; dev port default **8766** | Done |
| P | Commit `fa09597` + push + **production deploy v1.3.0** | Done ✓ |

### Verified on production (2026-07-24)

- https://vai.ornstein.work/ serves **v1.3.0**
- `GET /api/v1/experts` → **200** (roster JSON)
- Expert tab enabled (no longer “Kommer senare”)

### Open for next session

| Item | Owner |
|------|--------|
| Next Saturday V85 — Hari and/or Expert; UC-22 entry | Kricke / ornstein |
| ~~Transcribe real expert tips~~ → **done 2026-07-25** (Bollnäs five tips) | ornstein |
| Optional: commit this TRACE-LOG close-out + redeploy if needed | ornstein |
| **v1.2** — reduced-stake (UC-14 §3a); ATG disk cache | Povl |
| Housekeeping — archive duplicate `pending/` copies of published artifacts | Assistant |
| OI-004 — Spelstopp after Sept 2026 schedule change | Nisse |

### Notes

- **Ingestion remains manual** (YAML transcription); no ATG tip scrape in v1.3.
- Daily work as **`ornstein`**; deploy as root/`sudo` only when shipping.
- Tunnel for unreleased dev: `ssh -L 8766:127.0.0.1:8766 ornstein@168.119.155.11` then http://127.0.0.1:8766/

---

## Expert tips — Bollnäs 2026-07-25

**AIRUP:** I (Inbox) · **Mode:** Expert (UC-12) · **Game:** V85  
**Path:** `inbox/expert-tips/2026-07-25-bollnas/`  
**Operator:** ornstein (manual transcription) · **Status:** all `DRAFT` until double-checked against sources

| tip_id | Expert | Product / source | Combos | Cost (SEK) | Commit |
|--------|--------|------------------|--------|------------|--------|
| `bjorn-goop-2026-07-25` | Björn Goop | Björnkollen / ATG | 1600 (`5×1×5×1×4×4×4×1`) | 800 | `225ce90` |
| `travstugan-2026-07-25` | Travstugan | travstugan.se | 640 (`2×4×1×1×4×5×4×1`) | 320 | `dfe646c` |
| `referenten-2026-07-25` | Albin "Referenten" Engdahl | Travcash / ATG butik | 9216 (`8×1×8×1×6×3×8×1`) | 4608 | `32d8cbc` |
| `leboff-2026-07-25` | Leboff | Rekatochklart | 3024 (`2×3×7×2×3×4×1×3`) | 1512 | `32d8cbc` |
| `thomas-uhrberg-2026-07-25` | Thomas Uhrberg | thomasuhrberg.se | 2430 (`3×1×9×1×6×5×3×1`) | 1215 | `32d8cbc` |

### Source URLs

| tip_id | source_url |
|--------|------------|
| bjorn-goop | https://www.atg.se/V85/tips/bjornkollen-v85-lordag |
| travstugan | https://travstugan.se/tidiga-v85-bra-dag-for-djuse |
| referenten | https://www.atg.se/butik/icatierp/spel/208992_V85_2026-07-25_12_5 |
| leboff | https://www.rekatochklart.com/trav/v85-tips/v85-tips-bollnas-25-7/ |
| thomas-uhrberg | https://thomasuhrberg.se/v85-bollnas-25-juli/ |

### Ops

- Tips listed by Expert mode via `GET /api/v1/expert-tips?date=2026-07-25&track=Bollnäs`.
- Production: ship with `sudo bash /opt/vai/deploy/update-server.sh` after each push (Björnkollen verified live earlier; remaining tips on `master` @ `32d8cbc`).
- No code change — inbox YAML only. Cost formula: ∏(horses per leg) × 0.50 SEK.

---

## Release v1.3.0 — 2026-07-24

**Product line:** Expert mode (UC-12 betslip catalog) + Hari unchanged. **v1.2** still reserved for reduced-stake / ATG disk cache.

### Shipped

| Area | Change |
|------|--------|
| Mode | Expert tab: list/select professional tips; load full 8-leg system |
| Data | `inbox/expert-tips/` YAML schema; fixture tip Axevalla 2026-07-18 |
| Roster | `src/vai/strategies/experts.yaml` + `GET /api/v1/experts` |
| UX | Edit horses after load; auto + **Uppdatera spelkvitto**; dark theme for Expert |
| API/CLI | `generate/expert`, `expert-tips`; `python -m vai expert list\|apply` |
| Package | `pyproject.toml` / `vai.__version__` → **1.3.0** |
| Specs | `outbox/specs/expert-v1.md`; UC-12, expert.md, functions F-040–043 remapped |

### Commit / deploy

- Commit: `fa09597`
- Deploy: `bash /opt/vai/deploy/update-server.sh` (ornstein as root) → https://vai.ornstein.work/

---

## End of day — 2026-07-14

**Session owner:** ornstein (O&O)  
**Git remote:** `origin` → `https://github.com/jonasornstein/VAI.git` (`master` synced)  
**Production:** https://vai.ornstein.work/ (Hetzner `dev-server`, `168.119.155.11`)

### Completed

| Phase | Deliverable | Status |
|-------|-------------|--------|
| Ship | ATG → VAI package rename (`src/vai/`, `python -m vai serve`) | `4d0e120` |
| Ship | GitHub repo renamed and made **public** | VAI.git |
| Ship | Hetzner first deploy — systemd + nginx + certbot TLS | Live ✓ |
| Fix | nginx HTTPS 403 → `deploy/fix-nginx-https.sh` | Done |
| Fix | Server git drift — `reset --hard origin/master`, git as `vai` user | Done |
| Fix | HEAD requests for `curl -I` health checks | `7716174` |
| Ship | Operator deploy doc | [deploy-hetzner.md](./deploy-hetzner.md) |
| Ship | `deploy/update-server.sh` routine update path | `c87b38a` |
| U | Vercel deployment artifacts removed (Hetzner-only production) | `9102c4e` |
| Verify | HTTPS 200; Hari UI loads in browser | ornstein ✓ |

### Published / deployed artifacts (today)

- **Production URL:** https://vai.ornstein.work/
- **Docs:** `docs/deploy-hetzner.md`
- **Deploy:** `deploy/install-ubuntu.sh`, `setup-domain.sh`, `fix-nginx-https.sh`, `update-server.sh`
- **Code:** `src/vai/server.py` (HEAD), branch `master` on GitHub

### Open for next session

| ID | Item | Owner |
|----|------|-------|
| — | **Race day** — V85 Axevalla 2026-07-18; ATG fetch + Hari proposal; UC-22 entry | Kricke / ornstein |
| — | Optional server sync after `9102c4e` (Vercel file cleanup on disk) | ornstein |
| — | **v1.2** — reduced-stake (UC-14 §3a); ATG disk cache | Povl |
| — | Housekeeping — archive duplicate `pending/` copies | Assistant |
| OI-004 | Spelstopp after Sept 2026 schedule change — TBD | Nisse |

### Notes

- Production stack: nginx :443 → `127.0.0.1:8765` (`vai.service`). No Vercel.
- Server updates: `bash /opt/vai/deploy/update-server.sh` (git as `vai`, not root).
- `curl -I` and browser GET both return 200 after HEAD fix.
- Local dev unchanged: `python -m vai serve` → http://127.0.0.1:8765/

---

## Release v1.1.4 — 2026-07-15

**Product line:** Hari (random) local UI patch on v1.1. **v1.2** remains reserved for reduced-stake (UC-14 §3a) and ATG disk cache.

### Shipped

| Area | Change |
|------|--------|
| UX | Horse buttons (option A): start number + V85 pool % + vinnare odds |
| UX | Bet slip chips: operator **bold** / system *italic* + odds; spik name kept |
| UX | Dark theme: brighter pool % / odds on buttons and slip |
| API | `leg_odds` on ATG race-card payload (`extract_leg_odds` from `pools.vinnare.odds`) |
| Package | `pyproject.toml` / `vai.__version__` → **1.1.4** |

### Verification

- 39 pytest tests pass
- Live ATG card (Axevalla): pool/odds on buttons; slip chips after generate
- Operator sign-off light + dark themes
- Production: https://vai.ornstein.work/ after `update-server.sh`

---

## Release v1.1.3 — 2026-07-15

**Product line:** Hari (random) local UI patch on v1.1. **v1.2** remains reserved for reduced-stake (UC-14 §3a) and ATG disk cache.

### Shipped

| Area | Change |
|------|--------|
| UX | Bet slip: operator-selected horse numbers **bold** (`.slip-horse-op`) |
| UX | Bet slip: system/random horse numbers *italic* (`.slip-horse-sys`) |
| UX | Bet slip: five-space gaps between numbers (`&nbsp;` × 5 + inner span so flex keeps gaps) |
| Package | `pyproject.toml` / `vai.__version__` → **1.1.3** |

### Verification

- Operator confirmed bold/italic/spacing on Genererat spel
- Local UI: `python -m vai serve` → http://127.0.0.1:8765/ (prod after deploy)

---

## Release v1.1.2 — 2026-07-11

**Product line:** Hari (random) local UI patch on v1.1. **v1.2** remains reserved for reduced-stake (UC-14 §3a) and ATG disk cache.

### Shipped

| Area | Change |
|------|--------|
| UX | Strukna hästar shown in leg grid — red number, strikethrough, unselectable |
| UX | Betslip spik rows show `7 Hankypanky Leonie` (number + name) when one horse selected |
| API | `legs[].horse_names` from ATG `starts[].horse.name`; optional in manual YAML |
| Package | `pyproject.toml` / `atg.__version__` → **1.1.2** |

### Verification

- 37 pytest tests pass
- Local UI: `python -m atg serve` → http://127.0.0.1:8765/

---

## End of day — 2026-07-08

**Session owner:** ornstein  
**Git remote:** `origin` → `https://github.com/jonasornstein/ATG.git` (`master` synced)

### Completed

| Phase | Deliverable | Status |
|-------|-------------|--------|
| Plan | UC-15 Race-info — race-level metadata per avdelning (scope confirmed) | Done |
| Ship | F-029 `extract_race_info` — name, distance, start method, class from ATG JSON | `319a12e` |
| Ship | Multi-line leg headers in local UI (`.race-info-primary/secondary/class`) | Done |
| Fix | Scratched horses excluded from `legs[].horses` (schema rule 5) | Done |
| Review + Publish | UC-15 APPROVED, `race-info-v1.md`, race-card-schema v1.1 | Done |
| Verify | Operator sign-off — race info headers look great in browser | ornstein ✓ |
| Ops | ATG server restarted (`python -m atg serve` → :8765) | Done |

### Published / approved artifacts (today)

- **Spec:** `outbox/specs/race-info-v1.md`
- **Use case:** `docs/requirements/use-cases/UC-15-race-info.md`
- **Review:** `outbox/reviews/REVIEW_UC-15_race-info.md`
- **Code:** `src/atg/atg_race_card.py`, `models/race_card.py`, mockup, 34 tests pass

### Open for next session

| ID | Item | Owner |
|----|------|-------|
| — | **Race day Saturday** — Årjäng 2026-07-11; re-fetch with race info; UC-22 ATG entry | Kricke / ornstein |
| — | **v1.2** — reduced-stake (UC-14 §3a); ATG disk cache | Povl |
| — | Per-horse info in leg grid (deferred from UC-15 v1) | Future |
| — | Housekeeping — archive duplicate `pending/` copies | Assistant |
| OI-004 | Spelstopp after Sept 2026 schedule change — TBD | Nisse |

### Notes

- Race info uses existing `games/{game_id}` fetch — no extra ATG call.
- YAML inbox cards without `race_info` still show time-only headers.
- Local UI: http://127.0.0.1:8765/

---

## End of day — 2026-07-07

**Session owner:** ornstein  
**Git remote:** `origin` → `https://github.com/jonasornstein/ATG.git` (`master` synced)

### Completed

| Phase | Deliverable | Status |
|-------|-------------|--------|
| Ship | Random v1.1 + local UI (`python -m atg serve`) — exact budget, ATG fetch, nearest stake, F-052 basic, F-071 checklist | Done |
| Review + Publish | `random-v1.1.md`, `atg-data-source.md`, `local-ui-v1.1.md` | APPROVED |
| Review + Publish | UC-11, ux-workflow, race-card-schema v1.0 | APPROVED |
| Review + Publish | All 13 remaining use cases v1.0 — Phase 2b complete | `b571037` |
| Review + Publish | `functions.md` v1.0, `supplementary-specification.md` v1.0 — **RUP trilogy complete** | `9d76d89`, `b2670cc` |
| Proposal | V85 Årjäng 2026-07-11 — Hari seed 42, 500 SEK, 1 000 rader | [outbox/proposals/v85/2026-07-11-arjang/](../../outbox/proposals/v85/2026-07-11-arjang/) |
| Tooling | Try-out scripts (UI screenshot, hit tooltip, live V85 API) | `268de32` |
| Docs | `functions.md` v0.4 refresh; VISION Phase 3b link fix; scope-lock + random-v1.1 promotion checklists ✓ | Done |

### Published / approved artifacts (today)

- **Specs:** `outbox/specs/random-v1.1.md`, `atg-data-source.md`, `local-ui-v1.1.md`
- **Requirements:** all `docs/requirements/use-cases/UC-*.md`, `use-case-model.md` v0.4, `functions.md` v1.0, `supplementary-specification.md` v1.0, `ux-workflow.md`, `race-card-schema.md`
- **Reviews:** `outbox/reviews/REVIEW_*` (UC-11, ux-workflow, race-card-schema, use-cases batch, functions, supplementary)
- **Proposal:** `outbox/proposals/v85/2026-07-11-arjang/`

### Open for next session

| ID | Item | Owner |
|----|------|-------|
| — | **Race day** — re-fetch Årjäng 2026-07-11; scratches/reserves; UC-22 ATG entry | Kricke / ornstein |
| — | **v1.2** — reduced-stake systems (UC-14 §3a); ATG disk cache | Povl |
| — | Expert / Quant modes — UX tabs disabled; UC-12/13 spec-only | Nisse / Povl |
| — | Housekeeping — archive duplicate `pending/specs/` and `pending/mockups/` | Assistant |
| OI-004 | Spelstopp after Sept 2026 schedule change — TBD | Nisse |

### Notes

- Hari (random) v1.1 is the only active mode; Expert/Kvant show *Kommer senare*.
- Local UI: http://127.0.0.1:8765/ after `python -m atg serve`.
- No automated bet placement — proposals are operator-transcribed artifacts only.

---

## End of day — 2026-07-06

**Session owner:** ornstein  
**Git remote:** `origin` → `https://github.com/jonasornstein/ATG.git` (`main` + `master` synced)

### Completed

| Phase | Deliverable | Status |
|-------|-------------|--------|
| Research | V85 2026 payout rules verified (S-013, N-004); stale sources flagged | Done |
| Review + Publish | `docs/betting/v85.md` v1.0 APPROVED | `87eff44` / `c26587a` |
| Review + Publish | `docs/strategies/quantitative.md` v0.3 APPROVED | `7e50237` / `54dcfef` |
| UX (mockup) | V85 proposal UI v0.1 → v0.3; ATG.se colors/CSS; light/dark toggle | Done |
| Publish | UX mockups → `outbox/mockups/` | `0ca357c` / `51987af` |

### Published artifacts (outbox)

- `outbox/reviews/REVIEW_v85_rules.md`, `REVIEW_quantitative.md`
- `outbox/research/PENDING-RESEARCH_v85_rules.md` (archive)
- `outbox/mockups/` — html, png, pdf (light + dark)

### Open for next session

| ID | Item | Owner |
|----|------|-------|
| — | Real race day: fresh YAML + operator pools → proposal | Kricke / ornstein |
| — | ATG auto-fetch spec (`pending/specs/atg-data-source.md`) | Povl |
| — | Expert / Quant generators — **on hold** until ornstein directs | Povl |
| OI-001 | Ingest S-009b Swedish *Spelregler Häst* when ATG updates PDF | Nisse |
| OI-004 | Spelstopp after Sept 2026 schedule change — TBD | Nisse |

### Notes

- Mockup working copies remain in `pending/mockups/`; canonical published versions in `outbox/mockups/`.
- No automated bet placement — proposals are operator-transcribed artifacts only.