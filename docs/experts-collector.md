# Expert-tips collector (`experts/`)

Lives in `experts/` in the dev checkout on Hetzner (`~/grok/vai/experts`).
Collects public expert tips and pushes them as drafts into production VAI
(`vai.service`, `http://127.0.0.1:8765`), which stores them in
`/opt/vai/inbox/expert-tips/<date>-<track>/`.

- `fetch_experts.py --push --base-url ...` — fetcher/pusher.
- `run_experts.sh` — one run (TZ Europe/Malta); env overrides `VAI_BASE_URL`,
  `VAI_EXPERTS_STATE`, `VAI_API_TOKEN` (Bearer), `EXTRA_ARGS`.
  Output: `experts/state/run-output.log`.
- `experts_sched.sh` — background loop (not cron): Mon–Fri every 3 h
  08:47–20:47 Malta; Sat hourly 08:47–14:47 Malta; no Sunday runs.
- `crontab.txt` — equivalent cron lines (reference).
- `state/` — runtime state, not versioned.

Check it is running: `ps -eo pid,args | grep experts_sched`.
