#!/usr/bin/env python3
"""
Inject monitoring system into the running honeypot container
"""

import docker
import sys

# Connect to Docker
client = docker.from_env()
container = client.containers.get("honeypot-manual-test")

print("🔍 Injecting monitoring system...")

# 1. Create attack log directory
container.exec_run("mkdir -p /var/log/attacks")
print("  ✓ Created /var/log/attacks")

# 2. Enable bash history logging
monitoring_script = """
# Enable command logging
echo "export PROMPT_COMMAND='history -a'" >> /root/.bashrc
echo "export HISTFILE=/var/log/attacks/bash_history" >> /root/.bashrc
echo "export HISTSIZE=10000" >> /root/.bashrc
echo "export HISTFILESIZE=20000" >> /root/.bashrc
echo "export HISTTIMEFORMAT='%F %T '" >> /root/.bashrc

# Create history file
touch /var/log/attacks/bash_history
chmod 600 /var/log/attacks/bash_history

# Log all executed commands
echo "" >> /root/.bashrc
echo "# Log every command" >> /root/.bashrc
echo 'trap "echo \\$(date +\\'%Y-%m-%d %H:%M:%S\\') - \\$COMMAND >> /var/log/attacks/command_log" DEBUG" >> /root/.bashrc

# Log file access
echo "" >> /root/.bashrc
echo "# Log file access" >> /root/.bashrc
echo 'alias cat="echo \$(date +%Y-%m-%d\ %H:%M:%S) - cat \$@ >> /var/log/attacks/file_access.log; command cat \$@ "' >> /root/.bashrc
echo 'alias ls="echo \$(date +%Y-%m-%d\ %H:%M:%S) - ls \$@ >> /var/log/attacks/file_access.log; command ls \$@ "' >> /root/.bashrc
echo 'alias vim="echo \$(date +%Y-%m-%d\ %H:%M:%S) - vim \$@ >> /var/log/attacks/file_access.log; command vim \$@ "' >> /root/.bashrc
echo 'alias nano="echo \$(date +%Y-%m-%d\ %H:%M:%S) - nano \$@ >> /var/log/attacks/file_access.log; command nano \$@ "' >> /root/.bashrc
"""

container.exec_run(monitoring_script)
print("  ✓ Bash history logging enabled")

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
