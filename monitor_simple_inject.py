#!/usr/bin/env python3
"""
Inject simple authentication monitoring (non-intrusive)
"""

import docker

# Connect to Docker
client = docker.from_env()
container = client.containers.get("honeypot-manual-test")

print("🔐 Injecting authentication monitoring.\\n")

# 1. Create monitoring directories
container.exec_run("mkdir -p /var/log/attacks")
print("✓ Created log directory")

# 2. Configure SSH verbose logging (edit config, will apply to new connections)
container.exec_run("sed -i 's/#LogLevel.*/LogLevel VERBOSE/' /etc/ssh/sshd_config")
container.exec_run("sed -i 's/^LogLevel.*/LogLevel VERBOSE/' /etc/ssh/sshd_config")
print("✓ SSH verbose logging enabled")

# 3. Create auth status script
script = """
cat > /usr/local/bin/auth_monitor_status.sh << 'ENDSCRIPT'
#!/bin/bash
echo "=== AUTHENTICATION MONITORING ==="
echo ""
echo "1. Current Sessions:"
who
echo ""
echo "2. Login History:"
last -15
echo ""
echo "3. Failed Login Attempts:"
lastb -15 2>/dev/null || echo "lastb not available"
echo ""
echo "4. SSH Auth Log (last 20 lines):"
tail -20 /var/log/auth.log 2>/dev/null || tail -20 /var/log/syslog 2>/dev/null || echo "No auth log found"
echo ""
echo "5. Failed Attempts Count:"
grep -c "Failed password" /var/log/auth.log 2>/dev/null || echo "0"
echo ""
echo "6. Successful Logins Count:"
grep -c "Accepted" /var/log/auth.log 2>/dev/null || echo "0"
echo ""
echo "7. All Auth Events:"
grep -E "Accepted|Failed|authentication failure|Invalid user" /var/log/auth.log 2>/dev/null | tail -30 || echo "No events yet"
ENDSCRIPT

chmod +x /usr/local/bin/auth_monitor_status.sh
"""

container.exec_run(script)
print("✓ Auth status script created")

# 4. Create detailed auth analyzer
analyzer = """
cat > /usr/local/bin/analyze_auth.sh << 'ENDSCRIPT'
#!/bin/bash
echo "=== DETAILED AUTHENTICATION ANALYSIS ==="
echo ""
echo "Authentication Statistics:"
echo "---------------------------"
total_attempts=$(grep -cE "Accepted|Failed" /var/log/auth.log 2>/dev/null || echo "0")
successful=$(grep -c "Accepted" /var/log/auth.log 2>/dev/null || echo "0")
failed=$(grep -c "Failed" /var/log/auth.log 2>/dev/null || echo "0")

echo "Total attempts: $total_attempts"
echo "Successful logins: $successful"
echo "Failed attempts: $failed"
echo ""

if [ "$failed" -gt 0 ]; then
    echo "Top Failed Usernames:"
    grep "Failed password" /var/log/auth.log 2>/dev/null | \
        grep -oP "for (invalid user )?\\K\\w+" | \
        sort | uniq -c | sort -rn | head -10
    echo ""
    
    echo "Top Attacker IPs:"
    grep "Failed password" /var/log/auth.log 2>/dev/null | \
        grep -oP "from \\K[0-9.]+" | \
        sort | uniq -c | sort -rn | head -10
fi

echo ""
echo "Successful Logins Detail:"
grep "Accepted" /var/log/auth.log 2>/dev/null | \
    awk '{for(i=1;i<=NF;i++) if($i=="Accepted") print $(i-3)" "$(i-2)" "$(i+1)" from "$(i+3)}'
ENDSCRIPT

chmod +x /usr/local/bin/analyze_auth.sh
"""

container.exec_run(analyzer)
print("✓ Auth analyzer created")

print("\n✅ Monitoring injected successfully!")
print("\n📊 To check auth logs:")
print("   From SSH: auth_monitor_status.sh")
print("   From SSH: analyze_auth.sh")
print("\n🔍 I can also monitor from outside!")
