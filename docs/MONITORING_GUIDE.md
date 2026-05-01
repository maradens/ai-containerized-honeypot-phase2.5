# 🔍 Monitoring & Attack Logging Guide

**Last Updated:** May 1, 2026  
**Status:** ✅ Working & Tested

---

## 📊 Monitoring Systems Overview

This honeypot uses **4 layers of monitoring**:

```
┌─────────────────────────────────────────────────┐
│  Layer 1: System Logs (auth.log, bash_history)  │
│  Layer 2: Attack Logger (SQLite database)       │
│  Layer 3: Audit Tracking (auditd)               │
│  Layer 4: Behavioral Analysis (bot detection)   │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Step 1: Enable Monitoring

After deploying the container, run:

```bash
# Inject monitoring system
cd ~/github-repos/ai-containerized-honeypot-phase2.5
source venv/bin/activate
python monitor_inject.py
```

**What this does:**
- ✅ Creates `/var/log/attacks/` directory
- ✅ Enables bash history logging
- ✅ Installs auditd for system call monitoring
- ✅ Configures audit rules for sensitive files
- ✅ Creates monitoring status script

---

## 🔍 Step 2: Setup Logger

```bash
# Setup external logger (runs outside container)
python setup_logger.py

# Logger connects to container & prepares for attack logging
```

---

## 📈 Step 3: Monitor Activity

### Option A: Quick Status Check

```bash
# From SSH session inside container
./monitor_status.sh

# Shows:
# - Latest commands executed
# - Recent file accesses
# - Latest auth attempts
```

### Option B: Attack Logger (Comprehensive)

```bash
# Scan for new attacks
python attack_logger.py scan

# Shows:
# - Successful login attempts
# - Failed login attempts  
# - Commands executed
# - Source IP tracking
# - Database statistics
```

**Example Output:**
```
=========================
📊 ATTACK STATISTICS
=========================

Total attempts: 9

By result:
  FAILED: 3
  SUCCESS: 6

Top targeted usernames:
  root | Attempts: 9 | Failed: 3 | Success: 6

Top source IPs:
  172.17.0.1 | Attempts: 9
```

### Option C: Database Query

```bash
# Interactively query the attack database
python query_db.py

# Commands:
#   stats             - Show statistics
#   users             - List targeted usernames
#   ips               - List source IPs
#   timeline          - Show attack timeline
#   export            - Export data to JSON
```

---

## 🤖 Step 4: Behavioral Analysis

After collecting some data, run analysis:

```bash
# Bot vs Human detection
python behavioral_analyzer.py

# MITRE ATT&CK mapping
python ttp_analyzer.py

# Long-term patterns
python cross_correlation_analyzer.py

# Time-based analysis
python temporal_analyzer.py
```

**Example Behavioral Analysis:**
```
=========================
🤖 BEHAVIORAL ANALYSIS
=========================

Bot Score: 8/12
Classification: DEFINITELY_BOT

Indicators:
  ✓ Fast command execution (<1s)
  ✓ Low command diversity
  ✓ Auth pattern: dictionary attack
  ✓ Source IP: known scammer
```

---

## 📁 Log Locations

### Inside Container:
```
var/log/auth.log          # Authentication logs
var/log/attacks/          # Attack-specific logs
  command_log             # Commands executed by attackers
  bash_history            # Shell history
  file_access.log        # Sensitive file access (auditd)
  commands.log            # All bash commands with timestamps
```

### On Host (External Logger):
```
/home/maradens/.openclaw/workspace/ai-honeypot-phase1/data/attacks.db
  # SQLite database with:
  # - auth_attempts table (login attempts)
  # - commands table (executed commands)
  # - file_access table (sensitive file access)
```

---

## 🔄 Automated Monitoring

### Option 1: Manual (Recommended)

**Daily:**
```bash
# Check attacks
python attack_logger.py scan

# Behavioral analysis (weekly)
python behavioral_analyzer.py

# Export data
python query_db.py export
```

**Weekly:**
```bash
# Long-term correlation
python cross_correlation_analyzer.py

# Full health check
./health_check.sh check
```

### Option 2: Cron Jobs (Optional)

**⚠️ IMPORTANT:** Documentation says NO automation initially. But here's how:

```bash
# Add to crontab
crontab -e

# Daily attack scan at 3 AM
0 3 * * * cd /github-repos/ai-containerized-honeypot-phase2.5 && \
  source venv/bin/activate && python attack_logger.py scan >> /var/log/honeypot-scan.log 2>&1

# Weekly behavioral analysis every Monday
0 3 * * 1 cd /github-repos/ai-containerized-honeypot-phase2.5 && \
  source venv/bin/activate && python behavioral_analyzer.py >> /var/log/honeypot-analysis.log 2>&1
```

---

## 🐛 Troubleshooting

### No Data Showing Up?

```bash
# Check if monitoring is injected
docker exec honeypot-manual-test ls -la /var/log/attacks/

# Should show: bash_history, command_log, etc.

# Re-inject if needed:
python monitor_inject.py
python setup_logger.py
```

### Database Errors?

```bash
# Check database path
echo /home/maradens/.openclaw/workspace/ai-honeypot-phase1/data/attacks.db

# Create directory if missing
mkdir -p /home/maradens/.openclaw/workspace/ai-honeypot-phase1/data/

# Recreate logger
python setup_logger.py
```

### SSH Keys Missing (Health Check)?

```bash
# Re-run fake data injector
python fake_data_injector.py

# Verify injection:
docker exec honeypot-manual-test ls -la /root/.ssh/
```

### Users Missing (Health Check)?

```bash
# Add missing user accounts
./add_accounts.sh

# Verify:
docker exec honeypot-manual-test cat /etc/passwd | grep -E "(ubuntu|admin|developer)"
```

---

## 📊 Complete Monitoring Workflow

```
Day 1: Fresh Deployment
  → Deploy container
  → Inject fake data
  → Inject monitoring
  → Setup logger

Daily:
  → Check attack_logger.py scan
  → Review new auth attempts
  → Note any DEFINITELY_BOT classifications

Weekly:
  → Run behavioral_analyzer.py
  → Run ttp_analyzer.py
  → Cross-correlation (month 2+)
  → Export attack data

Monthly:
  → Review cross_correlation_analyzer.py
  → Check returning attackers
  → Update detection rules
```

---

## 🎯 What Gets Logged

| Event | Logged Where | Details Captured |
-------|----------|----------------|
| SSH Login (success) | auth.log + database | IP, username, timestamp |
| SSH Login (failed) | auth.log + database | IP, username, timestamp |
| Commands executed | bash_history + auditd | Command, user, timestamp |
| File access | auditd | File, user, operation |
| Sensitive reads | command logs | Full command output |

---

## 📈 Attack Data Schema

### auth_attempts:
```sql
id, timestamp, username, result, source_ip, container_id, port
```

### commands:
```sql
id, timestamp, source_ip, command, session_id
```

### file_access:
```sql
id, timestamp, source_ip, file_path, access_type, session_id
```

---

## 🚨 Alert Conditions

**IMMEDIATE ALERT (Block IP):**
- Bot score ≥ 8 (DEFINITELY_BOT)
- More than 100 failed logins in 1 hour
- Access to /etc/shadow or /root/.ssh/ (real files)

**MONITOR CLOSELY:**
- Bot score 6-7 (LIKELY_BOT)
- Successful login to production-like accounts
- Running `curl | bash` or similar commands
- Accessing fake AWS/SSH credentials

**NORMAL ACTIVITY:**
- Bot score ≤ 3 (LIKELY_HUMAN)
- Standard reconnaissance commands
- Failed logins trying common passwords

---

## 📝 Export Formats

### JSON Export:
```bash
python query_db.py export --format json
# → attacks_2026-05-01.json
```

### CSV Export:
```bash
python query_db.py export --format csv
# → attacks_2026-05-01.csv
```

### Database Backup:
```bash
cp attacks.db attacks_$(date +%Y%m%d).db
```

---

## 🔗 Quick Links

- `attack_logger.py` - Log attacks to database
- `behavioral_analyzer.py` - Bot/human classification
- `ttp_analyzer.py` - MITRE ATT&CK mapping
- `cross_correlation_analyzer.py` - Long-term patterns
- `temporal_analyzer.py` - Time-based analysis
- `query_db.py` - Interactive database queries
- `health_check.sh` - System health verification

---

## ✅ Verification Checklist

After monitoring injection:

- [ ] `/var/log/attacks/` directory exists
- [ ] Bash history logging enabled in `.bashrc`
- [ ] auditd service running
- [ ] Attack database exists on host
- [ ] `attack_logger.py scan` shows data

**Test it:**
```bash
# SSH in and execute some commands
ssh root@localhost -p 2225
ls -la
cat /root/.aws/credentials
mysql --version

# Exit and check logs
exit

python attack_logger.py scan
# Should show your commands!
```

---

## 🎯 Example Investigation

**Scenario:** You see a DEFINITELY_BOT classification

1. **Check IP:**
   ```bash
   python query_db.py
   > ips --limit 5
   # Shows top attacking IPs
   ```

2. **View Commands:**
   ```bash
   python query_db.py
   > commands --limit 10
   # Shows what attacker did
   ```

3. **MITRE Mapping:**
   ```bash
   python ttp_analyzer.py
   # Shows TTPs used (T1110, T1082, etc.)
   ```

4. **Timeline:**
   ```bash
   python query_db.py
   > timeline --ip <attacker_ip>
   # Shows full attack sequence
   ```

5. **Block IP (if needed):**
   ```bash
   # Add to iptables
   iptables -A INPUT -s <attacker_ip> -j DROP
   ```

---

**🐝 Ready to catch attackers!**
