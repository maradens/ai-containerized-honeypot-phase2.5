#!/usr/bin/env python3
from honeypot_config import get_config
import docker

client = docker.from_env()
container = client.containers.get(get_config()["container_name"])

# Read current bashrc
result = container.exec_run("cat /etc/bash.bashrc")
content = result.output.decode()

# Remove old logger lines
lines = content.split('\n')
new_lines = []
skip_until_end = False
for line in lines:
    if '# Honeypot Command Logger' in line:
        skip_until_end = True
        continue
    if skip_until_end:
        if line.strip() and not line.startswith('#'):
            continue
        skip_until_end = False
        new_lines.append(line)
    else:
        new_lines.append(line)

# Add new logger
new_lines.append('')
new_lines.append('# Honeypot Command Logger')
new_lines.append('[ -x /root/.bash_command_logger ] && . /root/.bash_command_logger')

# Write back
new_content = '\n'.join(new_lines)
container.exec_run(f"echo '{new_content}' > /tmp/bashrc_new")
container.exec_run("cp /tmp/bashrc_new /etc/bash.bashrc")

print("✅ /etc/bash.bashrc updated with fixed logger!")
