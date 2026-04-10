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
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Components](#components)
- [Usage Guide](#usage-guide)
- [Analysis Tools](#analysis-tools)
- [Detection Capabilities](#detection-capabilities)
- [Security & Legal](#security--legal)
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

### 📈 **External Data Persistence**
- **SQLite Database** - All attack data stored externally
- **Command Logging** - Captures every command executed
- **Auth Tracking** - Login attempts with timestamps
- **Export Capabilities** - JSON export for analysis

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ATTACKER INTERNET                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ SSH (Port 2225)
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Docker Container (honeypot-ubuntu)             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Real SSH Daemon (sshd)                              │  │
│  │  - Password authentication enabled                   │  │
│  │  - Multiple fake user accounts                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Interactive Fake Services                           │  │
│  │  ├── mysql      → Fake MySQL with user data          │  │
│  │  ├── redis-cli  → Fake Redis with passwords          │  │
│  │  ├── psql       → Fake PostgreSQL with credentials   │  │
│  │  ├── netstat    → Shows fake services (3306, 6379..) │  │
│  │  └── ps aux     → Shows fake processes               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Fake Data Files                                     │  │
│  │  ├── /root/.aws/credentials  (AWS keys)             │  │
│  │  ├── /root/.ssh/id_rsa       (SSH keys)             │  │
│  │  ├── /root/.git-credentials  (Git tokens)           │  │
│  │  ├── /root/.kube/config      (K8s secrets)          │  │
│  │  ├── /backup/*.sql           (Database dumps)       │  │
│  │  ├── /home/deploy/           (Docker/K8s configs)   │  │
│  │  └── /etc/nginx/             (Web configs)          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Command Logger (DEBUG trap)                         │  │
│  │  - Logs every command to /var/log/attacks/           │  │
│  │  - Timestamps, usernames, full commands              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Logs extracted periodically
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Host Machine (External Storage)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SQLite Database (attacks.db)                        │  │
│  │  ├── auth_attempts   (login attempts)                │  │
│  │  ├── commands        (executed commands)             │  │
│  │  ├── sessions        (connection sessions)           │  │
│  │  └── fingerprints    (SSH fingerprints)              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Analysis Tools                                      │  │
│  │  ├── behavioral_analyzer.py   (Bot vs Human)         │  │
│  │  ├── ttp_analyzer.py          (MITRE ATT&CK)         │  │
│  │  ├── cross_correlation.py     (Long-term patterns)   │  │
│  │  ├── container_manager.py     (Auto management)      │  │
│  │  └── attack_logger.py         (Data extraction)      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Automated Maintenance (Cron)                        │  │
│  │  ├── Daily reset at 3 AM (with backup)               │  │
│  │  ├── Health check every 6 hours                      │  │
│  │  ├── Attack scan every 30 minutes                    │  │
│  │  └── Backup cleanup at 4 AM (30 days retention)      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
Attacker → SSH Connection → Container
                           ↓
                    Command Execution
                           ↓
                   DEBUG Trap Logs
                           ↓
              /var/log/attacks/command_log
                           ↓
            Periodic Scan (every 30 min)
                           ↓
                    attack_logger.py
                           ↓
              External SQLite Database
                           ↓
          ┌───────┬───────┬───────┬───────┐
          ↓       ↓       ↓       ↓       ↓
    behavioral  ttp    cross-  container  export
    analyzer   analyzer correlation manager
```

---

## 💻 System Requirements

### Hardware
- **CPU**: 2+ cores
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 10GB free space
- **Network**: Internet connection (optional for threat intel)

### Software
- **Docker** 20.10+ (with rootless or sudo access)
- **Python** 3.10+
- **Linux** (Ubuntu 22.04+, Debian 11+, CentOS 8+)

### Optional
- **Git** (for version control)
- **SQLite** browser (for database inspection)

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/maradens/ai-containerized-honeypot-phase2.5.git
cd ai-containerized-honeypot-phase2.5
```

### 2. Build Docker Image

```bash
docker build -t honeypot-ubuntu:latest .
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Deploy Container

```bash
python container_manager.py deploy 2225
```

### 5. Access Honeypot

```bash
ssh root@localhost -p 2225
# Password: password123
```

### 6. Start Automated Maintenance

```bash
python container_manager.py schedule
```

### 7. Test It!

```bash
# From another terminal
python test_bot.py 30  # Run test bot for 30 seconds

# Check logs
python attack_logger.py scan

# Analyze behavior
python behavioral_analyzer.py

# Check TTPs
python ttp_analyzer.py
```

---

## 📦 Components

### Core Files

| File | Description |
|------|-------------|
| `Dockerfile` | Ubuntu 22.04 base with SSH pre-configured |
| `honeypot_manager.py` | Container lifecycle management |
| `attack_logger.py` | Extract logs from container to SQLite |
| `container_manager.py` | Auto reset, deploy, backup system |

### Analysis Tools

| Tool | Purpose |
|------|---------|
| `behavioral_analyzer.py` | Bot vs Human detection |
| `ttp_analyzer.py` | MITRE ATT&CK TTP mapping |
| `cross_correlation_analyzer.py` | Long-term pattern analysis |
| `temporal_analyzer.py` | Time-based attack patterns |

### Fake Data Injection

| Script | Purpose |
|--------|---------|
| `fake_data_injector.py` | AWS creds, SSH keys, Git tokens |
| `fake_files_enhanced.py` | Database dumps, deployment scripts |
| `copy_interactive_services.py` | MySQL, Redis, PostgreSQL fakes |
| `inject_fake_services.py` | Network services simulation |

### Test & Validation

| Script | Purpose |
|--------|---------|
| `test_bot.py` | Simulate automated attack |
| `test_ssh_bot.py` | SSH-based bot simulation |
| `manual_test.py` | Manual container testing |
| `query_db.py` | Database query interface |

---

## 📚 Usage Guide

### Interacting with Fake Services

```bash
# MySQL
mysql
show tables;
SELECT * FROM users;
SELECT * FROM api_keys;
exit;

# Redis
redis-cli
GET password
INFO
KEYS *
exit;

# PostgreSQL
psql
\dt
SELECT * FROM credentials;
\q
```

### Viewing Fake Files

```bash
# AWS credentials
cat /root/.aws/credentials

# SSH keys
cat /root/.ssh/id_rsa

# Git tokens
cat /root/.git-credentials

# Database dumps
cat /backup/users_backup.sql
cat /backup/api_keys_backup.sql

# K8s secrets
cat /home/deploy/k8s/deployment.yaml

# Nginx config
cat /etc/nginx/nginx.conf
cat /etc/nginx/.htpasswd
```

### Checking Fake Services

```bash
# Network services
netstat -tulpn

# Running processes
ps aux

# Cron jobs
cat /etc/crontab
```

---

## 🔬 Analysis Tools

### 1. Behavioral Analysis (Bot vs Human)

```bash
python behavioral_analyzer.py
```

**Output:**
```
🤖 BEHAVIORAL ANALYSIS REPORT

⏱️ COMMAND TIMING:
   Average: 4.30s between commands
   Bot likelihood: ❌ NO (variable timing = human)

🔐 AUTH PATTERNS:
   IP: 172.17.0.1
   Attempts: 317
   Classification: LIKELY_BOT (high volume, fast timing)

📊 COMMAND DIVERSITY:
   Total unique: 18
   Human likelihood: ✅ YES (strategic progression)
```

### 2. TTP Mapping (MITRE ATT&CK)

```bash
python ttp_analyzer.py
```

**Output:**
```
📊 MITRE ATT&CK TTP REPORT

📁 Credential Access
  🔹 T1110: Brute Force
     Count: 1 source
     Source: 172.17.0.1 (317 attempts)

📁 Discovery
  🔹 T1083: File and Directory Discovery
     Count: 1 instance
     Example: ls -la /root

📁 Reconnaissance
  🔹 T1592: Gather Victim Host Information
     Count: 2 instances
     Example: cat /etc/hosts
```

### 3. Cross-Correlation (Long-term)

```bash
python cross_correlation_analyzer.py
```

**Output:**
```
🔗 CROSS-CORRELATION ANALYSIS

📅 IP RETURN PATTERNS:
   IP: 185.220.101.1
   Active days: 30
   Returns every: 1.0 days (REGULAR)
   Pattern: Daily scanner (BOTNET)

🕐 TIME-OF-DAY PATTERNS:
   IP: 103.75.201.5
   Peak hour: 03:00 (85% of attacks)
   Pattern: Scheduled bot

🔗 SAME USERNAME LIST:
   IPs: 185.220.101.1, 103.75.201.5
   Same 50-username list → Same bot script
```

### 4. Query Database Directly

```bash
# Recent attempts
python query_db.py --recent

# Stats by username
python query_db.py --users

# Failed attempts
python query_db.py --failed

# Custom query
python query_db.py --custom "SELECT * FROM auth_attempts LIMIT 10"
```

---

## 🎯 Detection Capabilities

### Bot Detection Scoring

| Score | Classification | Characteristics |
|-------|--------------|----------------|
| 8-12 | **DEFINITELY_BOT** | High volume, many usernames, fast timing |
| 6-7 | **LIKELY_BOT** | Moderate bot indicators |
| 4-5 | **POSSIBLY_BOT** | Some bot-like patterns |
| 0-3 | **LIKELY_HUMAN** | Variable timing, strategic behavior |

### Scoring Criteria

- **Volume**: +1 to +3 (10-50+ attempts)
- **Username Diversity**: +1 to +3 (5-10+ unique)
- **Fast Timing**: +1 to +3 (<1-10 seconds)
- **Consistency**: +2 (low variance)
- **Low Success**: +1 (<10% success rate)

### MITRE ATT&CK Coverage

| Tactic | Techniques Covered |
|--------|-------------------|
| **Reconnaissance** | T1592, T1590, T1595 |
| **Discovery** | T1082, T1083, T1016 |
| **Credential Access** | T1110, T1552, T1528 |
| **Collection** | T1213, T1005 |
| **Command & Control** | T1071 |
| **Persistence** | T1053 |
| **Defense Evasion** | T1070 |
| **Impact** | T1490 |

---

## 🔒 Security & Legal

### ⚠️ Legal Disclaimer

This honeypot is designed for **defensive security research** only. By using this software, you agree to:

1. **Comply with local laws** regarding honeypot deployment
2. **Not use for offensive purposes** or unauthorized access
3. **Obtain proper authorization** before deploying on networks
4. **Respect privacy laws** when collecting attack data
5. **Use responsibly** for research, education, or defense

### Security Best Practices

- **Isolate honeypot** from production networks
- **Use separate VPS** for public deployment
- **Monitor regularly** for unexpected activity
- **Keep logs secure** and encrypted
- **Legal review** before public exposure
- **Rate limiting** to prevent abuse

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For issues, questions, or contributions:

- **GitHub Issues**: https://github.com/maradens/ai-containerized-honeypot-phase2.5/issues
- **Documentation**: See [DOCS.md](DOCS.md) for detailed guides

---

## 🙏 Acknowledgments

- MITRE ATT&CK Framework for threat modeling
- Docker community for containerization
- Security research community for honeypot techniques

---

**🐝 Built with care for security researchers and defenders!**
