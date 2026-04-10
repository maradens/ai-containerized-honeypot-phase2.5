# 📚 Documentation

## Table of Contents
- [Architecture Deep Dive](#architecture-deep-dive)
- [Component Details](#component-details)
- [Fake Services Reference](#fake-services-reference)
- [Analysis Tools Guide](#analysis-tools-guide)
- [Detection Algorithms](#detection-algorithms)
- [Troubleshooting](#troubleshooting)

---

## Architecture Deep Dive

### Container Isolation

The honeypot uses Docker containerization for:
- **Safety**: Real commands execute in isolated environment
- **Reset**: Easy recreation after compromise
- **Portability**: Works on any Docker-enabled system
- **Persistence**: Logs stored externally, survive container reset

### Data Flow

```
1. Attacker connects via SSH
2. Container authenticates (real SSH daemon)
3. User runs commands
4. DEBUG trap captures every command
5. Logs written to /var/log/attacks/
6. attack_logger.py extracts to SQLite
7. Analysis tools process data
8. Container auto-resets daily (with backup)
```

---

## Component Details

### attack_logger.py

**Purpose**: Extract container logs to external database

**Features**:
- Parse wtmp/btmp for auth attempts
- Extract command logs
- SQLite storage
- JSON export

**Usage**:
```bash
python attack_logger.py scan      # Extract logs
python attack_logger.py stats     # Show statistics
python attack_logger.py export    # Export to JSON
python attack_logger.py monitor   # Continuous monitoring
```

### behavioral_analyzer.py

**Purpose**: Differentiate bots from humans

**Algorithm**:
1. Analyze command timing (avg, std dev)
2. Check auth patterns (volume, usernames)
3. Calculate bot score (0-12)
4. Classify based on thresholds

**Scoring**:
- Volume: +1-3 points
- Username diversity: +1-3 points
- Fast timing: +1-3 points
- Consistency: +2 points
- Low success: +1 point

### ttp_analyzer.py

**Purpose**: Map attacks to MITRE ATT&CK

**Coverage**:
- Reconnaissance (T1592, T1590)
- Discovery (T1082, T1083)
- Credential Access (T1110, T1552)
- Collection (T1213, T1005)
- C2 (T1071)
- Persistence (T1053)
- Defense Evasion (T1070)
- Impact (T1490)

### cross_correlation_analyzer.py

**Purpose**: Long-term pattern detection

**Analysis**:
- IP return frequency
- Username list comparison
- Time-of-day patterns
- Persistent attacker identification

---

## Fake Services Reference

### MySQL (Interactive)

**Commands**:
```sql
show tables;
show databases;
SELECT * FROM users;
SELECT * FROM api_keys;
SELECT * FROM credentials;
use production_db;
```

**Tables**:
- `users` - Fake user credentials
- `api_keys` - Stripe, AWS, GitHub keys
- `credentials` - Database passwords
- `admin_sessions` - Session data

### Redis (Interactive)

**Commands**:
```redis
GET password
GET admin
GET secret
INFO
KEYS *
CONFIG GET requirepass
DUMP keyname
```

**Keys**:
- `password` - Super secret password
- `admin` - Admin credentials
- `secret` - Very secret data
- `session` - Session tokens

### PostgreSQL (Interactive)

**Commands**:
```sql
\l              -- List databases
\dt             -- List tables
\dn             -- List schemas
SELECT * FROM users;
SELECT * FROM credentials;
SELECT * FROM api_keys;
```

**Tables**:
- `users` - User accounts with passwords
- `credentials` - Service credentials
- `api_keys` - API keys and secrets
- `sessions` - Active sessions

---

## Analysis Tools Guide

### Behavioral Analysis

**When to run**: After collecting command data

**Interpretation**:
```
Bot likelihood: YES
- Fast timing (<2s between commands)
- Consistent intervals (low std dev)
- High volume (50+ attempts)
- Many usernames (10+)

Human likelihood: YES
- Variable timing (2-60s)
- Strategic progression
- Reads output, adapts
- Makes mistakes (typos)
```

### TTP Analysis

**When to run**: Periodically or after attacks

**Output**:
- MITRE ATT&CK technique IDs
- Tactic categorization
- Attack examples
- Instance counts

**Use case**: Threat intelligence, SOC integration

### Cross-Correlation

**When to run**: Weekly/monthly analysis

**Detects**:
- Persistent attackers (return regularly)
- Same bot from different IPs
- Scheduled attacks (time patterns)
- Botnet coordination

---

## Detection Algorithms

### Bot Classification Thresholds

| Score | Classification | Action |
|-------|----|-------|
| 8-12 | DEFINITELY_BOT | Block IP, alert |
| 6-7 | LIKELY_BOT | Monitor closely |
| 4-5 | POSSIBLY_BOT | Flag for review |
| 0-3 | LIKELY_HUMAN | Normal monitoring |

### Time Pattern Detection

**Algorithm**:
1. Group attempts by hour
2. Calculate peak hour concentration
3. If >60% in one hour → scheduled bot

**Example**:
```
03:00 - 85% of attempts
→ Scheduled task (cron job)
→ Bot running at fixed time
```

### Username Set Comparison

**Algorithm**:
1. Collect unique usernames per IP
2. Sort and hash username sets
3. Find identical sets
4. Same set = same bot/script

**Example**:
```
IP A: [root, admin, user, test, ...]
IP B: [root, admin, user, test, ...]
→ Same 50-username list
→ Same bot, different infrastructure
```

---

## Troubleshooting

### Container Won't Start

**Symptom**: `docker ps` shows no container

**Solution**:
```bash
# Check Docker is running
sudo systemctl status docker

# Rebuild image
docker build -t honeypot-ubuntu:latest .

# Deploy
python container_manager.py deploy 2225
```

### Logs Not Capturing

**Symptom**: Command log empty

**Solution**:
```bash
# Check logger installed
docker exec honeypot-manual-test cat /root/.bashrc | grep -A 3 "Command Logger"

# Reinstall
docker exec honeypot-manual-test bash /root/.bash_command_logger

# Reconnect SSH for changes to take effect
```

### Analysis Tools Fail

**Symptom**: `ModuleNotFoundError`

**Solution**:
```bash
# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.10+
```

### Auto-Reset Not Working

**Symptom**: Container not resetting daily

**Solution**:
```bash
# Check cron
crontab -l | grep honeypot

# Reschedule
python container_manager.py schedule

# Test manually
python container_manager.py reset --keep-logs
```

---

## Performance Tuning

### Reduce False Positives

Adjust thresholds in `behavioral_analyzer.py`:
```python
# Increase volume threshold
if attempts > 100:  # Was 50
    score += 3

# Relax timing requirement
if avg_delta < 5:  # Was 2
    score += 3
```

### Increase Detection Sensitivity

Lower thresholds for earlier detection:
```python
# Lower volume threshold
if attempts > 20:  # Was 50
    score += 2

# Lower timing threshold
if avg_delta < 3:  # Was 2
    score += 2
```

---

## Security Hardening

### For Production Deployment

1. **Isolate network**:
```bash
docker network create honeypot-net
# Run container on isolated network
```

2. **Resource limits**:
```bash
docker run --memory="1g" --cpus="1" ...
```

3. **Read-only filesystem**:
```bash
docker run --read-only --tmpfs /tmp ...
```

4. **Drop capabilities**:
```bash
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE ...
```

---

**🐝 For more help, check GitHub Issues!**
