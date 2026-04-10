#!/usr/bin/env python3
"""
Continue fake files injection - with proper directory handling
"""

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

def inject_more_files():
    client = docker.from_env()
    container = client.containers.get("honeypot-manual-test")
    
    print("📁 Continuing fake files injection...")
    
    # Nginx config
    nginx_config = '''user  www-data;
worker_processes  4;
events { worker_connections  1024; }
http {
    upstream backend_servers {
        server 10.0.1.10:8000;
        server 10.0.1.11:8000;
    }
    upstream redis_servers {
        server 10.0.2.10:6379;
    }
    server {
        listen 80;
        server_name example.com;
        location /admin { proxy_pass http://backend_servers; }
        location /api { proxy_pass http://backend_servers; }
    }
}
'''
    
    with open('/tmp/nginx.conf', 'w') as f:
        f.write(nginx_config)
    
    container.exec_run("mkdir -p /etc/nginx")
    tar_data = create_tar_archive('/tmp/nginx.conf', 'nginx.conf')
    container.put_archive('/etc/nginx', tar_data)
    print("  ✓ nginx.conf")
    
    # .htpasswd
    htpasswd = '''admin:$apr1$fA9q2xL9$abc123def456ghi789
developer:$apr1$xY7z8wV6$uvw123xyz789abc4
'''
    
    with open('/tmp/htpasswd', 'w') as f:
        f.write(htpasswd)
    tar_data = create_tar_archive('/tmp/htpasswd', '.htpasswd')
    container.put_archive('/etc/nginx', tar_data)
    print("  ✓ .htpasswd")
    
    # Deployment scripts
    deploy_sh = '''#!/bin/bash
echo "Deploying..."
docker-compose up -d
kubectl apply -f k8s/
'''
    
    with open('/tmp/deploy.sh', 'w') as f:
        f.write(deploy_sh)
    container.exec_run("mkdir -p /home/deploy")
    tar_data = create_tar_archive('/tmp/deploy.sh', 'deploy.sh')
    container.put_archive('/home/deploy', tar_data)
    container.exec_run("chmod +x /home/deploy/deploy.sh")
    print("  ✓ deploy.sh")
    
    # Docker compose
    docker_compose = '''version: '3.8'
services:
  web:
    image: myapp:latest
    ports:
      - "80:80"
    environment:
      - DB_PASSWORD=${DB_PASSWORD}
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword123
  redis:
    image: redis:6-alpine
    command: redis-server --requirepass redispassword123
'''
    
    with open('/tmp/docker-compose.yml', 'w') as f:
        f.write(docker_compose)
    tar_data = create_tar_archive('/tmp/docker-compose.yml', 'docker-compose.yml')
    container.put_archive('/home/deploy', tar_data)
    print("  ✓ docker-compose.yml")
    
    # Kubernetes manifest
    k8s_yaml = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: production-app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:v2.4.1
        env:
        - name: DB_PASSWORD
          value: cm9vdHBhc3N3b3JkMTIz
---
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: cm9vdHBhc3N3b3JkMTIz
'''
    
    with open('/tmp/deployment.yaml', 'w') as f:
        f.write(k8s_yaml)
    container.exec_run("mkdir -p /home/deploy/k8s")
    tar_data = create_tar_archive('/tmp/deployment.yaml', 'deployment.yaml')
    container.put_archive('/home/deploy/k8s', tar_data)
    print("  ✓ k8s/deployment.yaml")
    
    # Fake log file
    fake_log = '''Apr 10 08:15:23 honeypot sshd[12345]: Failed password for root from 185.220.101.1 port 12345 ssh2
Apr 10 08:20:00 honeypot sshd[12400]: Accepted password for admin from 192.168.1.100 port 54321 ssh2
Apr 10 08:25:00 honeypot sshd[12500]: Failed password for root from 103.75.201.5 port 33445 ssh2
'''
    
    with open('/tmp/auth.log.fake', 'w') as f:
        f.write(fake_log)
    container.exec_run("mkdir -p /var/log")
    tar_data = create_tar_archive('/tmp/auth.log.fake', 'auth.log.fake')
    container.put_archive('/var/log', tar_data)
    print("  ✓ auth.log.fake")
    
    print("\n✅ Enhanced files injection complete!")
    print("\n🔍 You can now check:")
    print("   cat /etc/nginx/nginx.conf")
    print("   cat /etc/nginx/.htpasswd")
    print("   cat /home/deploy/docker-compose.yml")
    print("   cat /home/deploy/k8s/deployment.yaml")
    print("   cat /var/log/auth.log.fake")

if __name__ == "__main__":
    inject_more_files()
