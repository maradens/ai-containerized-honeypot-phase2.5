# 🐝 AI-Driven Containerized Honeypot - Phase 2.5

## ✅ **Status: Production Ready** (May 1, 2026)

| Item | Status |
|------|--------|
| **Phase 1:** Host Deployment (localhost:2225) | ✅ Complete & Tested |
| **All Bugs Fixed** | ✅ 16 issues resolved |
| **Documentation** | ✅ Updated & Complete |
| **Fake Services** | ✅ Realistic (no "Fake" text) |
| **Deployability** | ✅ README gives complete instructions |

**Latest:** All critical bugs fixed, tested, and documented. See [docs/FIXES_LOG.md](docs/FIXES_LOG.md) for details.

---

Advanced SSH honeypot with behavioral analysis, MITRE ATT&CK mapping, automated management & comprehensive fake data injection.

![Phase](https://img.shields.io/badge/Phase-2.5-green.svg)
![Docker](https://img.shields.io/badge/Docker-Latest-blue.svg)
![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📁 Repository Structure

## 📁 Repository Structure

```
ai-containerized-honeypot-phase2.5/
├── README.md                          # 📖 You are here
├── QUICKSTART.md                      # ⚡ 5-minute quick start guide
├── requirements.txt                   # 📦 Python dependencies
├── .env.example                       # ⚙️ Configuration template
├── Dockerfile                         # 🐳 Container definition
│
├── deploy/                            # 🚀 Deployment scripts
│   ├── container_manager.py           # Container orchestration
│   ├── add_accounts.sh                # User account injection
│   ├── health_check.sh                # System health verification
│   └── verify_setup.sh                # Deployment validation
│
├── inject/                            # 📦 Data & service injection
│   ├── fake_data_injector.py          # AWS, SSH keys, Git tokens
│   ├── inject_fake_services.py        # Interactive fake services
│   ├── copy_interactive_services.py   # Interactive shells
│   ├── monitor_inject.py              # System monitoring
│   ├── setup_logger.py                # Attack logger setup
│   └── ... (3 more)
│
├── monitor/                           # 📊 Attack monitoring
│   ├── attack_logger.py               # Scan & log to SQLite
│   └── query_db.py                    # Database queries
│
├── analyze/                           # 🔬 Analysis scripts
│   ├── behavioral_analyzer.py         # Bot vs Human detection
│   ├── ttp_analyzer.py               # MITRE ATT&CK mapping
│   ├── cross_correlation_analyzer.py # Long-term patterns
│   ├── temporal_analyzer.py          # Time-based analysis
│   └── exports/                      # Generated reports
│
├── config/                            # ⚙️ Configuration
│   ├── honeypot_config.py            # Config loader
│   └── honeypot_manager.py           # High-level manager
│
├── docs/                              # 📚 Documentation
│   ├── ARCHITECTURE.md               # Technical architecture
│   ├── DEPLOYMENT_GUIDE.md           # Complete deployment steps
│   ├── ATTACK_ANALYSIS.md            # Analysis results
│   ├── MONITORING_GUIDE.md           # Monitoring workflow
│   ├── FIXES_LOG.md                  # Changelog
│   ├── DEPLOYMENT_CHECKLIST.md       # Pre-deployment checklist
│   └── ... (4 more)
│
└── scripts/                           # 🛠️ Utilities & maintenance
    └── ... (7 maintenance scripts)
```

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

**⚠️ IMPORTANT:** This honeypot has been tested and all bugs fixed (see [docs/FIXES_LOG.md](docs/FIXES_LOG.md)). Follow these steps exactly for a flawless deployment.

### Option A: Local Testing (Recommended First - 5 minutes)

Test on your host machine before deploying to production VM:

```bash
# 1. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install docker python-dotenv

# 2. Build Docker image
docker build -t honeypot-ubuntu:latest .

# 3. Deploy container (port 2225)
python container_manager.py deploy 2225

# 4. Inject fake data
python fake_data_injector.py
python inject_fake_services.py
python copy_interactive_services.py

# 5. Test it!
ssh root@localhost -p 2225  # Password: password123
```

### Option B: Production Deployment (Port 22)

**Prerequisites:**
- ⚠️ Change admin SSH from port 22 to 64222 first!
- ⚠️ Ensure you can still access admin account

```bash
# 1. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install docker python-dotenv

# 2. Build Docker image
docker build -t honeypot-ubuntu:latest .

# 3. Configure (optional - use defaults)
cp .env.example .env  # Edit if needed

# 4. Deploy container (port 22 - replaces SSH)
python container_manager.py deploy 22

# 5. Inject fake data
python fake_data_injector.py
python inject_fake_services.py
python copy_interactive_services.py

# 6. Test it!
ssh root@localhost -p 22  # Password: password123
```

### 🔧 Optional Configuration

```bash
# Copy config template
cp .env.example .env

# Edit as needed (optional)
nano .env

# Default values:
# CONTAINER_NAME=honeypot-manual-test
# SSH_PORT=2225
# SSH_USER=root
# SSH_PASSWORD=password123
```

### ✅ Verify Deployment

**Quick Tests:**
```bash
# Test SSH access
ssh root@localhost -p 2225
# Password: password123

# Inside SSH, verify fake services (should NOT show "Fake" text!)
mysql --version
# Expected: mysql Ver 8.0.36-0ubuntu0.20.04.1 for Linux (x86_64) using EditLine wrapper

netstat -tulpn
# Expected: Shows services on ports 22, 80, 443, 3306, 6379, 5432, 27017

cat /root/.aws/credentials
# Expected: Shows 3 profiles (default, production, staging)

ps aux
# Expected: Shows sshd, mysqld, nginx, redis-server
```

**Full Verification:**
```bash
./health_check.sh check  # Comprehensive status check
```

**See:**
- [docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md) - Complete deployment steps
- [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - Latest deployment information
- [docs/DEPLOYMENT_ISSUES.md](docs/DEPLOYMENT_ISSUES.md) - Troubleshooting 16 common issues
- [docs/FIXES_LOG.md](docs/FIXES_LOG.md) - All bugs fixed in this session
- [docs/MONITORING_GUIDE.md](docs/MONITORING_GUIDE.md) - Attack logging & behavioral analysis

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
| "Fake" text in output | See docs/DEPLOYMENT_ISSUES.md Issue #16 |
| Container not running | `./health_check.sh restore` |
| Port 22 in use | Change admin SSH to 64222 |
| Missing fake data | Re-run injection scripts |
| Database corrupted | `./health_check.sh restore` |

See [docs/DEPLOYMENT_ISSUES.md](docs/DEPLOYMENT_ISSUES.md) for 16 documented issues and fixes.

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
