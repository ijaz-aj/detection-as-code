# Detection-as-Code

A public, reproducible **Detection-as-Code** portfolio project: version-controlled
[Sigma](https://github.com/SigmaHQ/sigma) detection rules mapped to
[MITRE ATT&CK](https://attack.mitre.org/), validated in a real home lab with
[Atomic Red Team](https://github.com/redcanaryco/atomic-red-team), and shipped through a
CI/CD pipeline — the same way modern detection engineering teams manage detections in production.

> **Status:** 🚧 Under active construction. Built in public, one phase at a time.

---

## What this project demonstrates

- **Detection engineering** — Sigma rules with full metadata, mapped to ATT&CK techniques,
  auto-compiled to Splunk SPL, Microsoft Sentinel (KQL), and Elastic.
- **A reproducible home lab** — a Windows VM running Sysmon, shipping telemetry into
  Elastic Security via Elastic Agent.
- **Purple-team validation** — the *attack → detect → tune* loop, driven by Atomic Red Team.
- **CI/CD for detections** — a GitHub Actions pipeline that lints, validates, and test-compiles
  every rule on each push.
- **ATT&CK coverage visibility** — an auto-generated MITRE ATT&CK Navigator layer.
- **Security automation** — a Python phishing / IOC triage tool with API enrichment and a
  no-keys demo mode.

## Repository layout

```
detection-as-code/
├── detections/            # Sigma rules, organized by ATT&CK tactic
├── tests/                 # pytest suite that validates every rule against the standard
├── automation/            # Python phishing / IOC triage tool
├── lab/                   # Home-lab setup (Docker Compose, agent configs, lab README)
├── docs/                  # Detection standard, case studies, coverage map, screenshots
│   ├── case-studies/      # One attack→detect→tune writeup per technique
│   ├── reports/           # Generated triage reports (gitignored)
│   └── screenshots/       # Evidence screenshots
└── .github/workflows/     # CI/CD pipeline
```

## Tech stack

| Area | Tool |
|------|------|
| Detection language | Sigma (converted via `sigma-cli` / pySigma) |
| Lab SIEM | Elastic Security (single-node, Docker) |
| Endpoint telemetry | Windows VM + Sysmon (SwiftOnSecurity config) + Elastic Agent |
| Attack simulation | Atomic Red Team |
| CI/CD | GitHub Actions |
| Automation | Python 3.11+ (standard library + `requests`) |

## Quickstart

> Full setup instructions arrive as each phase lands. See [`PROGRESS.md`](PROGRESS.md) for current
> status and [`PROJECT.md`](PROJECT.md) for architecture and design decisions.

## License

[MIT](LICENSE) © ijaz-aj
