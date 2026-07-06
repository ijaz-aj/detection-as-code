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

## Phase 2 — Write the detections  🚧 in progress

**Goal:** author 12 Sigma rules meeting docs/detection-standard.md, each compiled to Splunk SPL,
Elastic (Lucene/ECS), and Microsoft Sentinel (KQL).

Conversion strategy (per rule's telemetry):
- Splunk: `-t splunk -p splunk_windows`
- Elastic: `-t lucene -p ecs_windows` (ECS fields, matches lab data)
- Sentinel: process_creation rules -> `-t kusto -p microsoft_xdr` (DeviceProcessEvents, full query);
  other Sysmon events -> `-t kusto -O query_table=Sysmon` condition wrapped as `Sysmon | where ...`;
  Windows Security events -> SecurityEvent table.
- Lint with `sigma check -x attacktag` (pySigma 1.4.0 attacktag validator has an outdated tactic list).
- Correlation/aggregation rules (e.g. brute force): Splunk converts natively; Elastic needs **ES|QL**
  (`-t esql`, Lucene/EQL can't do correlations); Sentinel Kusto backend has no correlation support yet
  so the KQL is hand-authored (documented in the rule's .kql file).

Rules completed (2 / 12):
- [x] 1. PowerShell encoded command — Execution / T1059.001 — Sysmon EID 1
- [x] 2. LSASS memory access — Credential Access / T1003.001 — Sysmon EID 10
- [x] 3. mshta/rundll32 abuse — Defense Evasion / T1218.005+011 — Sysmon EID 1
- [x] 4. Failed logon brute force — Credential Access / T1110 — Security 4625 (correlation rule)
- [x] 5. New service install — Persistence+PrivEsc / T1543.003 — System 7045
- [ ] 6. Scheduled task creation — Persistence / T1053.005 — Security 4698
- [ ] 7. RDP logon type 10 — Lateral Movement / T1021.001 — Security 4624
- [ ] 8. Account created then added to admins — Persistence / T1136+T1098 — 4720/4732
- [ ] 9. Suspicious Office->shell parent-child — Execution / T1059 — Sysmon 1
- [ ] 10. DNS query to suspicious TLD — C2 / T1071.004 — Sysmon 22
- [ ] 11. Renamed system binary — Defense Evasion / T1036.003 — Sysmon 1
- [ ] 12. PowerShell download cradle — Execution / T1059.001 — Sysmon 1
## Phase 3 — Attack → detect → tune  ⬜ not started
## Phase 4 — CI/CD pipeline & ATT&CK coverage map  ⬜ not started
## Phase 5 — Python phishing / IOC triage tool  ⬜ not started
## Phase 6 — Polish and publish  ⬜ not started
