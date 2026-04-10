#!/usr/bin/env python3
"""
Manual test script - creates honeypot step by step for debugging
"""

import docker
import time

print("🚀 Starting manual honeypot creation...")

# Connect to Docker
client = docker.from_env()
print(f"✓ Docker connected (version: {client.version()['Version']})")

# Create container
print("\n📦 Creating container...")
container = client.containers.run(
    "ubuntu:22.04",
    command=["/bin/bash", "-c", "while true; do sleep 1; done"],
    name="honeypot-manual-test",
    ports={22: 2225},
    detach=True
)
print(f"✓ Container created: {container.name}")
print(f"  Status: {container.status}")

# Wait for container to be ready
time.sleep(2)

# Install SSH
print("\n⚙️  Installing SSH...")
result = container.exec_run("apt update && apt install -y openssh-server", demux=True)
print(f"  Exit code: {result.exit_code}")
if result.exit_code != 0:
    print(f"  Error: {result.output[1][:200] if result.output[1] else 'No error output'}")

# Configure SSH
print("\n⚙️  Configuring SSH...")
container.exec_run("mkdir -p /var/run/sshd")
container.exec_run('echo "root:password123" | chpasswd')
container.exec_run('sed -i "s/#PermitRootLogin.*/PermitRootLogin yes/" /etc/ssh/sshd_config')
container.exec_run('sed -i "s/#PasswordAuthentication.*/PasswordAuthentication yes/" /etc/ssh/sshd_config')

# Start SSH
print("\n🚀 Starting SSH...")
result = container.exec_run("/usr/sbin/sshd", demux=True)
print(f"  Exit code: {result.exit_code}")

# Verify SSH is running
print("\n🔍 Verifying SSH...")
result = container.exec_run("ps aux | grep sshd", demux=True)
output = result.output[0].decode() if result.output[0] else ""
print(f"  Process list:\n{output}")

# Check if port is listening
result = container.exec_run("netstat -tlnp | grep 22 || ss -tlnp | grep 22", demux=True)
output = result.output[0].decode() if result.output[0] else ""
print(f"  Port 22 status:\n{output if output else 'Port not listening'}")

print(f"\n✅ Manual setup complete!")
print(f"   Container: {container.name}")
print(f"   Port: 2225")
print(f"\n   Try: ssh root@localhost -p 2225")
print(f"   Password: password123")
print(f"\nContainer will stay up for testing...")
print(f"   To stop: docker stop {container.name}")

# Keep script alive
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("\n\nStopping container...")
    container.stop()
    container.remove()
