# 🐝 AI-Driven Containerized Honeypot - Phase 2.5

## Advanced SSH Honeypot with Behavioral Analysis & Automated Management

A production-ready, containerized SSH honeypot with interactive fake services, automated container management, behavioral analysis for bot/human differentiation, MITRE ATT&CK TTP mapping, and long-term cross-correlation analysis.

![Phase](https://img.shields.io/badge/Phase-2.5-green.svg)
![Docker](https://img.shields.io/badge/Docker-Latest-blue.svg)
![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Deploy](#quick-deploy)
- [User Accounts](#user-accounts)
- [Components](#components)
- [Usage Guide](#usage-guide)
- [Monitoring](#monitoring)
- [Health Check](#health-check)
- [Analysis Tools](#analysis-tools)
- [Detection Capabilities](#detection-capabilities)
- [Security & Legal](#security--legal)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### 🎭 **Interactive Fake Services**
- **MySQL Server** - Fake database with user credentials, API keys, secrets
- **Redis Client** - Fake cache with passwords and session data
- **PostgreSQL** - Fake database with credentials and sensitive tables
- **Network Services** - Simulated MySQL, Redis, PostgreSQL, MongoDB, Nginx

### 📁 **Comprehensive Fake Data**
- AWS credentials (3 profiles: default, production, staging)
- SSH keys for multiple users
- Git credentials (GitHub, GitLab tokens)
- Kubernetes configurations with secrets
- Database dumps (users, API keys, credentials)
- Docker Compose & deployment scripts
- Nginx configs with backend servers
- Fake admin panels and API endpoints

### 👥 **8 Pre-Configured User Accounts**
- **root/password123** - Superuser access
- **ubuntu/ubuntu** - Common Ubuntu default
- **admin/password** - Generic admin account
- **developer/Dev@123456** - Developer with fake projects
- **webmaster** (locked) - Service account for reconnaissance
- **backup** (locked) - Service account for reconnaissance
- **deploy** (locked) - CI/CD account for reconnaissance

### 🤖 **Bot vs Human Detection**
- **Behavioral Analysis** - Command timing, auth patterns, diversity analysis
- **Classification System** - Quantifies bot likelihood (0-12 score)
- **Real-time Detection** - Identifies automated vs manual attacks

### 🔗 **MITRE ATT&CK TTP Mapping**
- **TTP Detection** - Correlates attacks with MITRE ATT&CK framework
- **Pattern Recognition** - Identifies reconnaissance, credential access, collection
- **Threat Intelligence** - Export data for security research

### 📊 **Cross-Correlation Analysis**
- **Persistent Attacker Tracking** - Detects IPs that return regularly
- **Username Pattern Analysis** - Identifies same bot from different IPs
- **Time-of-Day Patterns** - Finds scheduled attacks
- **Long-term Monitoring** - Weeks/months of attack correlation

### 🔄 **Automated Container Management**
- **Daily Reset** - Automatic container reset at 3 AM
- **Health Monitoring** - Checks every 6 hours
- **Attack Scanning** - Logs attacks every 30 minutes
- **Backup System** - Preserves attack data before reset
- **Auto Cleanup** - Removes old backups (30 days retention)

### 🏥 **One-Command Health Check & Restore**
- **Check Status** - Verify honeypot is healthy
- **Full Restore** - Rebuild from scratch in 2-3 minutes
- **Database Backup** - Automatic backup before restore
- **Data Preservation** - Attack logs survive container reset

---

## 🏗️ Architecture

### System Overview

```
┌───────────────────────────────────────────┐
│          ATTACKER INTERNET                │
└──────────────┬────────────────────────────┘
               │ SSH (Port 22)
               │
┌──────────────▼────────────────────────────┐
│    Docker Container (honeypot-ubuntu)     │
│  ┌────────────────────────────────────┐   │
│  │  Real SSH Daemon (sshd)            │   │
│  │  - 8 user accounts                 │   │
│  │  - Password authentication         │   │
│  └────────────────────────────────────┘   │
│  ┌────────────────────────────────────┐   │
│  │  Interactive Fake Services         │   │
│  │  - mysql, redis-cli, psql          │   │
│  │  - netstat, ps (realistic output)  │   │
│  └────────────────────────────────────┘   │
│  ┌────────────────────────────────────┐   │
│  │  Fake Data Files                   │   │
│  │  - AWS, SSH, Git, K8s credentials  │   │
│  │  - Database dumps, configs         │   │
│  └────────────────────────────────────┘   │
└──────────────┬────────────────────────────┘
               │ Logs extracted periodically
               │
┌──────────────▼────────────────────────────┐
│    Host Machine (External Storage)        │
│  ┌────────────────────────────────────┐   │
│  │  SQLite Database (attacks.db)      │   │
│  │  - auth_attempts, commands         │   │
│  │  - sessions, fingerprints          │   │
│  └────────────────────────────────────┘   │
│  ┌────────────────────────────────────┐   │
│  │  Analysis Tools                    │   │
│  │  - behavioral_analyzer.py          │   │
│  │  - ttp_analyzer.py                 │   │
│  │  - cross_correlation_analyzer.py   │   │
│  └────────────────────────────────────┘   │
│  ┌────────────────────────────────────┐   │
│  │  Health Check Scripts              │   │
│  │  - health_check.sh (check/restore) │   │
│  │  - add_accounts.sh (add users)     │   │
│  └────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

---

## 🚀 Quick Deploy

### 1. Clone & Setup
```bash
git clone https://github.com/maradens/ai-containerized-honeypot-phase2.5.git
cd ai-containerized-honeypot-phase2.5
```

### 2. Build & Deploy
```bash
docker build -t honeypot-ubuntu:latest .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python container_manager.py deploy 22
```

### 3. Inject Data & Users
```bash
python fake_data_injector.py
python inject_fake_services.py
./add_accounts.sh
```

### 4. Verify & Start
```bash
./health_check.sh check
python attack_logger.py scan
```

**See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for complete deployment guide.**

---

## 👥 User Accounts

The honeypot includes **8 pre-configured accounts** for attackers:

| Username | Password | Type |
|---------|-----|------|
| root | password123 | Superuser |
| ubuntu | ubuntu | Common default |
| admin | password | Generic admin |
| developer | Dev@123456 | Developer |
| webmaster | (locked) | Recon only |
| backup | (locked) | Recon only |
| deploy | (locked) | Recon only |

**All accounts have access to the same fake data and services!**

---

## 📦 Components

### Core Scripts

| Script | Purpose |
|--------|-------|
| `honeypot_manager.py` | Container lifecycle management |
| `attack_logger.py` | Extract logs to SQLite database |
| `container_manager.py` | Auto reset, deploy, backup system |
| `query_db.py` | Database query interface |

### Analysis Tools

| Tool | Purpose | Output |
|------|-----|-----|
| `behavioral_analyzer.py` | Bot vs Human detection | Classification score |
| `ttp_analyzer.py` | MITRE ATT&CK mapping | TTP report + JSON |
| `cross_correlation_analyzer.py` | Long-term patterns | Correlation report |
| `temporal_analyzer.py` | Time-based analysis | Timing patterns |

### Fake Data Injection

| Script | Purpose |
|--------|-----|
| `fake_data_injector.py` | AWS creds, SSH keys, Git tokens |
| `fake_files_enhanced.py` | Database dumps, configs |
| `inject_fake_services.py` | Fake mysql, netstat, ps |
| `continue_fake_files.py` | Additional enhanced files |

### Health Check & Utilities

| Script | Purpose |
|--------|-----|
| `health_check.sh` | Check status, restore honeypot |
| `add_accounts.sh` | Add ubuntu/admin users |
| `verify_setup.sh` | Verify installation |

---

## 📊 Monitoring

### Manual Only (No Automation)

```bash
# Daily check
python attack_logger.py stats

# Scan for new data
python attack_logger.py scan

# Behavioral analysis
python behavioral_analyzer.py

# MITRE ATT&CK mapping
python ttp_analyzer.py

# Long-term patterns
python cross_correlation_analyzer.py
```

### Health Check Commands

```bash
# Quick status
./health_check.sh status

# Full health check
./health_check.sh check

# Restore if compromised
./health_check.sh restore
```

---

## 🎯 Detection Capabilities

### Bot Detection Scoring

| Score | Classification | Action |
|-------|----|------|
| 8-12 | **DEFINITELY_BOT** | Block IP, alert |
| 6-7 | **LIKELY_BOT** | Monitor closely |
| 4-5 | **POSSIBLY_BOT** | Flag for review |
| 0-3 | **LIKELY_HUMAN** | Normal monitoring |

### MITRE ATT&CK Coverage

| Tactic | Techniques |
|--------|------|
| Reconnaissance | T1592, T1590, T1595 |
| Discovery | T1082, T1083, T1016 |
| Credential Access | T1110, T1552, T1528 |
| Collection | T1213, T1005 |
| Command & Control | T1071 |
| Persistence | T1053 |
| Defense Evasion | T1070 |
| Impact | T1490 |

---

## 🔒 Security & Legal

### Before Deployment

- ✅ **Legal Review** - Ensure compliance with local laws
- ✅ **Isolation** - Keep separate from production
- ✅ **Rate Limiting** - Prevent DDoS abuse
- ✅ **Logging** - Enable comprehensive logging
- ✅ **Backup** - Test backup system

### During Operation

- Monitor daily
- Review alerts regularly
- Update detection rules
- Export data weekly
- Rotate backups monthly

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|-----|
| "Fake" text in output | See DEPLOYMENT_ISSUES.md Issue #16 |
| Container not running | `./health_check.sh restore` |
| Port 22 in use | Change admin SSH to 64222 |
| Missing fake data | Re-run injection scripts |
| Database corrupted | `./health_check.sh restore` |

See [DEPLOYMENT_ISSUES.md](DEPLOYMENT_ISSUES.md) for 16 documented issues and fixes.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test thoroughly
4. Submit pull request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

**🐝 Ready to catch attackers!**

**Version**: Phase 2.5 | **Last Updated**: April 17, 2026
