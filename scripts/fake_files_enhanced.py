#!/usr/bin/env python3
"""
Enhanced Fake Files - Add more realistic content
"""

from honeypot_config import get_config
import docker
import tarfile
import io
import os

def create_tar_archive(file_path, arcname=None):
    """Create a tar archive from a file"""
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
        tar.add(file_path, arcname=arcname or os.path.basename(file_path))
    tar_buffer.seek(0)
    return tar_buffer.read()

def inject_enhanced_files():
    client = docker.from_env()
    container = client.containers.get(get_config()["container_name"])
    
    print("📁 Injecting enhanced fake files...")
    
    # 1. Fake backup scripts
    scripts = {
        '/usr/local/bin/backup.sh': '''#!/bin/bash
# Daily backup script
echo "Starting backup at $(date)"
tar -czf /backup/daily-$(date +%Y%m%d).tar.gz /var/www/html /home/admin
echo "Backup completed"
''',
        '/usr/local/bin/security_scan.sh': '''#!/bin/bash
# Security scan script
echo "Running security scan..."
echo "Checking for vulnerabilities..."
echo "Scanning ports..."
echo "Scan complete - no critical issues found"
''',
        '/usr/local/bin/monitor_services.sh': '''#!/bin/bash
# Service monitoring
for service in mysql redis postgres nginx; do
    if pgrep -x $service > /dev/null; then
        echo "$service: RUNNING"
    else
        echo "$service: DOWN - restarting..."
    fi
done
''',
    }
    
    for path, content in scripts.items():
        with open('/tmp/script', 'w') as f:
            f.write(content)
        tar_data = create_tar_archive('/tmp/script', os.path.basename(path))
        container.put_archive(os.path.dirname(path), tar_data)
        container.exec_run(f"chmod +x {path}")
        print(f"  ✓ {os.path.basename(path)}")
    
    # 2. Fake database dumps
    dumps = {
        '/backup/users_backup.sql': '''-- MySQL dump 10.13  Distrib 8.0.32
-- Host: localhost    Database: production_db
-- 
-- Table structure for table `users`
--
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

--
-- Dumping data for table `users`
--
INSERT INTO `users` VALUES
(1,'admin','admin@example.com','$2y$10$examplehash123456789',NULL),
(2,'user1','user1@example.com','$2y$10$examplehash987654321',NULL),
(3,'developer','dev@example.com','$2y$10$examplehash456789123',NULL),
(4,'testuser','test@example.com','password123',NULL);
''',
        '/backup/api_keys_backup.sql': '''-- MySQL dump for api_keys
--
CREATE TABLE IF NOT EXISTS `api_keys` (
  `id` int NOT NULL AUTO_INCREMENT,
  `service` varchar(50) NOT NULL,
  `api_key` varchar(255) NOT NULL,
  `secret` varchar(255) NOT NULL,
  `expires_at` date DEFAULT NULL,
  PRIMARY KEY (`id`)
);

--
-- Dumping data
--
INSERT INTO `api_keys` VALUES
(1,'Stripe','sk_live_abc123def456ghi789','stripe_secret_xyz789','2026-12-31'),
(2,'AWS','AKIAIOSFODNN7EXAMPLE','wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY','2026-06-30'),
(3,'GitHub','ghp_1234567890abcdefghijklmnopqrstuvwxyz','github_secret_token','2026-09-15'),
(4,'SendGrid','SG.abcdefghijklmnopqrstuvwxyz123456','sendgrid_api_key_secret','2027-01-01');
''',
    }
    
    # Create backup directory
    container.exec_run("mkdir -p /backup")
    
    for path, content in dumps.items():
        with open('/tmp/dump', 'w') as f:
            f.write(content)
        tar_data = create_tar_archive('/tmp/dump', os.path.basename(path))
        container.put_archive('/backup', tar_data)
        print(f"  ✓ {os.path.basename(path)}")
    
    # 3. Fake Nginx config with passwords
    nginx_config = '''# Nginx configuration
user  www-data;
worker_processes  4;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Realistic settings
    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     off;
    keepalive_timeout  65;
    
    # Fake upstream servers (attackers will check these)
    upstream backend_servers {
        server 10.0.1.10:8000;
        server 10.0.1.11:8000;
        server 10.0.1.12:8000;
    }
    
    upstream redis_servers {
        server 10.0.2.10:6379;
        server 10.0.2.11:6379;
    }
    
    server {
        listen 80;
        server_name example.com www.example.com;
        
        # Fake admin panel
        location /admin {
            proxy_pass http://backend_servers;
            proxy_set_header Host $host;
        }
        
        # Fake API endpoint
        location /api {
            proxy_pass http://backend_servers;
            auth_basic "Restricted";
            auth_basic_user_file /etc/nginx/.htpasswd;
        }
        
        # Database status endpoint
        location /db/status {
            stub_status on;
            allow 127.0.0.1;
            deny all;
        }
    }
}
'''
    
    with open('/tmp/nginx.conf', 'w') as f:
        f.write(nginx_config)
    tar_data = create_tar_archive('/tmp/nginx.conf', 'nginx.conf')
    container.put_archive('/etc/nginx', tar_data)
    print(f"  ✓ nginx.conf (with fake upstreams)")
    
    # 4. Fake .htpasswd file
    htpasswd_content = '''admin:$(apr1)$fA9q2xL9$abc123def456ghi789jkl0
developer:$(apr1)$xY7z8wV6$uvw123xyz789abc4
backup:$(apr1)$mN5o4pQ3$mno456pqr789stu0
'''
    
    container.exec_run("mkdir -p /etc/nginx")
    with open('/tmp/htpasswd', 'w') as f:
        f.write(htpasswd_content)
    tar_data = create_tar_archive('/tmp/htpasswd', '.htpasswd')
    container.put_archive('/etc/nginx', tar_data)
    print(f"  ✓ .htpasswd (fake admin passwords)")
    
    # 5. Fake deployment scripts
    deploy_scripts = {
        '/home/deploy/deploy.sh': '''#!/bin/bash
# Deployment script
echo "Deploying application..."
docker-compose up -d
kubectl apply -f k8s/
echo "Deployment complete"
''',
        '/home/deploy/docker-compose.yml': '''version: '3.8'
services:
  web:
    image: myapp:latest
    ports:
      - "80:80"
    environment:
      - DB_PASSWORD=${DB_PASSWORD}
      - API_KEY=${API_KEY}
    depends_on:
      - mysql
      - redis
  
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword123
      - MYSQL_DATABASE=production
    volumes:
      - mysql_data:/var/lib/mysql
  
  redis:
    image: redis:6-alpine
    command: redis-server --requirepass redispassword123
  
volumes:
  mysql_data:
''',
    }
    
    container.exec_run("mkdir -p /home/deploy")
    for path, content in deploy_scripts.items():
        with open('/tmp/deploy', 'w') as f:
            f.write(content)
        tar_data = create_tar_archive('/tmp/deploy', os.path.basename(path))
        container.put_archive(os.path.dirname(path), tar_data)
        container.exec_run(f"chmod +x {path}" if path.endswith('.sh') else f"chmod 644 {path}")
        print(f"  ✓ {os.path.basename(path)}")
    
    # 6. Fake Kubernetes manifests
    k8s_manifest = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: production-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v2.4.1
        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secret
              key: key
---
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: cm9vdHBhc3N3b3JkMTIz  # rootpassword123 in base64
---
apiVersion: v1
kind: Secret
metadata:
  name: api-secret
type: Opaque
data:
  key: c2tfbGl2ZV9hYmMxMjNkZWY0NTY=  # sk_live_abc123def456 in base64
'''
    
    container.exec_run("mkdir -p /home/deploy/k8s")
    with open('/tmp/k8s.yaml', 'w') as f:
        f.write(k8s_manifest)
    tar_data = create_tar_archive('/tmp/k8s.yaml', 'deployment.yaml')
    container.put_archive('/home/deploy/k8s', tar_data)
    print(f"  ✓ k8s/deployment.yaml (with secrets!)")
    
    # 7. Fake log files showing past attacks
    fake_logs = {
        '/var/log/auth.log.fake': '''Apr 10 08:15:23 honeypot sshd[12345]: Failed password for root from 185.220.101.1 port 12345 ssh2
Apr 10 08:15:26 honeypot sshd[12346]: Failed password for admin from 185.220.101.1 port 12346 ssh2
Apr 10 08:15:29 honeypot sshd[12347]: Failed password for root from 185.220.101.1 port 12347 ssh2
Apr 10 08:20:00 honeypot sshd[12400]: Accepted password for admin from 192.168.1.100 port 54321 ssh2
Apr 10 08:20:05 honeypot sudo: admin : TTY=pts/0 ; PWD=/home/admin ; USER=root ; COMMAND=/bin/bash
Apr 10 08:25:00 honeypot sshd[12500]: Failed password for root from 103.75.201.5 port 33445 ssh2
Apr 10 08:30:00 honeypot sshd[12600]: Failed password for root from 45.155.205.233 port 44556 ssh2
Apr 10 08:35:00 honeypot sshd[12700]: Accepted password for developer from 192.168.1.150 port 55667 ssh2
''',
    }
    
    for path, content in fake_logs.items():
        with open('/tmp/log', 'w') as f:
            f.write(content)
        tar_data = create_tar_archive('/tmp/log', os.path.basename(path))
        container.put_archive(os.path.dirname(path), tar_data)
        print(f"  ✓ {os.path.basename(path)}")
    
    print("\n✅ Enhanced fake files injection complete!")
    print("\n📁 Added:")
    print("   • Fake backup scripts (backup.sh, security_scan.sh)")
    print("   • Fake database dumps (users, api_keys)")
    print("   • Fake Nginx config with upstream servers")
    print("   • Fake .htpasswd with admin passwords")
    print("   • Fake deployment scripts (Docker, Kubernetes)")
    print("   • Fake K8s manifests with secrets!")
    print("   • Fake log files with past attack attempts")

if __name__ == "__main__":
    inject_enhanced_files()
