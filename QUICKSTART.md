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
```bash
python container_manager.py deploy 2225
```

### 4. Access Honeypot
```bash
ssh root@localhost -p 2225
# Password: password123
```

### 5. Test It!
```bash
# In SSH session, try:
mysql
redis-cli
psql
netstat -tulpn
cat /root/.aws/credentials
```

### 6. Start Monitoring
```bash
# Back in workspace
python container_manager.py schedule
python attack_logger.py scan
```

---

## Test Attack Detection

### Run Test Bot
```bash
python test_bot.py 30
```

### Analyze Results
```bash
python behavioral_analyzer.py
python ttp_analyzer.py
python cross_correlation_analyzer.py
```

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

### "Connection refused"
```bash
# Check container is running
docker ps

# Restart if needed
python container_manager.py deploy 2225
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

---

## Next Steps

1. **Explore fake services** - Test MySQL, Redis, PostgreSQL
2. **View fake files** - Check AWS creds, SSH keys, configs
3. **Run analyses** - Behavioral, TTP, Cross-correlation
4. **Monitor attacks** - Check logs periodically
5. **Expose to internet** - When ready (legal review first)

---

**🐝 Happy hunting!**
