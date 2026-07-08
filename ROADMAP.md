# Roadmap & Improvement Backlog

The core project (**Phases 0–5**) is complete: 12 Sigma rules across 7 ATT&CK tactics, a reproducible
Elastic home lab, 8 *attack → detect → tune* case studies, a CI pipeline, and an auto-generated ATT&CK
coverage map.

This is a **living backlog** of enhancements. Pick any item, branch, build, and open a PR — CI will
validate it. Effort/value legend: 🟢 quick win · 🟡 moderate · 🔴 larger project.

---

## 1. Detection coverage
- [ ] 🟢 **Discovery** techniques — T1087 (account discovery), T1082 (system info), T1057 (process discovery).
- [ ] 🟢 **Lateral Movement** beyond RDP — T1021.002 (SMB/admin shares), T1021.006 (WinRM).
- [ ] 🟡 **Impact** — T1490 (inhibit recovery: `vssadmin delete shadows`), T1489 (service stop).
- [ ] 🟡 **Exfil / C2 depth** — T1048 (exfil over alternative protocol), T1571 (non-standard port).
- [ ] 🔴 **Linux endpoint** in the lab (auditd / Sysmon-for-Linux) + Linux rules.
- [ ] 🔴 **Cloud** detections (Azure AD sign-ins / AWS CloudTrail) via Sigma cloud logsources.

## 2. Detection depth & quality
- [ ] 🟢 Fill the **T1218.005 mshta screenshot** gap (case-study TODO) and any other evidence gaps.
- [ ] 🟢 Add a per-rule `README.md` linking rule ↔ case study ↔ compiled queries.
- [ ] 🟡 **EQL sequence rules** for multi-step behavior (e.g. Office → PowerShell → network connection).
- [ ] 🟡 More **correlation rules** — e.g. password spray (many accounts, few attempts each).
- [ ] 🟡 **False-positive baselining** over a longer lab run; record per-rule tuning deltas.

## 3. CI/CD & automation
- [ ] 🟢 **Pre-commit hooks** (`sigma check` + `pytest`) so issues are caught before a push.
- [ ] 🟢 Regenerate + **auto-commit the coverage SVG** in CI (currently a manual Navigator export).
- [ ] 🟡 **Compile all three backends** in a CI matrix (not just the Splunk smoke test) — handle the
      correlation rule (ES|QL) and Sentinel per-table pipelines.
- [ ] 🟡 **Golden-file tests** — assert each committed `.spl`/`.lucene`/`.kql` matches a fresh
      conversion, so compiled outputs can't silently drift from the rule.
- [ ] 🔴 **Auto-deploy** validated rules into Elastic detection rules via the Kibana API (close CI → SIEM).

## 4. Tooling
- [ ] 🟢 A **new-rule scaffolder** (`scripts/new_rule.py`) that stamps out the folder + metadata skeleton.
- [ ] 🟡 A **compile-all** script that regenerates every backend output for every rule in one command.
- [ ] 🟡 **Coverage gap analysis** — diff repo coverage against the top-N most-common ATT&CK techniques.

## 5. Lab & telemetry
- [ ] 🟡 Enable richer Windows telemetry — **PowerShell Script Block Logging (4104)**, **command-line
      auditing (4688)**, DNS client logs.
- [ ] 🟡 Add a **second endpoint** to exercise lateral-movement detections realistically.
- [ ] 🔴 **Infrastructure-as-code** the lab (Vagrant / Ansible) so the whole thing stands up in one command.

## 6. Reporting & metrics
- [ ] 🟢 Auto-generate a **coverage summary table** in the README from the layer JSON.
- [ ] 🟡 **Coverage-over-time** — snapshot technique count per release and chart the growth.
- [ ] 🟡 A **layered Navigator** view — detections vs. available data sources ("where am I blind?").

## 7. Documentation & polish
- [ ] 🟢 A **CONTRIBUTING.md** describing the rule standard and how CI validates a change.
- [ ] 🟢 Map each rule to its **ATT&CK data source / component** (what telemetry it depends on).
- [ ] 🟡 Short **blog writeups** derived from the strongest case studies (T1003.001, T1053.005).

---

### Suggested first pick
For a quick, high-value win that sharpens the "detections as software" story:
**§3 pre-commit hooks** or **§4 the new-rule scaffolder** — each is roughly one short session.
