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

## Phase 1 — Home lab (telemetry flowing)  ✅ complete (2026-07-06)

**Goal:** real Windows Sysmon logs landing in Elastic Security.

Host decisions: 16 GB RAM machine, so Elastic is RAM-tuned (ES heap 1 GB, mem limits 2/1/1 GB).

- [x] WSL2 installed on host (v2.7.10)
- [x] Docker Desktop installed (4.80.0) + engine running (docker 29.6.1)
- [x] Fresh dedicated VM `DaC-Win10-Endpoint` built (Win10 Enterprise x64, 4 GB/2 CPU/60 GB,
      user `analyst`, Guest Additions installed, NAT nic1). Snapshot `01-clean-os` taken.
- [x] Lab configs authored: `lab/docker-compose.yml` (ES + Kibana + Fleet Server, HTTP+auth, tuned),
      `lab/.env.example`, `lab/.env` (gitignored), `lab/kibana.yml` (Fleet preconfig), `lab/README.md`
- [x] `vm.max_map_count=262144` set in docker-desktop WSL
- [x] Elastic stack up + healthy (es01 + kibana + fleet-server all healthy; Fleet Server online).
      Lab simplified to **HTTP + auth (TLS off)** for reproducibility after TLS/cert/SAN issues —
      documented as a lab-only simplification. Fleet preconfig moved to `lab/kibana.yml`. Policies
      `fleet-server-policy` and `dac-endpoint-policy` (DaC Windows Endpoint) auto-created.
- [x] Kibana login verified in browser (http://localhost:5601, user elastic)
- [x] VM host-only networking: NIC2 host-only added, VM got 192.168.56.101; verified VM can reach
      host ports 9200/8220/5601 (all True). NIC1 stays NAT for internet.
- [x] Sysmon (SwiftOnSecurity config) installed on VM; service Running, logging Event ID 1 etc.
- [x] Elastic Agent 8.15.3 enrolled into dac-endpoint-policy (host DESKTOP-TKIOM3B, online).
      Key fix: Fleet Server bound to localhost inside the container → set FLEET_SERVER_HOST=0.0.0.0
      + wiped fleetserverdata to force re-bootstrap. Enrol with --insecure (HTTP Fleet Server).
- [x] Live telemetry confirmed in ES: Sysmon Event ID 1 = 374, EID 11 = 668; Security 4624 = 387,
      4672 = 358. Data streams logs-windows.sysmon_operational + logs-system.security populated.
- [ ] Screenshots to docs/screenshots/ — USER TODO (Fleet agents healthy, Discover w/ Sysmon events)

## Phase 2 — Write the detections  ⬜ not started
## Phase 3 — Attack → detect → tune  ⬜ not started
## Phase 4 — CI/CD pipeline & ATT&CK coverage map  ⬜ not started
## Phase 5 — Python phishing / IOC triage tool  ⬜ not started
## Phase 6 — Polish and publish  ⬜ not started
