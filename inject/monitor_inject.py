#!/usr/bin/env python3
"""
Inject monitoring system into the running honeypot container
"""

from honeypot_config import get_config
import docker
import sys

# Connect to Docker
client = docker.from_env()
container = client.containers.get(get_config()["container_name"])

print("🔍 Injecting monitoring system...")

# 1. Create attack log directory
container.exec_run("mkdir -p /var/log/attacks")
print("  ✓ Created /var/log/attacks")

# Enable bash history logging
monitoring_script = """
# Create history file
touch /var/log/attacks/bash_history
chmod 600 /var/log/attacks/bash_history

# Log all executed commands (simple approach)
export PROMPT_COMMAND='history -a'
export HISTFILE=/var/log/attacks/bash_history
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTTIMEFORMAT='%F %T '
"""

container.exec_run(monitoring_script)
print("  ✓ Bash history logging enabled")

# Now add to bashrc correctly (this persists for new sessions)
bashrc_content = """
# Enable command logging
export PROMPT_COMMAND='history -a'
export HISTFILE=/var/log/attacks/bash_history
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTTIMEFORMAT='%F %T '
"""

container.exec_run(f"echo '{bashrc_content}' >> /root/.bashrc")
container.exec_run('chmod +x /root/.bashrc')
print("  ✓ Bashrc updated for new sessions")

# 3. Install auditd for system-level monitoring
container.exec_run("apt-get update && apt-get install -y auditd > /dev/null 2>&1 || true")
print("  ✓ Auditd installed")

# 4. Configure audit rules
audit_rules = """
# Monitor sensitive files
auditctl -w /etc/passwd -p wa -k passwd_changes
auditctl -w /etc/shadow -p wa -k shadow_changes
auditctl -w /etc/ssh -p wa -k ssh_changes
auditctl -w /root/.ssh -p wa -k ssh_key_changes
auditctl -w /home -p wa -k home_changes

# Monitor command execution
auditctl -a exit,always -F arch=b64 -S execve -k commands_executed

# Start auditd
service auditd start || true
"""

container.exec_run(audit_rules)
print("  ✓ Audit rules configured")

# 5. Create monitoring summary script
monitor_script = '''
cat > /usr/local/bin/monitor_status.sh << 'EOF'
#!/bin/bash
echo "=== HONEYPOT ATTACK MONITORING ==="
echo ""
echo "1. Current Users:"
who
echo ""
echo "2. Recent Commands (last 20):"
tail -20 /var/log/attacks/command_log 2>/dev/null || echo "No commands logged yet"
echo ""
echo "3. File Access Log:"
tail -10 /var/log/attacks/file_access.log 2>/dev/null || echo "No file access logged yet"
echo ""
echo "4. Audit Log (last 10 events):"
ausearch -ts recent -k commands_executed 2>/dev/null | tail -10 || echo "No audit events yet"
echo ""
echo "5. Network Connections:"
netstat -tunap 2>/dev/null || ss -tunap
echo ""
echo "6. Process List:"
ps aux
EOF
chmod +x /usr/local/bin/monitor_status.sh
'''

container.exec_run(monitor_script)
print("  ✓ Monitoring status script created")

print("\n✅ Monitoring system injected!")
print("\n📊 To view monitoring data:")
print("   From your SSH session, run: monitor_status.sh")
print("   Or check logs directly:")
print("     - Commands: /var/log/attacks/command_log")
print("     - File access: /var/log/attacks/file_access.log")
print("     - Auth log: /var/log/auth.log")
print("     - Audit log: ausearch -ts recent")
print("\n🐝 I can also monitor from outside:")
print("   Run 'docker logs honeypot-manual-test' or use my monitoring commands")
