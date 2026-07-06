# Detection Standard

Every detection rule in this repository **must** conform to this standard. The CI pipeline
(`.github/workflows/validate.yml`, from Phase 4) enforces the required fields automatically — a rule
that omits any required field fails the build.

This standard is based on the [official Sigma rule specification](https://github.com/SigmaHQ/sigma-specification)
with a few project-specific conventions layered on top.

---

## 1. File format & location

- Rules are written in **Sigma** — a YAML-based, vendor-neutral detection format. One rule = one
  `.yml` file.
- Each rule lives at: `detections/<attack-tactic>/<rule-name>/<rule-name>.yml`
  - `<attack-tactic>` is the lowercase, hyphenated MITRE ATT&CK tactic (e.g. `credential-access`).
  - The per-rule folder also holds the compiled backend outputs (`*.spl`, `*.kql`, `*.eql`) and,
    later, a short `README.md` case-study link.
- File names use `lowercase-with-hyphens`.

## 2. Required fields

Every rule **must** include all of the following top-level Sigma fields. These are what CI checks.

| Field | Type | Purpose |
|-------|------|---------|
| `title` | string | Short, human-readable name. Describes the behavior, not the tool. Max ~50 chars. |
| `id` | string (UUID) | Globally unique rule identifier. Generate once, never reuse. |
| `status` | enum | Rule maturity: `experimental`, `test`, or `stable`. |
| `description` | string | 1–3 sentences: what this detects and why it matters. |
| `references` | list | URLs backing the detection (ATT&CK page, blog, advisory). At least one. |
| `author` | string | Who wrote it. |
| `date` | date | Creation date, `YYYY-MM-DD` (Sigma uses `YYYY/MM/DD` in older rules; we use ISO). |
| `tags` | list | Must include the ATT&CK technique tag, e.g. `attack.t1003.001`, plus the tactic tag, e.g. `attack.credential-access`. |
| `logsource` | map | Which logs the rule reads (`product`, `category`, and/or `service`). |
| `detection` | map | The detection logic (`selection` blocks + a `condition`). |
| `falsepositives` | list | Known benign triggers. **Never** write "None" — if you can't think of one, think harder. |
| `level` | enum | Severity: `informational`, `low`, `medium`, `high`, or `critical`. |

## 3. Field conventions

### `title`
- Describe the **attacker behavior**: "LSASS Memory Access via Sysmon" — not "T1003 rule".

### `tags` (ATT&CK mapping)
- Always pair the **technique** and its **tactic**:
  ```yaml
  tags:
    - attack.credential_access      # tactic
    - attack.t1003.001              # technique (sub-technique here)
  ```
- Use the exact lowercase ATT&CK IDs. Sub-techniques use a dot: `t1003.001`.
- **Multi-word tactics use an underscore** (SigmaHQ convention): `attack.defense_evasion`,
  `attack.credential_access`, `attack.privilege_escalation`, `attack.lateral_movement`,
  `attack.command_and_control`, `attack.initial_access`, `attack.resource_development`.

> **Validation note:** run `sigma check` with `-x attacktag`. The `attacktag` validator in
> pySigma 1.4.0 ships an outdated tactic list (it calls Defense Evasion "stealth") and wrongly
> flags correct SigmaHQ-convention tags, so we exclude that one validator while keeping all others.

### `logsource`
- Be specific about the telemetry the rule depends on. Examples:
  ```yaml
  logsource:
    product: windows
    category: process_creation    # Sysmon Event ID 1 / Security 4688
  ```
  ```yaml
  logsource:
    product: windows
    service: security             # Windows Security event log (e.g. 4625, 4624)
  ```

### `detection`
- Prefer field-based matching over raw string grep where possible (fewer false positives).
- Keep `condition` readable: `selection and not filter_legit`.

### `falsepositives`
- List concrete, realistic benign sources. This is a graded part of every rule — it proves you
  understand operational impact, not just the attack.

### `level`
- Map to how confidently a hit means "investigate now":
  - `critical` / `high` — high-fidelity, low-noise, act immediately.
  - `medium` — worth review, some noise expected.
  - `low` / `informational` — hunting / correlation fuel, not standalone alerts.

## 4. Required companion documentation

- **False-positive section** (above) is mandatory in the rule itself.
- From Phase 3, every validated technique gets a case study in `docs/case-studies/` following the
  *attack run → log evidence → detection → tuning* structure.

## 5. Example skeleton

```yaml
title: LSASS Memory Access via Sysmon
id: 00000000-0000-0000-0000-000000000000   # replace with a real UUID
status: experimental
description: >
  Detects processes opening a handle to lsass.exe with access rights commonly used to dump
  credentials (e.g. Mimikatz). Relies on Sysmon Event ID 10 (ProcessAccess).
references:
  - https://attack.mitre.org/techniques/T1003/001/
author: ijaz-aj
date: 2026-07-05
tags:
  - attack.credential-access
  - attack.t1003.001
logsource:
  product: windows
  category: process_access        # Sysmon Event ID 10
detection:
  selection:
    TargetImage|endswith: '\lsass.exe'
    GrantedAccess:
      - '0x1010'
      - '0x1410'
  condition: selection
falsepositives:
  - Endpoint security agents (EDR/AV) legitimately reading LSASS memory
  - Backup or diagnostic tooling that inspects process memory
level: high
```
