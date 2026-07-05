# PROGRESS.md — Phase Log

A running log of what was built in each phase. Newest entries at the top of each phase section.

---

## Phase 0 — Repo scaffold and standards  ✅ complete (2026-07-05)

**Goal:** a clean, professional skeleton before any real detection content.

- [x] `git init`, default branch renamed to `main`, local commit identity set
- [x] Directory structure created (`detections/` per ATT&CK tactic, `tests/`, `automation/`,
      `docs/`, `lab/`, `.github/workflows/`)
- [x] `.gitignore` (secrets, venv, caches, generated reports)
- [x] `README.md` (starter), `LICENSE` (MIT), `PROJECT.md`, `PROGRESS.md`
- [x] `docs/detection-standard.md` — required fields for every rule
- [x] Python venv + `requirements.txt` (installed cleanly on Python 3.14.5 — no downgrade needed)
- [x] `sigma-cli` verified: Splunk (SPL), Elastic (lucene/eql/esql), Sentinel (kusto/KQL) targets available
- [x] `pytest` runs cleanly (0 tests collected — OK)
- [x] First commit

---

## Phase 1 — Home lab (telemetry flowing)  ⬜ not started
## Phase 2 — Write the detections  ⬜ not started
## Phase 3 — Attack → detect → tune  ⬜ not started
## Phase 4 — CI/CD pipeline & ATT&CK coverage map  ⬜ not started
## Phase 5 — Python phishing / IOC triage tool  ⬜ not started
## Phase 6 — Polish and publish  ⬜ not started
