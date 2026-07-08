# PROGRESS.md — Phase Log

A running log of what was built in each phase. Newest entries at the top of each phase section.

---

## Phase 0 — Repo scaffold and standards  ✅ complete (2026-07-05)

**Goal:** a clean, professional skeleton before any real detection content.

- [x] `git init`, default branch renamed to `main`, local commit identity set
- [x] Directory structure created (`detections/` per ATT&CK tactic, `tests/`,
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
- [x] Screenshots to docs/screenshots/ — 01-fleet-healthy.png + 02-sysmon-discover.png (committed)

## Phase 2 — Write the detections  ✅ complete (2026-07-06)

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
- [x] 6. Scheduled task creation — Persistence+Execution / T1053.005 — Security 4698
- [x] 7. RDP logon type 10 — Lateral Movement / T1021.001 — Security 4624 (azure_monitor maps it clean)
- [x] 8. User added to privileged group — Persistence+PrivEsc / T1098 — Security 4732 (SID-based)
- [x] 9. Office->shell parent-child — Execution / T1059 — Sysmon 1 (parent-child logic)
- [x] 10. DNS query to suspicious TLD — C2 / T1071.004 — Sysmon 22 (hunting-grade, level low)
- [x] 11. Renamed system binary — Defense Evasion / T1036.003 — Sysmon 1 (OriginalFileName mismatch)
- [x] 12. PowerShell download cradle — Execution / T1059.001 — Sysmon 1

**Result:** 12 rules, 12 ATT&CK techniques, 7 tactics, all lint-clean; 36 compiled queries
(12 Splunk SPL + 12 Elastic + 12 Sentinel KQL).
## Phase 3 — Attack → detect → tune  ✅ complete (2026-07-08)

Atomic Red Team installed on the VM (`C:\AtomicRedTeam`), Defender exclusion added.
Verify detections against live ES with `scratchpad` queries / Python (elastic:DacLab-Elastic-2026).

Case studies (docs/case-studies/):
- [x] T1059.001 encoded PowerShell — ran ATH test 15 (`-E`), Rule 1 MISSED in Elastic (Lucene is
      case-sensitive; Sigma case-insensitivity didn't survive). TUNED with case variants → now
      catches pid 8008. Splunk/Sentinel already caught it (case-insensitive operators). Regex `|re`
      modifier unsupported by the pySigma elasticsearch backend.
- [x] T1218.005 mshta — ATH test 2 (vbscript). Defender blocked it first (real-time protection;
      folder exclusion didn't cover inline vbscript from system32) → disabled RTP on lab VM.
      Rule 3 clean catch, first try, no tuning. Screenshot still TODO.
- [x] T1003.001 LSASS — ATH test 2 (comsvcs.dll MiniDump). THREE findings: (1) sensor gap — Sysmon
      EID 10 disabled by default in SwiftOnSecurity config → enabled ProcessAccess for lsass +
      reloaded; (2) precision — Elastic Agent (agentbeat.exe) flooded rule with 0x1010 FPs (136 hits)
      → excluded `\Elastic\Agent\` by path; (3) recall — dump's 0x1fffff full-access open was missed
      → added 0x1fffff. After tune: 136 → 2 clean rundll32→lsass hits. Best case study of the project.
- [x] T1543.003 new service install — ATH test 2. SCOPE finding: default test installs a service
      running its own binary (AtomicService.exe) → Rule 5 MISS by design (7045 landed fine, ImagePath
      matched none of the shell/temp patterns). Overrode binary_path to cmd.exe → Rule 5 CATCH.
      Rule works as scoped (shell/PsExec services); documented two-tier coverage idea for binary
      services. Different finding type: rule scope/coverage tradeoff, not a bug.
- [x] T1110 brute force — controlled 4625 burst (net use loop, fake account, no lockout). First
      CORRELATION-rule validation: verified via ES|QL aggregation (stats count by TargetUserName |
      where >= 10) → bruteforce_test event_count=30, over the ≥10 threshold. Clean catch, no tuning.
      Skill: correlation-verify (aggregate/threshold), not single-event match.
- [x] T1036.003 renamed system binary — ATH test 5 (powershell.exe copied to %APPDATA%\taskhostw.exe
      and run). Clean catch: Rule 11 returned only the masquerade (Image=taskhostw.exe,
      OriginalFileName=PowerShell.EXE) and correctly ignored the legit powershell (filter works).
      Validates the PE-metadata-mismatch idea. Noted scope limit (curated OriginalFileName list).
- [x] T1053.005 scheduled task — ATH test 2 (`SCHTASKS /Create /TN spawn /TR cmd.exe`). TWO findings in
      TWO layers: (1) SENSOR — `auditpol` "Other Object Access Events" = No Auditing by default → no 4698
      logged → enabled `/success`; (2) INDEX — 4698 landed and `TaskContent` XML was visible but rule
      MISSED. Root cause: `winlog.event_data.TaskContent` mapped `keyword` w/ `ignore_above: 1024`; task
      XML exceeds it → value stored in _source but NOT indexed (`_ignored`) → unsearchable. Fix at index
      layer: `wildcard` override via `logs-system.security@custom` component template + data-stream
      rollover (new `-000002` index = wildcard). Re-ran attack → Rule 6's ORIGINAL query catches, benign
      Windows Update task correctly excluded. Elastic-specific (Splunk/Sentinel unaffected). New failure
      archetype: recorded+visible but unsearchable (index layer). Screenshots 13–16.
- [x] T1098 user added to admins — sensor already on (`auditpol` Security Group Management = Success,
      default). ART test 1 was the WRONG tool (renames Administrator → 4781, not 4732) — used a
      controlled `net user /add` + `net localgroup administrators /add` to fire 4732 (then reverted).
      CLEAN CATCH, no tuning: Rule 8 matched the Administrators add (SID `S-1-5-32-544`) and correctly
      ignored the auto "Users" add (`S-1-5-32-545`). Highlight: SID-based match (locale-independent,
      evasion-resistant) vs name-based. Screenshot 17.

**Phase 3 complete (2026-07-08): 8 documented attack→detect→tune case studies** spanning the full range
of finding types — rule-logic bug (T1059.001), clean catches (T1218.005, T1036.003, T1098), compound
sensor+precision+recall (T1003.001), scope tradeoff (T1543.003), correlation-threshold (T1110), and a
two-layer sensor+index-mapping investigation (T1053.005). Next: Phase 4 (CI/CD + ATT&CK Navigator).
## Phase 4 — CI/CD pipeline & ATT&CK coverage map  ⬜ not started
## Phase 5 — Polish and publish  ⬜ not started

> **Scope note (2026-07-08):** the original Phase 5 (Python phishing / IOC triage tool) was **descoped**
> to keep this a laser-focused detection-engineering repo. That tool, if built, belongs in a separate
> project. Roadmap is now 6 phases (0–5).
