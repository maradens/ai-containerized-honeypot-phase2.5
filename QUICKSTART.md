# 🚀 Quick Start Guide

## 5-Minute Setup

### 1. Build Image (1 minute)
```bash
docker build -t honeypot-ubuntu:latest .
```

### 2. Setup Python (1 minute)
```bash
python3 -m venv venv
source venv/bin/activate
pip install docker
```

### 3. Deploy Container (1 minute)

**Production Deployment (Recommended):**
```bash
python container_manager.py deploy 22
```

**Local Testing (Alternative):**
```bash
python container_manager.py deploy 2225
```

### 4. Access Honeypot

**Production (honeypot on port 22):**
```bash
# Multiple accounts available:
ssh root@localhost -p 22          # Password: password123
ssh ubuntu@localhost -p 22        # Password: ubuntu
ssh admin@localhost -p 22         # Password: password
ssh developer@localhost -p 22     # Password: Dev@123456
```

**Local Testing (port 2225):**
```bash
ssh root@localhost -p 2225        # Password: password123
ssh ubuntu@localhost -p 2225      # Password: ubuntu
ssh admin@localhost -p 2225       # Password: password
```

**All accounts have the same fake data and services available!**

### 5. Test It!
```bash
# In SSH session, try:
mysql              # Should show: mysql Ver 15.1 Distrib 10.0.39-MariaDB
netstat -tulpn     # Should show: Active Internet connections (servers and established)
ps aux            # Should show realistic process list
cat /root/.aws/credentials  # Should show 3 AWS profiles
cat /var/www/html/.env     # Should show fake secrets
```

**⚠️ IMPORTANT:** Service outputs must NOT contain "Fake" text!

**Expected (CORRECT):**
```bash
$ mysql --version
mysql  Ver 15.1 Distrib 10.0.39-MariaDB, for debian-linux-gnu (x86_64)
```

**NOT Expected (WRONG - gives away honeypot):**
```bash
$ mysql --version
MySQL Fake Server v5.7.42-0ubuntu0.20.04.1
```

### 6. Start Monitoring (MANUAL ONLY)

**⚠️ IMPORTANT:** Do NOT set up continuous monitoring (no cron jobs, no background processes). Use scripts manually when you want to check.

**To check for attacks manually:**
```bash
# SSH into VM
ssh maradens@<VM_IP> -p 64222

# Navigate to project
cd ~/ai-containerized-honeypot-phase2.5

# Activate venv
source venv/bin/activate

# Check attack statistics
python attack_logger.py stats

# Scan for new data
python attack_logger.py scan
```

---

## Test Attack Detection (Manual Analysis)

### Run Test Bot (Optional - Creates Test Data)
```bash
python test_bot.py 30
```
This simulates 30 SSH login attempts for testing purposes.

---

## Manual Analysis Commands

### 1. Quick Check (Daily)
```bash
python attack_logger.py stats
```
**Output:** Total attempts, success/fail counts, top IPs

### 2. Full Scan (Daily)
```bash
python attack_logger.py scan
```
**Output:** Updates database and shows full statistics

### 3. Behavioral Analysis (Weekly)
```bash
python behavioral_analyzer.py
```
**Output:** Bot vs Human classification with scoring

### 4. MITRE ATT&CK Mapping (Weekly)
```bash
python ttp_analyzer.py
```
**Output:** TTP report with MITRE ATT&CK technique IDs

### 5. Long-term Patterns (Monthly)
```bash
python cross_correlation_analyzer.py
```
**Output:** Persistent attacker detection, time patterns

### 6. Export Data (As Needed)
```bash
python attack_logger.py export
```
**Output:** JSON file for external analysis

---

## Expected Output (Example)

```
📊 ATTACK STATISTICS

Total attempts: 7
By result:
  FAILED: 3
  SUCCESS: 4

Top source IPs:
  111.94.104.82 | Attempts: 6 | Failed: 3
  152.118.101.240 | Attempts: 1 | Failed: 0

Last 7 days activity:
  2026-04-17: 7 attempts
```

---

## Important Notes

1. **No Continuous Monitoring:** All scripts run manually only
2. **Database Location:** `~/ai-containerized-honeypot-phase2.5/data/attacks.db`
3. **Your Test IP:** Filter out your own IP when analyzing real attacks
4. **First Run:** Creates the database automatically

---

## Expected Output

```
✅ Container running on port 2225
✅ All fake services installed
✅ Command logging active
✅ Automated maintenance scheduled
✅ Analysis tools ready
```

---

## Common Issues

### "Fake" Text in Service Output (CRITICAL!)
```bash
# WRONG - gives away honeypot:
$ mysql --version
MySQL Fake Server v5.7.42

# FIX - see DEPLOYMENT_ISSUES.md Issue #16
docker exec -i honeypot-manual-test tee /usr/local/bin/mysql > /dev/null << 'EOF'
#!/bin/bash
echo "mysql  Ver 15.1 Distrib 10.0.39-MariaDB, for debian-linux-gnu (x86_64) using  EditLine wrapper"
EOF
chmod +x /usr/local/bin/mysql
```

### "Connection refused"
```bash
# Check container is running
docker ps

# Restart if needed
python container_manager.py deploy 22
```

### "Permission denied" for Docker
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Then logout/login or:
newgrp docker
```

### "Module not found"
```bash
# Activate venv
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
```

### Port 22 Already in Use
```bash
# See README.md "Production Deployment Notes"
# Change admin SSH to port 64222, use port 22 for honeypot
```

---

## Next Steps

1. **Explore fake services** - Test MySQL, Redis, PostgreSQL
2. **View fake files** - Check AWS creds, SSH keys, configs
3. **Run analyses** - Behavioral, TTP, Cross-correlation
4. **Monitor attacks** - Check logs periodically
5. **Expose to internet** - When ready (legal review first)

---

**🐝 Happy hunting!**
