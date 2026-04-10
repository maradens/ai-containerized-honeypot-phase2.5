#!/usr/bin/env python3
"""
Fake Data Injector - Phase 2
Injects realistic fake data into honeypot containers to attract attackers
"""

import docker
import os
import random
import string
from datetime import datetime, timedelta
import json

class FakeDataInjector:
    def __init__(self, container_name="honeypot-manual-test"):
        self.client = docker.from_env()
        self.container = self.client.containers.get(container_name)
        print(f"🎭 Fake Data Injector initialized for: {container_name}")
        
    def inject_fake_users(self):
        """Create fake user accounts with realistic profiles"""
        print("\n👥 Creating fake users...")
        
        users = [
            ("developer", "Dev@123456", "/home/developer", "software developer"),
            ("admin", "Admin@2024", "/home/admin", "system administrator"),
            ("webmaster", "Web@Master123", "/home/webmaster", "web administrator"),
            ("backup", "Backup@2024", "/home/backup", "backup service"),
            ("deploy", "Deploy@123", "/home/deploy", "deployment service"),
        ]
        
        for username, password, home_dir, description in users:
            try:
                # Create user
                self.container.exec_run(f"useradd -m -s /bin/bash -d {home_dir} {username} 2>/dev/null || true")
                # Set password
                self.container.exec_run(f'echo "{username}:{password}" | chpasswd')
                # Add admin to sudo
                if username in ["admin", "developer"]:
                    self.container.exec_run(f"usermod -aG sudo {username}")
                
                print(f"  ✓ Created {username} ({description})")
                
            except Exception as e:
                print(f"  ⚠ Error creating {username}: {e}")
                
    def inject_ssh_keys(self):
        """Create fake SSH keys that look real"""
        print("\n🔑 Creating fake SSH keys...")
        
        # RSA private key (fake but realistic format)
        fake_rsa_key = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBxK8J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5AAAAdgAAACBxK
8J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5J5AAAAC3NzaC1lZDI1NTE5AAAAIBFq
ZmJhc2RmZ2hqa2xsem5vcHFyc3R1dnd4eXoxMjM0NTY3ODkwYWJjZGVmZ2hqa2xzbm9wcXJz
dHV2d3h5ejAxMjM0NTY3ODkwYWJjZGVmZ2hqa2xzbm9wcXJzdHV2d3h5ejAxMjM0NTY3ODkw
YWJjZGVmZ2hqa2xzbm9wcXJzdHV2d3h5ejAxMjM0NQAAAEC
-----END OPENSSH PRIVATE KEY-----
"""
        
        # Create .ssh directories and keys
        for user in ["root", "admin", "developer"]:
            ssh_dir = f"/home/{user}/.ssh" if user != "root" else "/root/.ssh"
            
            self.container.exec_run(f"mkdir -p {ssh_dir}")
            self.container.exec_run(f"echo '{fake_rsa_key}' > {ssh_dir}/id_rsa")
            self.container.exec_run(f"chmod 700 {ssh_dir}")
            self.container.exec_run(f"chmod 600 {ssh_dir}/id_rsa")
            
            # Create public key
            pub_key = f"ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFakePublicKeyFor{user}@localhost {user}@localhost"
            self.container.exec_run(f"echo '{pub_key}' > {ssh_dir}/id_rsa.pub")
            self.container.exec_run(f"chmod 644 {ssh_dir}/id_rsa.pub")
            
            # Add to authorized_keys
            self.container.exec_run(f"echo '{pub_key}' >> {ssh_dir}/authorized_keys")
            self.container.exec_run(f"chmod 644 {ssh_dir}/authorized_keys")
            
            print(f"  ✓ Created SSH keys for {user}")
            
    def inject_aws_credentials(self):
        """Create fake AWS credentials"""
        print("\n☁️  Creating fake AWS credentials...")
        
        aws_creds = """[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region = us-east-1
output = json

[profile production]
aws_access_key_id = AKIAIOSFODNN7PRODKEY
aws_secret_access_key = productionSecretKey123456789EXAMPLE
region = us-west-2
output = json

[profile staging]
aws_access_key_id = AKIAIOSFODNN7STAGING
aws_secret_access_key = stagingSecretKey987654321EXAMPLE
region = eu-west-1
output = json
"""
        
        for user in ["root", "admin", "developer", "deploy"]:
            cred_path = f"/home/{user}/.aws/credentials" if user != "root" else "/root/.aws/credentials"
            self.container.exec_run(f"mkdir -p {os.path.dirname(cred_path)}")
            self.container.exec_run(f"echo '{aws_creds}' > {cred_path}")
            self.container.exec_run(f"chmod 600 {cred_path}")
            
        print(f"  ✓ Created AWS credentials for multiple users")
        
    def inject_env_files(self):
        """Create fake .env files with sensitive data"""
        print("\n📝 Creating fake .env files...")
        
        # Development environment
        dev_env = """# Development Environment Configuration
NODE_ENV=development
DEBUG=true

# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=app_production
DB_USER=admin
DB_PASS=SuperSecret123!
DB_ROOT_PASS=rootpassword456

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redispassword123

# API Keys
API_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz
API_SECRET=secret_abcdefghijklmnopqrstuvwxyz123456
STRIPE_SECRET_KEY=sk_test_1234567890abcdefghijklmnop
STRIPE_PUBLISHABLE_KEY=pk_test_1234567890abcdefghijklmnop

# JWT
JWT_SECRET=your-256-bit-secret-key-here-do-not-share
JWT_EXPIRES_IN=24h

# AWS
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
AWS_S3_BUCKET=production-bucket

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASS=emailpassword123

# Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin@123456
"""
        
        # Web app config
        web_app_dir = "/var/www/html"
        self.container.exec_run(f"mkdir -p {web_app_dir}")
        self.container.exec_run(f"echo '{dev_env}' > {web_app_dir}/.env")
        self.container.exec_run(f"chmod 644 {web_app_dir}/.env")
        
        # Create in home directories too
        for user in ["admin", "developer"]:
            env_path = f"/home/{user}/.env"
            self.container.exec_run(f"echo '{dev_env}' > {env_path}")
            self.container.exec_run(f"chmod 600 {env_path}")
            
        print(f"  ✓ Created .env files")
        
    def inject_database_configs(self):
        """Create fake database configuration files"""
        print("\n🗄️  Creating fake database configs...")
        
        # MySQL config with fake credentials
        mysql_config = """[mysqld]
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
default-authentication-plugin=mysql_native_password

# Fake credentials stored in config (attackers love this!)
root_password=rootpassword456
admin_password=Admin@2024
"""
        
        self.container.exec_run(f"mkdir -p /etc/mysql")
        self.container.exec_run(f"echo '{mysql_config}' > /etc/mysql/my.cnf")
        self.container.exec_run(f"chmod 644 /etc/mysql/my.cnf")
        
        # PostgreSQL config
        postgres_config = """# PostgreSQL configuration file
listen_addresses = 'localhost'
port = 5432
max_connections = 100
shared_buffers = 128MB
dynamic_shared_memory_type = posix

# Authentication
password_encryption = md5

# Fake admin credentials
# admin:postgres123
# backup:backup456
"""
        
        self.container.exec_run(f"mkdir -p /etc/postgresql/14/main")
        self.container.exec_run(f"echo '{postgres_config}' > /etc/postgresql/14/main/postgresql.conf")
        self.container.exec_run(f"chmod 644 /etc/postgresql/14/main/postgresql.conf")
        
        print(f"  ✓ Created database configs (MySQL, PostgreSQL)")
        
    def inject_git_credentials(self):
        """Create fake Git credentials"""
        print("\n📦 Creating fake Git credentials...")
        
        git_credential_helper = """https://oauth2:ghp_1234567890abcdefghijklmnopqrstuvwxyz@github.com
https://x-access-token:github_pat_1234567890abcdefghijklmnopqrstuvwxyz@github.com
https://oauth2:glpat-1234567890abcdefghijklmnopqrstuvwxyz@gitlab.com
"""
        
        git_config = """[user]
    name = Admin User
    email = admin@example.com
[credential]
    helper = store
[core]
    sshCommand = ssh -i /root/.ssh/id_rsa
"""
        
        for user in ["root", "admin", "developer", "git"]:
            home = f"/home/{user}" if user != "root" else "/root"
            
            self.container.exec_run(f"echo '{git_credential_helper}' > {home}/.git-credentials")
            self.container.exec_run(f"chmod 600 {home}/.git-credentials")
            
            self.container.exec_run(f"mkdir -p {home}/.gitconfig 2>/dev/null || true")
            self.container.exec_run(f"echo '{git_config}' > {home}/.gitconfig")
            self.container.exec_run(f"chmod 644 {home}/.gitconfig")
            
        print(f"  ✓ Created Git credentials")
        
    def inject_kubernetes_config(self):
        """Create fake Kubernetes configuration"""
        print("\n☸️  Creating fake Kubernetes config...")
        
        kube_config = """apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUR...
    server: https://192.168.1.100:6443
  name: production-cluster
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUR...
    server: https://10.0.0.1:6443
  name: staging-cluster
contexts:
- context:
    cluster: production-cluster
    namespace: default
    user: admin-cluster
  name: admin@production-cluster
- context:
    cluster: staging-cluster
    namespace: dev
    user: dev-user
  name: dev@staging-cluster
current-context: admin@production-cluster
kind: Config
preferences: {}
users:
- name: admin-cluster
  user:
    token: eyJhbGciOiJSUzI1NiIsImtpZCI6IkZaVlUyTDFN...
- name: dev-user
  user:
    token: eyJhbGciOiJSUzI1NiIsImtpZCI6IkZaVlUyTDFN...
"""
        
        for user in ["root", "admin", "developer", "deploy"]:
            home = f"/home/{user}" if user != "root" else "/root"
            self.container.exec_run(f"mkdir -p {home}/.kube")
            self.container.exec_run(f"echo '{kube_config}' > {home}/.kube/config")
            self.container.exec_run(f"chmod 600 {home}/.kube/config")
            
        print(f"  ✓ Created Kubernetes configs")
        
    def inject_bash_history(self):
        """Create fake bash history to look realistic"""
        print("\n📜 Creating fake bash history...")
        
        fake_history = """ls
cd /root
cat /etc/passwd
sudo su
ps aux
netstat -tulpn
cat /etc/shadow
find / -name "*.key"
find / -name "*.pem"
find / -name "id_rsa"
cat ~/.ssh/id_rsa
cat ~/.aws/credentials
cat /var/www/html/.env
mysql -u root -p
mysql> use database;
mysql> show tables;
mysql> select * from users;
redis-cli
redis> get password
docker ps
docker exec -it container /bin/bash
kubectl get pods
kubectl get secrets
aws s3 ls
aws ec2 describe-instances
git clone https://github.com/company/secret-project.git
npm install
npm run build
python manage.py migrate
crontab -l
history
clear
exit
"""
        
        for user in ["root", "admin", "developer"]:
            history_file = f"/home/{user}/.bash_history" if user != "root" else "/root/.bash_history"
            self.container.exec_run(f"echo '{fake_history}' >> {history_file}")
            self.container.exec_run(f"chmod 644 {history_file}")
            
        print(f"  ✓ Created bash history")
        
    def inject_fake_logs(self):
        """Create fake system logs"""
        print("\n📝 Creating fake system logs...")
        
        # Auth log with fake login attempts
        auth_log = """Apr  8 10:23:45 honeypot sshd[1234]: Accepted password for admin from 192.168.1.100 port 54321 ssh2
Apr  8 10:24:00 honeypot sshd[1235]: Accepted password for root from 10.0.0.50 port 12345 ssh2
Apr  8 10:25:15 honeypot sudo: admin : TTY=pts/0 ; PWD=/home/admin ; USER=root ; COMMAND=/bin/bash
Apr  8 10:30:22 honeypot sshd[1236]: Failed password for invalid user test from 203.0.113.42 port 33445 ssh2
Apr  8 10:30:25 honeypot sshd[1237]: Failed password for invalid user administrator from 203.0.113.42 port 33446 ssh2
Apr  8 10:30:28 honeypot sshd[1238]: Failed password for root from 198.51.100.1 port 33447 ssh2
Apr  8 10:31:00 honeypot sshd[1239]: Accepted publickey for developer from 172.16.0.10 port 44556 ssh2
Apr  8 11:00:00 honeypot CRON[2345]: (root) CMD (/usr/local/bin/backup.sh)
Apr  8 12:00:00 honeypot sshd[3456]: Accepted password for webmaster from 192.168.1.150 port 55667 ssh2
"""
        
        self.container.exec_run(f"mkdir -p /var/log")
        self.container.exec_run(f"echo '{auth_log}' >> /var/log/auth.log")
        self.container.exec_run(f"chmod 644 /var/log/auth.log")
        
        print(f"  ✓ Created fake auth logs")
        
    def create_fake_files(self):
        """Create various fake files that attackers look for"""
        print("\n📁 Creating fake files...")
        
        # Create backup files
        backup_files = {
            "/root/backup.sql": "CREATE DATABASE app; USE app; CREATE TABLE users (id INT, username VARCHAR(50), password VARCHAR(255)); INSERT INTO users VALUES (1, 'admin', 'password123');",
            "/home/admin/config.bak": "DB_PASSWORD=admin123\nAPI_KEY=secretkey456",
            "/tmp/debug.log": "[DEBUG] Password: admin123\n[DEBUG] API Key: secret123",
            "/var/www/html/wp-config.php": "<?php define('DB_PASSWORD', 'wordpress123'); ?>",
            "/home/developer/.npmrc": "//registry.npmjs.org/:_authToken=npm_token_123456789",
        }
        
        for filepath, content in backup_files.items():
            self.container.exec_run(f"mkdir -p {os.path.dirname(filepath)}")
            self.container.exec_run(f"echo '{content}' > {filepath}")
            
        print(f"  ✓ Created {len(backup_files)} fake files")
        
    def inject_all(self):
        """Run all injection methods"""
        print("\n" + "="*60)
        print("🎭 STARTING FAKE DATA INJECTION")
        print("="*60)
        
        self.inject_fake_users()
        self.inject_ssh_keys()
        self.inject_aws_credentials()
        self.inject_env_files()
        self.inject_database_configs()
        self.inject_git_credentials()
        self.inject_kubernetes_config()
        self.inject_bash_history()
        self.inject_fake_logs()
        self.create_fake_files()
        
        print("\n" + "="*60)
        print("✅ FAKE DATA INJECTION COMPLETE!")
        print("="*60)
        print("\n🎯 The honeypot now contains:")
        print("   - 6 fake user accounts")
        print("   - SSH keys for multiple users")
        print("   - AWS credentials (3 profiles)")
        print("   - Environment files with secrets")
        print("   - Database configs (MySQL, PostgreSQL)")
        print("   - Git credentials (GitHub, GitLab)")
        print("   - Kubernetes configs")
        print("   - Fake bash history")
        print("   - Fake system logs")
        print("   - Backup files and debug logs")
        print("\n🐝 Your honeypot is now much more realistic!")


if __name__ == "__main__":
    import sys
    
    container_name = sys.argv[1] if len(sys.argv) > 1 else "honeypot-manual-test"
    
    injector = FakeDataInjector(container_name)
    injector.inject_all()
