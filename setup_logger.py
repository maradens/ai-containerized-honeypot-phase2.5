#!/usr/bin/env python3
import docker

client = docker.from_env()
container = client.containers.get("honeypot-manual-test")

# Create the logger script content
logger_script = """#!/bin/bash
# Command Logger for Honeypot
mkdir -p /var/log/attacks 2>/dev/null
if [ -n "$BASH_COMMAND" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S')|$(whoami)|$BASH_COMMAND" >> /var/log/attacks/command_log
fi
"""

# Write logger script
with open('/tmp/logger.sh', 'w') as f:
    f.write(logger_script)

# Copy to container
import tarfile
import io

buffer = io.BytesIO()
with tarfile.open(fileobj=buffer, mode='w') as tar:
    tar.add('/tmp/logger.sh', arcname='.bash_command_logger')
buffer.seek(0)

container.put_archive('/root', buffer.read())
container.exec_run('chmod +x /root/.bash_command_logger')

# Add to .bashrc
container.exec_run('echo "# Command Logger" >> /root/.bashrc')
container.exec_run('echo "[ -x /root/.bash_command_logger ] && . /root/.bash_command_logger" >> /root/.bashrc')

print("✅ Logger setup complete!")
print("📝 Please reconnect via SSH and run commands.")
print("🔍 Then I'll check the logs.")
