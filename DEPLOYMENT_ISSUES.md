# 🐝 Deployment Issues & Fixes

Common problems encountered during Phase 2.5 honeypot deployment and their solutions.

---

## Issue 1: Port 22 Already in Use by Host SSH

**Symptom:**
```
docker.errors.APIError: 500 Server Error ... failed to bind host port 0.0.0.0:22/tcp: address already in use
```

**Root Cause:** VM's admin SSH daemon is using port 22.

**Solution:**
1. **Option A (Recommended for Production):**
   - Move admin SSH to port 64222
   - Use port 22 for honeypot (most attractive to attackers)

2. **Option B (Local Testing):**
   - Keep admin SSH on port 22
   - Use port 2222 for honeypot

**Steps to Change Admin SSH Port:**
```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config
# Change: Port 22 → Port 64222

# Edit systemd socket (CRITICAL - many miss this!)
sudo nano /etc/systemd/system/ssh.socket
# Change: ListenStream=22 → ListenStream=64222

# Restart services
sudo systemctl daemon-reload
sudo systemctl restart ssh

# Verify
sudo ss -tulpn | grep -E ':(22|64222) '
```

---

## Issue 2: Container Crashes/Exits Immediately

**Symptom:**
```
CONTAINER ID   STATUS
5b178033e2d0   Exited (0) 11 seconds ago
```

**Root Cause:** Docker's CMD with `/usr/sbin/sshd -D` conflicts with container lifecycle. SSH daemon exits cleanly, causing container to stop.

**Solutions:**

### Solution A: Use bash wrapper (Recommended)
```bash
docker run -d --name honeypot-manual-test \
  -p 22:22 \
  --restart unless-stopped \
  honeypot-ubuntu \
  /bin/bash -c '/usr/sbin/sshd -D'
```

### Solution B: Add sleep infinity
```bash
docker run -d --name honeypot-manual-test \
  -p 22:22 \
  --restart unless-stopped \
  honeypot-ubuntu \
  /bin/bash -c '/usr/sbin/sshd -D & sleep infinity'
```

**Verify:**
```bash
docker ps                    # Should show "Up X seconds"
docker logs honeypot-manual-test  # Should show "Server listening on port 22"
```

---

## Issue 3: put_archive() Directory Not Found

**Symptom:**
```
docker.errors.NotFound: 404 Client Error ... Could not find the file /var/www/html/admin
```

**Root Cause:** `put_archive()` requires parent directory to exist. Docker doesn't auto-create directories.

**Affected Scripts:**
- `inject_fake_services.py` (line 101)
- Any script using `container.put_archive()`

**Solutions:**

### Solution A: Create directory first
```python
# Before put_archive
container.exec_run('mkdir -p /var/www/html/admin')
container.put_archive('/var/www/html/admin', tar_data)
```

### Solution B: Use exec_run with heredoc (simpler for small files)
```python
# Instead of put_archive
content = """<!DOCTYPE html>
<html><body><h1>Admin Panel</h1></body></html>"""
container.exec_run(f'mkdir -p /var/www/html/admin')
container.exec_run(f'echo "{content}" > /var/www/html/admin/index.html')
```

### Solution C: Use docker cp from host
```bash
# On host machine
docker cp index.html honeypot-manual-test:/var/www/html/admin/
```

---

## Issue 4: "Interactive Services Not Found" False Positive

**Symptom:**
```
🎭 Copying interactive services...
  ✗ mysql not found
  ✗ redis-cli not found
  ✗ psql not found

✅ Interactive services installed!
```

**Root Cause:** Script checks if files exist in **local** `interactive_services/` directory, but reports status before checking **container**. Files ARE copied successfully.

**Verify Installation:**
```bash
# Check if files exist in container
docker exec honeypot-manual-test ls -la /usr/local/bin/mysql
docker exec honeypot-manual-test ls -la /usr/local/bin/redis-cli
docker exec honeypot-manual-test ls -la /usr/local/bin/psql

# Test if they work
docker exec honeypot-manual-test mysql --version
docker exec honeypot-manual-test redis-cli --version
docker exec honeypot-manual-test psql --version
```

**Expected Output:**
```
-rwxrwxr-x 1 1000 1000 3832 Apr 17 02:07 /usr/local/bin/mysql
MySQL Fake Server v5.7.42-0ubuntu0.20.04.1
```

**Fix Script:** Update `copy_interactive_services.py` to check container instead:
```python
# Instead of:
if os.path.exists(f'interactive_services/{service}'):

# Use:
result = container.exec_run(f'which {service}')
if result.exit_code == 0:
    print(f'  ✓ {service} found in container')
```

---

## Issue 5: Command Logger File Not Found

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 
'/home/maradens/.openclaw/workspace/ai-honeypot-phase1/scripts/command_logging.sh'
```

**Root Cause:** Script references old Phase 1 path. Files were moved/renamed for Phase 2.5.

**Solution A: Update path in script**
```python
# In command_logger_injector.py, change:
script_path = '/home/maradens/.openclaw/workspace/ai-honeypot-phase1/scripts/command_logging.sh'

# To:
script_path = '/home/maradens/ai-containerized-honeypot-phase2.5/scripts/command_logging.sh'
```

**Solution B: Use simpler logger (recommended)**
```bash
# This creates logger directly without external files
python setup_logger.py
```

**Solution C: Create missing directory**
```bash
mkdir -p /home/maradens/.openclaw/workspace/ai-honeypot-phase1/scripts/
# Copy command_logging.sh there (if you still have it)
```

---

## Issue 6: "Container is restarting" During Injection

**Symptom:**
```
docker.errors.APIError: 409 Client Error ... container is restarting, wait until the container is running
```

**Root Cause:** Container restarts during injection (especially with SSH daemon manipulation). Scripts run too fast and hit restarting container.

**Solution A: Add delays**
```python
import time

# After each injection step
time.sleep(3)  # Wait for container to stabilize
```

**Solution B: Check container status before operations**
```python
def wait_for_container(container, timeout=10):
    import time
    start = time.time()
    while time.time() - start < timeout:
        container.reload()
        if container.status == 'running':
            return True
        time.sleep(1)
    raise Exception("Container failed to start")

# Use before each operation
wait_for_container(container)
```

**Solution C: Run injections sequentially**
```bash
# Don't run all at once. Do step by step:
python fake_data_injector.py
# Wait, verify
docker ps | grep honeypot

python inject_fake_services.py
# Wait, verify
docker exec honeypot-manual-test which mysql

python copy_interactive_services.py
# etc.
```

---

## Issue 7: Invalid Escape Sequence Warnings

**Symptom:**
```
monitor_auth_inject.py:34: SyntaxWarning: invalid escape sequence '\K'
monitor_auth_inject.py:88: SyntaxWarning: invalid escape sequence '\|'
```

**Root Cause:** Python 3.12+ is stricter about escape sequences in regular strings. `\K` and `\|` are not valid Python escape sequences.

**Solution: Use raw strings**
```python
# Change from:
auth_monitor_script = """
echo '\K'  # Clear to start of line
"""

# To:
auth_monitor_script = r"""
echo '\K'  # Clear to start of line
"""
```

**Note:** These warnings are **harmless** and don't affect functionality. The shell receives the correct strings.

---

## Issue 8: Invalid Condition "running" in container.wait()

**Symptom:**
```
docker.errors.APIError: 400 Client Error ... invalid condition: "running"
```

**Root Cause:** Docker SDK version incompatibility. Older versions use `container.wait(condition='running')`, newer versions don't support 'running' condition.

**Solution A: Update wait condition**
```python
# Change from:
container.wait(condition='running')

# To:
container.wait(condition='exited')  # or 'removed'
# Or just remove the wait entirely:
time.sleep(2)  # Simple delay
```

**Solution B: Use different check**
```python
import time
time.sleep(2)

# Verify container is running
container.reload()
if container.status != 'running':
    raise Exception("Container not running")
```

---

## Issue 9: Passwordless SSH Not Working

**Symptom:**
```
Permission denied (publickey,password).
```

**Root Cause:** SSH key not properly installed on VM, or wrong permissions.

**Solution:**
```bash
# On LOCAL machine
ssh-keygen -t ed25519 -C "your-email@example.com"
# Press Enter to accept defaults

# Copy to VM (uses password this one time)
ssh-copy-id maradens@152.118.201.103 -p 64222

# Verify
ssh maradens@152.118.201.103 -p 64222
# Should connect without password

# Check permissions on VM
ssh maradens@152.118.201.103 -p 64222 "ls -la ~/.ssh/"
# Should show: drwx------ for .ssh, -rw------- for authorized_keys
```

**Manual fix if ssh-copy-id fails:**
```bash
# On LOCAL machine
cat ~/.ssh/id_ed25519.pub

# Copy output, then on VM:
ssh maradens@152.118.201.103 -p 64222
mkdir -p ~/.ssh
echo "PASTE_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
exit
```

---

## Issue 10: Passwordless Sudo Not Configured

**Symptom:**
```
[maradens@honeypot password]:
```
(Script requires password input, can't automate)

**Solution:**
```bash
# Edit sudoers file (safely)
sudo visudo

# Add this line at the end (replace 'maradens' with your username):
maradens ALL=(ALL) NOPASSWD: ALL

# Save and exit (:wq in vim)

# Test
sudo whoami
# Should output: root (without password prompt)
```

**Security Note:** This gives full root access without password. For production, be more specific:
```bash
# More restrictive (only allow specific commands)
maradens ALL=(ALL) NOPASSWD: /usr/bin/docker*, /usr/sbin/sshd
```

---

## Issue 11: Firewall Blocking Honeypot Port

**Symptom:**
```
Connection timed out
```

**Solution:**
```bash
# Check firewall status
sudo ufw status

# If active, add rules:
sudo ufw allow 22/tcp       # Honeypot
sudo ufw allow 64222/tcp    # Admin SSH
sudo ufw allow 80/tcp       # HTTP (optional)
sudo ufw allow 443/tcp      # HTTPS (optional)

# Enable if not already
sudo ufw enable

# Verify
sudo ufw status verbose
```

---

## Issue 12: No Swap Space (Container Build Fails)

**Symptom:**
```
Error: cannot allocate memory
```
During Docker image build

**Solution:**
```bash
# Check current swap
free -h
# If Swap shows 0B, create swap:

# Create 2GB swap file
sudo fallocate -l 2G /swapfile

# Set permissions
sudo chmod 600 /swapfile

# Make it a swap area
sudo mkswap /swapfile

# Enable swap
sudo swapon /swapfile

# Make permanent (survives reboot)
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify
free -h
# Should show 2.0G swap
```

---

## Issue 13: Container Name Wrong in Scripts

**Symptom:**
```
docker.errors.NotFound: 404 Client Error ... container not found
```

**Root Cause:** Scripts use hardcoded container name `honeypot-manual-test`, but you deployed as `honeypot-prod` or different name.

**Solution:**
```bash
# Check actual container name
docker ps --format '{{.Names}}'

# Update all scripts to use correct name
# In container_manager.py, attack_logger.py, etc.:
# Change: CONTAINER_NAME = "honeypot-manual-test"
# To:     CONTAINER_NAME = "honeypot-prod"
```

**Or use environment variable:**
```bash
export HONEYPOT_CONTAINER="honeypot-prod"

# In scripts:
CONTAINER_NAME = os.environ.get('HONEYPOT_CONTAINER', 'honeypot-manual-test')
```

---

## Issue 14: Injection Scripts Fail Mid-Stream

**Symptom:**
```
Step 1: ✓ Complete
Step 2: ✓ Complete
Step 3: ✗ Error (container not running)
Step 4: ✗ Error (container not running)
...
```

**Root Cause:** Container crashed during Step 3, all subsequent steps fail.

**Solution:**
```bash
# 1. Check container status
docker ps -a

# 2. If stopped, restart it
docker start honeypot-manual-test
sleep 2

# 3. Verify it's running
docker ps

# 4. Re-run FAILED steps only (not all)
python inject_fake_services.py  # Re-run Step 3
python copy_interactive_services.py  # Re-run Step 4
python setup_logger.py  # Re-run Step 5
python monitor_auth_inject.py  # Re-run Step 6
```

**Prevention:** Run injections one at a time with verification:
```bash
python fake_data_injector.py
docker exec honeypot-manual-test ls /root/.aws/credentials
# Verify before continuing...

python inject_fake_services.py
docker exec honeypot-manual-test which mysql
# Verify before continuing...
```

---

## Issue 15: Database Path Wrong in Scripts

**Symptom:**
```
sqlite3.OperationalError: no such table: auth_attempts
```
Or scripts read old Phase 1 data instead of production data

**Root Cause:** Scripts use hardcoded path `/home/maradens/.openclaw/workspace/ai-honeypot-phase1/data/attacks.db` instead of production path.

**Solution:**
```python
# In attack_logger.py, behavioral_analyzer.py, etc.:
# Change:
DB_PATH = '/home/maradens/.openclaw/workspace/ai-honeypot-phase1/data/attacks.db'

# To (on production VM):
DB_PATH = '/home/maradens/ai-containerized-honeypot-phase2.5/data/attacks.db'

# Or use environment variable:
import os
DB_PATH = os.environ.get('HONEYPOT_DB_PATH', './data/attacks.db')
```

---

## Issue 16: "Fake" Text in Service Output (CRITICAL!)

**Symptom:**
```
$ mysql --version
MySQL Fake Server v5.7.42-0ubuntu0.20.04.1

$ netstat -tulpn
Active Internet connections (w/o servers)
```

**Root Cause:** Fake service scripts include "Fake" or "w/o servers" in output, giving away that it's a honeypot. Attackers will immediately know it's not real!

**Impact:** ⚠️ **HIGH** - Compromises the entire honeypot's effectiveness

**Solution:**

### Fix MySQL:
```bash
# On VM:
docker exec -i honeypot-manual-test tee /usr/local/bin/mysql > /dev/null << 'EOF'
#!/bin/bash
if [[ "$1" == "--version" ]] || [[ "$1" == "-V" ]]; then
    echo "mysql  Ver 15.1 Distrib 10.0.39-MariaDB, for debian-linux-gnu (x86_64) using  EditLine wrapper"
    exit 0
fi
echo "Welcome to the MySQL monitor.  Commands end with ; or \g."
echo "Your MySQL connection id is $RANDOM"
echo "Server version: 10.0.39-MariaDB-0ubuntu0.20.04.2 Ubuntu 20.04"
echo ""
echo "Copyright (c) 2000, 2024, Oracle, MariaDB Corporation Ab and others."
echo ""
echo "Type 'help'; or '\h' for help. Type '\c' to clear the current input statement."
echo ""
echo "mysql> SHOW TABLES;"
echo "+--------------+"
echo "| Tables_in_db|"
echo "+--------------+"
echo "| api_keys     |"
echo "| credentials  |"
echo "| users        |"
echo "+--------------+"
echo "3 rows in set (0.00 sec)"
echo ""
echo "mysql> "
EOF
chmod +x /usr/local/bin/mysql
```

### Fix netstat:
```bash
# Change from:
echo "Active Internet connections (w/o servers)"

# To:
echo "Active Internet connections (servers and established)"
```

### Fix ps:
```bash
# Make output look like real Linux ps aux:
echo "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND"
echo "root         1  0.0  0.1  16544  3200 ?        Ss   13:55   0:00 /sbin/init"
echo "root       123  0.0  0.2 567890 45632 ?        Ss   13:55   0:00 /usr/sbin/sshd: /usr/sbin/sshd -D"
# ... (more realistic processes)
```

**Verification:**
```bash
# Should show NO "Fake" text:
docker exec honeypot-manual-test mysql --version
# Output: mysql  Ver 15.1 Distrib 10.0.39-MariaDB, for debian-linux-gnu (x86_64)

docker exec honeypot-manual-test netstat -tulpn
# Output: Active Internet connections (servers and established)
```

**Prevention:** Always test service outputs before deploying. Attackers will notice:
- "Fake" in any output ❌
- "w/o servers" in netstat ❌
- Unrealistic process names ❌
- Missing standard Linux output format ❌

---

## Best Practices

### 1. **Always Test Connection First**
```bash
# Before running any script, verify VM access:
ssh maradens@152.118.201.103 -p 64222 "hostname"
# Should output: honeypot
```

### 2. **Check Container Status Before Injection**
```bash
docker ps | grep honeypot
# Should show: Up X seconds/minutes
```

### 3. **Verify Each Step**
```bash
python fake_data_injector.py
# Verify:
docker exec honeypot-manual-test cat /root/.aws/credentials
# Should show AWS credentials

python inject_fake_services.py
# Verify:
docker exec honeypot-manual-test which mysql
# Should show: /usr/local/bin/mysql
```

### 4. **Log Everything**
```bash
# Run injections with logging:
python fake_data_injector.py 2>&1 | tee injection-log-$(date +%Y%m%d).txt
```

### 5. **Have Recovery Plan**
```bash
# If all else fails, redeploy fresh:
docker stop honeypot-manual-test
docker rm honeypot-manual-test
docker run -d --name honeypot-manual-test -p 22:22 honeypot-ubuntu /bin/bash -c '/usr/sbin/sshd -D'
# Re-run all injections from scratch
```

---

**🐝 Documented from real deployment on April 16-17, 2026**
