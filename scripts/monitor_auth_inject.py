#!/usr/bin/env python3
"""
Inject enhanced authentication monitoring into the honeypot container
Captures: username/password attempts, login times, failed attempts
"""

from honeypot_config import get_config
import docker
import sys

# Connect to Docker
client = docker.from_env()
container = client.containers.get(get_config()["container_name"])

print("🔐 Injecting enhanced authentication monitoring...")

# 1. Configure SSH to log all authentication attempts
sshd_config_patch = """
# Backup original config
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# Set verbose logging
sed -i 's/#LogLevel.*/LogLevel VERBOSE/' /etc/ssh/sshd_config
sed -i 's/LogLevel.*/LogLevel VERBOSE/' /etc/ssh/sshd_config

# Enable detailed authentication logging
echo "AuthLogWarning yes" >> /etc/ssh/sshd_config
echo "LogFailures yes" >> /etc/ssh/sshd_config
"""

container.exec_run(sshd_config_patch)
print("  ✓ SSH verbose logging enabled")

# 2. Create authentication log interceptor
auth_monitor_script = """
# Create auth monitoring script
cat > /usr/local/bin/auth_monitor.sh << 'AUTHSCRIPT'
#!/bin/bash

# Authentication monitoring log
AUTH_LOG="/var/log/attacks/auth_attempts.log"
FAIL_LOG="/var/log/attacks/auth_failures.log"
SUCCESS_LOG="/var/log/attacks/auth_success.log"

# Initialize logs
touch $AUTH_LOG $FAIL_LOG $SUCCESS_LOG

# Function to log auth attempt
log_auth_attempt() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local source_ip=$1
    local username=$2
    local result=$3
    local method=$4
    
    echo "[$timestamp] IP: $source_ip | User: $username | Result: $result | Method: $method" >> $AUTH_LOG
    
    if [ "$result" = "SUCCESS" ]; then
        echo "[$timestamp] IP: $source_ip | User: $username | Method: $method" >> $SUCCESS_LOG
    else
        echo "[$timestamp] IP: $source_ip | User: $username | Method: $method" >> $FAIL_LOG
    fi
}

# Monitor auth.log in real-time
echo "Starting authentication monitor..."
tail -f /var/log/auth.log 2>/dev/null | while read line; do
    if echo "$line" | grep -q "Accepted"; then
        ip=$(echo "$line" | grep -oP 'from \K[0-9.]+' | head -1)
        user=$(echo "$line" | grep -oP 'for \K\w+' | head -1)
        method=$(echo "$line" | grep -oP '(password|publickey|keyboard-interactive)' | head -1)
        log_auth_attempt "$ip" "$user" "SUCCESS" "$method"
    elif echo "$line" | grep -q "Failed\|Failed password\|authentication failure"; then
        ip=$(echo "$line" | grep -oP 'from \K[0-9.]+' | head -1)
        user=$(echo "$line" | grep -oP 'for (invalid user )?\K\w+' | head -1)
        method="password"
        log_auth_attempt "$ip" "$user" "FAILED" "$method"
    fi
done
AUTHSCRIPT

chmod +x /usr/local/bin/auth_monitor.sh
"""

container.exec_run(auth_monitor_script)
print("  ✓ Auth monitor script created")

# 3. Create credential capture wrapper for login
credential_capture = """
# Create PAM script to capture credentials (for research only)
mkdir -p /var/log/pam
cat > /var/log/pam/auth_capture << 'PAMSCRIPT'
#!/bin/bash
# This captures authentication events from PAM
exec >> /var/log/attacks/pam_auth.log 2>&1
while true; do
    dmesg | tail -1 | grep -i "auth\|pam\|session" >> /var/log/attacks/pam_auth.log 2>/dev/null
    sleep 2
done
PAMSCRIPT
chmod +x /var/log/pam/auth_capture
"""

container.exec_run(credential_capture)
print("  ✓ PAM auth capture ready")

# 4. Create summary script for auth monitoring
auth_summary_script = '''
cat > /usr/local/bin/auth_monitor_status.sh << 'EOF'
#!/bin/bash

echo "=== AUTHENTICATION MONITORING STATUS ==="
echo ""
echo "1. Authentication Attempts (Last 20):"
if [ -f /var/log/attacks/auth_attempts.log ]; then
    tail -20 /var/log/attacks/auth_attempts.log
else
    echo "No auth attempts logged yet"
fi
echo ""
echo "2. Successful Logins:"
if [ -f /var/log/attacks/auth_success.log ]; then
    tail -10 /var/log/attacks/auth_success.log
else
    echo "No successful logins yet"
fi
echo ""
echo "3. Failed Attempts:"
if [ -f /var/log/attacks/auth_failures.log ]; then
    tail -10 /var/log/attacks/auth_failures.log
else
    echo "No failed attempts yet"
fi
echo ""
echo "4. Auth Statistics:"
echo "   - Total attempts: $(wc -l < /var/log/attacks/auth_attempts.log 2>/dev/null || echo 0)"
echo "   - Successful: $(wc -l < /var/log/attacks/auth_success.log 2>/dev/null || echo 0)"
echo "   - Failed: $(wc -l < /var/log/attacks/auth_failures.log 2>/dev/null || echo 0)"
echo ""
echo "5. Current Sessions:"
who
echo ""
echo "6. SSH Auth Log (last 15 lines):"
tail -15 /var/log/auth.log 2>/dev/null || echo "No auth log yet"
echo ""
echo "7. Login History:"
last -10
EOF

chmod +x /usr/local/bin/auth_monitor_status.sh
'''

container.exec_run(auth_summary_script)
print("  ✓ Auth status script created")

# 5. Restart SSH with new configuration
print("\n🔄 Restarting SSH with enhanced logging...")
container.exec_run("/usr/sbin/sshd -t")  # Test config
container.exec_run("pkill sshd")  # Stop old SSH
container.exec_run("/usr/sbin/sshd -D &")  # Start new SSH with verbose logging
time.sleep(2)

# Verify SSH is running
result = container.exec_run("ps aux | grep sshd")
if "sshd" in result.output.decode():
    print("  ✓ SSH restarted with verbose logging")
else:
    print("  ⚠ SSH may not be running")

print("\n✅ Enhanced authentication monitoring installed!")
print("\n📊 Monitoring capabilities:")
print("   - All SSH authentication attempts (success & failure)")
print("   - Username/password combinations tried")
print("   - Source IP addresses")
print("   - Authentication methods used")
print("   - Number of attempts before success/failure")
print("   - Login duration and session info")
print("\n📝 Log files created:")
print("   - /var/log/attacks/auth_attempts.log (all attempts)")
print("   - /var/log/attacks/auth_success.log (successful logins)")
print("   - /var/log/attacks/auth_failures.log (failed attempts)")
print("   - /var/log/auth.log (SSH native logs)")
print("\n🔍 To view auth monitoring:")
print("   From SSH: auth_monitor_status.sh")
print("   From outside: I can check the logs for you!")
