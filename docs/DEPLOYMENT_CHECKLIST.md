# 🚀 Deployment Checklist - Phase 2.5

Quick reference for deploying the honeypot from scratch.

## ✅ Pre-Deployment Checklist

- [ ] Legal review complete (honeypot laws in your jurisdiction)
- [ ] VM provisioned (Ubuntu 22.04+ recommended)
- [ ] Docker installed and working
- [ ] Python 3.10+ available
- [ ] Network ports configured (22 for honeypot, 64222 for admin SSH)
- [ ] Firewall rules in place
- [ ] Backup location identified

---

## 📋 Deployment Steps

### 1. Clone Repository
```bash
git clone https://github.com/maradens/ai-containerized-honeypot-phase2.5.git
cd ai-containerized-honeypot-phase2.5
```

### 2. Build Docker Image
```bash
docker build -t honeypot-ubuntu:latest .
```

### 3. Setup Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Deploy Container
```bash
# Production (honeypot on port 22)
python container_manager.py deploy 22

# Testing (honeypot on port 2222)
python container_manager.py deploy 2222
```

### 5. Inject Fake Data
```bash
# Users, AWS creds, SSH keys, Git tokens, etc.
python fake_data_injector.py

# Interactive services (mysql, netstat, ps)
python inject_fake_services.py

# Additional fake files (enhanced)
python continue_fake_files.py
```

### 6. Add Common Credentials
```bash
# Add ubuntu/ubuntu and admin/password
./add_accounts.sh
```

### 7. Verify Health
```bash
./health_check.sh check
```

### 8. Test Honeypot
```bash
# Try logging in
ssh root@localhost -p 22
# Password: password123

# Test fake services
mysql
netstat -tulpn
ps aux
cat /root/.aws/credentials
```

### 9. Run First Attack Scan
```bash
python attack_logger.py scan
```

### 10. Start Monitoring (Manual)
```bash
# Daily check
python attack_logger.py stats

# Weekly analysis
python behavioral_analyzer.py
python ttp_analyzer.py

# Monthly correlation
python cross_correlation_analyzer.py
```

---

## 🎯 Post-Deployment

### Verify Everything
```bash
./health_check.sh check
```

### Expected Result
```
✓ Container: Running
✓ SSH Service: Listening on 22
✓ Fake Services: All present
✓ Fake Data: All present
✓ Database: Created
✓ Realism Check: No "Fake" text

ALL CHECKS PASSED ✓
```

### User Accounts Available
```
root      / password123
ubuntu    / ubuntu
admin     / password
developer / Dev@123456
webmaster / (locked)
backup    / (locked)
deploy    / (locked)
```

---

## 🔧 Troubleshooting

### Container won't start
```bash
./health_check.sh restore
```

### "Fake" text in output
```bash
# See DEPLOYMENT_ISSUES.md Issue #16
./health_check.sh restore
```

### Port 22 already in use
```bash
# Change admin SSH to port 64222
# See README.md "Production Deployment Notes"
```

### Missing fake data
```bash
python fake_data_injector.py
python inject_fake_services.py
```

---

## 📊 Quick Commands Reference

| Task | Command |
|------|-------|
| Check status | `./health_check.sh status` |
| Full health check | `./health_check.sh check` |
| Restore honeypot | `./health_check.sh restore` |
| Add credentials | `./add_accounts.sh` |
| View attacks | `python attack_logger.py stats` |
| Scan for attacks | `python attack_logger.py scan` |
| Behavioral analysis | `python behavioral_analyzer.py` |
| TTP mapping | `python ttp_analyzer.py` |
| Long-term patterns | `python cross_correlation_analyzer.py` |
| Export data | `python attack_logger.py export` |

---

## 📚 Documentation

- **README.md** - Complete guide
- **QUICKSTART.md** - 5-minute setup
- **DOCS.md** - Detailed documentation
- **ARCHITECTURE.md** - Architecture diagrams
- **DEPLOYMENT_ISSUES.md** - Troubleshooting guide
- **HEALTH_CHECK.md** - Health monitoring guide

---

**Ready to deploy!** 🐝✨
