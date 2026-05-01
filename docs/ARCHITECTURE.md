# 🏗️ Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                │
│                                                                │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│   │  Bot #1  │  │  Bot #2  │  │ Human    │  │  Bot #N  │      │
│   │185.220.. │  │ 103.75.. │  │ Researcher│ │45.155..  │      │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│        │             │             │             │             │
└────────┼─────────────┼─────────────┼─────────────┼────────────┘
         │             │             │             │
         │     SSH Connections (Port 2225)         │
         │             │             │             │
         └─────────────┴──────┬──────┴─────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Docker Host      │
                    │  (Ubuntu 22.04)   │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Docker Container │
                    │honeypot-manual-test│
                    └─────────┬─────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
┌────────▼────────┐  ┌────────▼────────┐  ┌───────▼──────┐
│  Real SSH       │  │ Fake Services   │  │ Command      │
│  Daemon         │  │ (Interactive)   │  │ Logger       │
│                 │  │                 │  │              │
│ - PermitRoot    │  │ - mysql         │  │ - DEBUG trap │
│ - Password auth │  │ - redis-cli     │  │ - Logs to    │
│ - Multiple users│  │ - psql          │  │   file       │
└────────┬────────┘  │ - netstat       │  └───────┬──────┘
         │           │ - ps aux        │          │
         │           └────────┬────────┘          │
         │                    │                    │
         │      ┌─────────────┴─────────────┐      │
         │      │    Fake Data Files        │      │
         │      │                           │      │
         │      │ /root/.aws/credentials    │      │
         │      │ /root/.ssh/id_rsa         │      │
         │      │ /root/.git-credentials    │      │
         │      │ /root/.kube/config        │      │
         │      │ /backup/*.sql             │      │
         │      │ /home/deploy/*.yml        │      │
         │      │ /etc/nginx/nginx.conf     │      │
         │      └─────────────┬─────────────┘      │
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  /var/log/attacks/│
                    │  - command_log    │
                    │  - auth.log       │
                    │  - wtmp/btmp      │
                    └─────────┬─────────┘
                              │
                    Periodic Extraction (every 30 min)
                              │
                    ┌─────────▼─────────┐
                    │  Host Machine     │
                    │  (External Storage)│
                    └─────────┬─────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
┌────────▼────────┐  ┌────────▼────────┐  ┌───────▼──────┐
│  SQLite         │  │ Analysis Tools  │  │ Automated    │
│  Database       │  │                 │  │ Maintenance  │
│                 │  │                 │  │              │
│ attacks.db      │  │ - behavioral_   │  │ - Daily      │
│                 │  │   analyzer      │  │   reset      │
│ - auth_attempts │  │ - ttp_analyzer  │  │ - Health     │
│ - commands      │  │ - cross_corr    │  │   checks     │
│ - sessions      │  │ - attack_logger │  │ - Backup     │
│ - fingerprints  │  │ - query_db      │  │   cleanup    │
└────────┬────────┘  └────────┬────────┘  └───────┬──────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Reports &       │
                    │   Exports         │
                    │                   │
                    │ - behavioral.json │
                    │ - ttp_report.json │
                    │ - cross_corr.json │
                    │ - backups/        │
                    └───────────────────┘
```

## Data Flow Sequence

```
1. Attack Initiation
   └─> Attacker connects via SSH to port 2225
   
2. Authentication
   └─> Real SSH daemon validates credentials
   └─> Success/Failure logged to wtmp/btmp
   
3. Session Start
   └─> User gets shell access
   └─> .bashrc loads command logger
   
4. Command Execution
   └─> User runs: cat /root/.aws/credentials
   └─> DEBUG trap captures command
   └─> Logged: timestamp|user|command
   
5. Output Display
   └─> Fake AWS credentials shown
   └─> Attacker sees "real" data
   
6. Periodic Extraction
   └─> Every 30 minutes: attack_logger.py runs
   └─> Parses /var/log/attacks/command_log
   └─> Inserts into SQLite database
   
7. Analysis
   └─> behavioral_analyzer.py detects bot
   └─> ttp_analyzer.py maps to MITRE ATT&CK
   └─> cross_correlation.py finds patterns
   
8. Auto-Maintenance
   └─> Daily at 3 AM: container resets
   └─> Backup created before reset
   └─> Fresh container deployed
   └─> Fake data re-injected
```

## Component Interaction

```
┌─────────────────────────────────────────────────────┐
│              Container Layer                        │
│                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │   SSH    │───>│  Fake    │───>│   Data   │     │
│  │  Daemon  │    │ Services │    │  Files   │     │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘     │
│       │               │               │            │
│       └───────────────┴───────────────┘            │
│                         │                          │
│                         v                          │
│              ┌──────────────────┐                  │
│              │  Command Logger  │                  │
│              │  (DEBUG trap)    │                  │
│              └────────┬─────────┘                  │
│                       │                            │
└───────────────────────┼────────────────────────────┘
                        │
                        v
┌─────────────────────────────────────────────────────┐
│              Host Layer                             │
│                                                     │
│              ┌──────────────────┐                  │
│              │ attack_logger.py │                  │
│              └────────┬─────────┘                  │
│                       │                            │
│                       v                            │
│              ┌──────────────────┐                  │
│              │  SQLite DB       │                  │
│              │  (attacks.db)    │                  │
│              └────────┬─────────┘                  │
│                       │                            │
│        ┌──────────────┼──────────────┐            │
│        │              │              │            │
│        v              v              v            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Behavioral│  │  TTP     │  │Cross-    │       │
│  │Analyzer  │  │Analyzer  │  │Correlation│      │
│  └──────────┘  └──────────┘  └──────────┘       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Security Boundaries

```
┌─────────────────────────────────────────┐
│         Untrusted Network               │
│         (Internet/Attackers)            │
└──────────────────┬──────────────────────┘
                   │ SSH (Port 2225)
                   │
         ┌─────────▼─────────┐
         │  Firewall Rules   │
         │  - Allow 2225     │
         │  - Log all        │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │  Docker Network   │
         │  (Isolated)       │
         │                   │
         │  ┌─────────────┐  │
         │  │  Honeypot   │  │
         │  │  Container  │  │
         │  │             │  │
         │  │ - Real SSH  │  │
         │  │ - Fake Data │  │
         │  │ - Logging   │  │
         │  └─────────────┘  │
         └─────────┬─────────┘
                   │
                   │ Logs extracted
                   │
         ┌─────────▼─────────┐
         │  Host Machine     │
         │  (Trusted)        │
         │                   │
         │ - SQLite DB       │
         │ - Analysis Tools  │
         │ - Backups         │
         └───────────────────┘
```

## Deployment Options

### Option 1: Local Testing
```
Your Laptop → Docker → Honeypot Container
(No internet exposure)
```

### Option 2: VPS Deployment
```
Internet → VPS Firewall → Docker → Honeypot Container
(Public IP, rate limiting)
```

### Option 3: Multi-Container
```
Internet → Load Balancer → Multiple Honeypot Containers
(Different configs, geographic diversity)
```

---

**🐝 See README.md for usage details!**
