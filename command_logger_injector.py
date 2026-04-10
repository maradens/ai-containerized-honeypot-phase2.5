#!/usr/bin/env python3
"""
Command Logger Injector - Enables comprehensive command logging
"""

import docker
import os

def inject_command_logging():
    client = docker.from_env()
    container = client.containers.get("honeypot-manual-test")
    
    print("📝 Injecting command logging system...")
    
    # 1. Create log directory
    container.exec_run("mkdir -p /var/log/attacks")
    print("  ✓ Created log directory")
    
    # 2. Copy command logging script
    script_path = "/home/maradens/.openclaw/workspace/ai-honeypot-phase1/scripts/command_logging.sh"
    container.put_archive("/tmp", create_tar_archive(script_path, "command_logging.sh"))
    container.exec_run("chmod +x /tmp/command_logging.sh")
    print("  ✓ Copied command logging script")
    
    # 3. Install command logging in .bashrc for all users
    bashrc_addition = """
# == COMMAND LOGGING ==
# Log every command to database
export PROMPT_COMMAND='echo "$(date +"%Y-%m-%d %H:%M:%S")|$(whoami)|$(history 1 | sed "s/^[ ]*[0-9][0-9]*[ ]*//")" >> /var/log/attacks/command_log 2>/dev/null'

# Also log to JSON format for easy parsing
export PREEXEC_CMD='echo "$(date +"%Y-%m-%d %H:%M:%S")|$(whoami)|$HISTCMD|$(history 1)" >> /var/log/attacks/command_log'

# Initialize log file
touch /var/log/attacks/command_log
chmod 644 /var/log/attacks/command_log
"""
    
    for user in ["root", "admin", "developer", "webmaster"]:
        bashrc_path = f"/home/{user}/.bashrc" if user != "root" else "/root/.bashrc"
        container.exec_run(f"echo '{bashrc_addition}' >> {bashrc_path}")
        print(f"  ✓ Added logging to {user}'s .bashrc")
    
    # 4. Create command analyzer script
    analyzer_script = '''#!/bin/bash
echo "=== COMMAND LOG ANALYZER ==="
echo ""
echo "1. Total Commands Logged:"
wc -l /var/log/attacks/command_log 2>/dev/null || echo "0"
echo ""
echo "2. Recent Commands (Last 20):"
tail -20 /var/log/attacks/command_log 2>/dev/null || echo "No commands yet"
echo ""
echo "3. Commands by User:"
cut -d'|' -f2 /var/log/attacks/command_log 2>/dev/null | sort | uniq -c | sort -rn
echo ""
echo "4. Most Common Commands:"
cut -d'|' -f4 /var/log/attacks/command_log 2>/dev/null | sort | uniq -c | sort -rn | head -20
echo ""
echo "5. Suspicious Commands:"
grep -iE "password|secret|key|token|credential|ssh|aws|git|docker|kubectl|mysql|psql" /var/log/attacks/command_log 2>/dev/null | tail -10 || echo "None found"
echo ""
echo "6. File Access Commands:"
grep -iE "cat |less |more |head |tail |vim |nano " /var/log/attacks/command_log 2>/dev/null | tail -10 || echo "None found"
'''
    
    container.exec_run("echo '#!/bin/bash' > /usr/local/bin/analyze_commands.sh")
    container.exec_run(f"echo '{analyzer_script[8:]}' >> /usr/local/bin/analyze_commands.sh")
    container.exec_run("chmod +x /usr/local/bin/analyze_commands.sh")
    print("  ✓ Created command analyzer script")
    
    # 5. Initialize log file
    container.exec_run("touch /var/log/attacks/command_log")
    container.exec_run("chmod 644 /var/log/attacks/command_log")
    print("  ✓ Initialized log file")
    
    print("\n✅ Command logging system installed!")
    print("\n📊 To analyze commands:")
    print("   From SSH: analyze_commands.sh")
    print("   From outside: python attack_logger.py scan-commands")
    print("\n📝 Logs location: /var/log/attacks/command_log")
    
def create_tar_archive(file_path, arcname=None):
    """Create a tar archive from a file"""
    import tarfile
    import io
    
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
        tar.add(file_path, arcname=arcname or os.path.basename(file_path))
    tar_buffer.seek(0)
    return tar_buffer.read()

if __name__ == "__main__":
    inject_command_logging()
