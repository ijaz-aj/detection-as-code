# Home Lab — Sysmon → Elastic Security

A reproducible single-host lab: a Windows 10 VM running **Sysmon** ships telemetry to a single-node
**Elastic Security** stack (Elasticsearch + Kibana + Fleet Server) running in Docker on the host, via
**Elastic Agent**.

```
  Windows 10 VM (VirtualBox)                 Host (Docker Desktop / WSL2)
  ┌───────────────────────────┐              ┌───────────────────────────────┐
  │  Sysmon (SwiftOnSecurity)  │  Elastic     │  fleet-server  :8220           │
  │  Windows Security log      │  Agent   ───▶│  elasticsearch :9200           │
  │  Elastic Agent             │  (host-only) │  kibana        :5601           │
  └───────────────────────────┘  192.168.56.x └───────────────────────────────┘
        192.168.56.101                ▲ host-only IP 192.168.56.1
```

> **Lab simplification:** the stack runs Elasticsearch **authentication ON but HTTP TLS OFF**. This
> keeps the lab reproducible (no per-machine certificates) and removes agent↔stack TLS friction.
> A production deployment would enable TLS. Agents enrol with `--insecure` for the same reason.

## Prerequisites

- **Docker Desktop** (WSL2 backend) on the host.
- **VirtualBox** with a Windows 10 VM.
- ~14 GB RAM budget free (host + Docker + VM). Tuned for a 16 GB machine.

---

## Part A — Elastic stack (host, Docker)

### 1. Configure secrets
```bash
cd lab
cp .env.example .env
# edit .env: set ELASTIC_PASSWORD, KIBANA_PASSWORD, and a fresh ENCRYPTION_KEY
#   generate a key with:  openssl rand -hex 32   (or: python -c "import secrets;print(secrets.token_hex(32))")
```

### 2. (One-time) raise the map-count limit Elasticsearch needs
Elasticsearch requires `vm.max_map_count >= 262144`. On Docker Desktop / WSL2:
```powershell
wsl -d docker-desktop sysctl -w vm.max_map_count=262144
```

### 3. Bring up the stack
```bash
docker compose up -d
docker compose ps          # wait until es01 + kibana show "healthy"
```
First run pulls ~2 GB of images. The `setup` container sets the `kibana_system` password and exits(0)
— that is expected. Kibana auto-creates two agent policies from `kibana.yml`:
`fleet-server-policy` and `dac-endpoint-policy` ("DaC Windows Endpoint").

### 4. Verify
- Open **http://localhost:5601** (HTTP, not HTTPS). Log in as **`elastic`** / your `ELASTIC_PASSWORD`.
- Cluster health from the host:
  ```bash
  curl -u elastic:$ELASTIC_PASSWORD http://localhost:9200/_cluster/health?pretty
  ```
  Expect `status: yellow` (normal for a single node — replicas can't be assigned).
- Fleet Server reachable from the host (proves it binds to 0.0.0.0, not localhost):
  ```bash
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8220/api/status   # -> 200
  ```

---

## Part B — Windows VM (endpoint)

### VM build
- **VirtualBox VM:** `DaC-Win10-Endpoint`, Windows 10 Enterprise x64, 4 GB RAM, 2 CPU, 60 GB disk.
- **ISO:** Windows 10 Enterprise Evaluation from the
  [Microsoft Evaluation Center](https://www.microsoft.com/en-us/evalcenter/download-windows-10-enterprise)
  (90-day free). This lab used the Windows 10 IoT Enterprise LTSC 22H2 ISO — either works.
- **Guest Additions** installed. **Local account:** `analyst`.

### Networking (host ↔ VM)
- NIC1 = **NAT** (internet for downloads).
- NIC2 = **Host-only** on `192.168.56.0/24` (VirtualBox's default host-only network, DHCP enabled),
  so the agent reaches Fleet Server at `192.168.56.1:8220` and Elasticsearch at `192.168.56.1:9200`.
  ```powershell
  VBoxManage modifyvm "DaC-Win10-Endpoint" --nic2 hostonly `
    --hostonlyadapter2 "VirtualBox Host-Only Ethernet Adapter" --cableconnected2 on
  ```
- Verify from **inside the VM**: `Test-NetConnection 192.168.56.1 -Port 8220` → `TcpTestSucceeded: True`.

### Install Sysmon (Administrator PowerShell in the VM)
```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
New-Item -ItemType Directory -Force C:\Sysmon | Out-Null; Set-Location C:\Sysmon
Invoke-WebRequest "https://download.sysinternals.com/files/Sysmon.zip" -OutFile Sysmon.zip
Expand-Archive Sysmon.zip -DestinationPath . -Force
Invoke-WebRequest "https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml" -OutFile sysmonconfig.xml
.\Sysmon64.exe -accepteula -i sysmonconfig.xml
Get-Service Sysmon64        # -> Running
```

### Enrol Elastic Agent (Administrator PowerShell in the VM)
Download Elastic Agent 8.15.3 (Windows x86_64) from
`https://artifacts.elastic.co/downloads/beats/elastic-agent/elastic-agent-8.15.3-windows-x86_64.zip`,
unzip, then (get the enrolment token from Kibana → Fleet → Enrollment tokens → **DaC Windows Endpoint**,
or the API below):
```powershell
cd C:\elastic-agent-8.15.3-windows-x86_64
.\elastic-agent.exe install --url=http://192.168.56.1:8220 --enrollment-token=<TOKEN> --insecure
```
Get the token from the host:
```powershell
curl.exe -s -u elastic:<PW> -H "kbn-xsrf: true" http://localhost:5601/api/fleet/enrollment_api_keys
# use the api_key whose policy_id = dac-endpoint-policy
```

---

## Verify telemetry is flowing (from the host)
```powershell
$pw="<ELASTIC_PASSWORD>"
curl.exe -s -u elastic:$pw "http://localhost:9200/logs-windows.sysmon_operational-*/_count?q=event.code:1"  # Sysmon proc-create
curl.exe -s -u elastic:$pw "http://localhost:9200/logs-system.security-*/_count?q=event.code:4624"          # Windows logons
```
Both counts should be > 0. In Kibana → **Discover**, select the `logs-*` data view to browse events.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `es01` keeps restarting | `vm.max_map_count` too low | Run the sysctl command in A.2 |
| Kibana crashes on boot (`.find is not a function` / config validation) | complex Fleet config in env vars | It belongs in `kibana.yml`, not env vars (already fixed here) |
| Agent enrol fails: `fail to execute request to fleet-server: EOF` and `curl http://localhost:8220` gives empty reply | Fleet Server bound to `localhost` inside the container | Set `FLEET_SERVER_HOST=0.0.0.0` (in compose) **and** wipe its state so it re-bootstraps: `docker compose rm -sf fleet-server && docker volume rm lab_fleetserverdata && docker compose up -d --no-deps fleet-server` |
| Agent enrol fails with `x509` error | Fleet Server is HTTP; agent tried TLS | Enrol with `--insecure` and `http://` URL |
| Recreating one service errors on `setup` dependency | `setup` is a one-shot | Recreate that service alone: `docker compose up -d --no-deps <service>` |
| Stale/offline agent lingers in Fleet | previous enrolment | Unenrol via Fleet UI, or `POST /api/fleet/agents/<id>/unenroll {"revoke":true}` |

## Reset
```bash
docker compose down          # stop, keep data
docker compose down -v        # stop and DELETE all indexed data (destructive)
```
