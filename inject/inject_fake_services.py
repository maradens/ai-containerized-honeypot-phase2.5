#!/usr/bin/env python3
"""
Fake Services Injector - Simple version using file copies
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

def inject_services():
    client = docker.from_env()
    container = client.containers.get(get_config()["container_name"])
    
    print("🎭 Injecting fake services...")
    
    # Fake MySQL command
    mysql_script = """#!/bin/bash
echo "mysql Ver 8.0.36-0ubuntu0.20.04.1 for Linux (x86_64) using EditLine wrapper"
echo "Copyright (c) 2000, 2023, Oracle and/or its affiliates."
echo "All Rights Reserved."
echo ""
echo "Usage: mysql [OPTIONS] database_name"
echo ""
echo "Example: mysql -u root -p"
"""
    
    with open('/tmp/mysql_fake', 'w') as f:
        f.write(mysql_script)
    
    # Fake netstat
    netstat_script = """#!/bin/bash
echo "Active Internet connections (w/o servers)"
echo ""
echo "Proto Recv-Q Send-Q Local Address           Foreign Address         State"
echo "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN"
echo "tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN"
echo "tcp        0      0 0.0.0.0:443             0.0.0.0:*               LISTEN"
echo "tcp        0      0 0.0.0.0:3306            0.0.0.0:*               LISTEN"
echo "tcp        0      0 0.0.0.0:6379            0.0.0.0:*               LISTEN"
echo "tcp        0      0 0.0.0.0:5432            0.0.0.0:*               LISTEN"
echo "tcp        0      0 0.0.0.0:27017           0.0.0.0:*               LISTEN"
echo "tcp        0      0 127.0.0.1:8080          0.0.0.0:*               LISTEN"
"""
    
    with open('/tmp/netstat_fake', 'w') as f:
        f.write(netstat_script)
    
    # Fake ps
    ps_script = """#!/bin/bash
if [ "$1" = "aux" ] || [ -z "$1" ]; then
    echo "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND"
    echo "root         1  0.0  0.1  16544  3200 ?        Ss   13:55   0:00 /sbin/init"
    echo "root       123  0.0  0.2 224568 45632 ?        Ss   13:55   0:00 /usr/sbin/sshd -D"
    echo "root       234  0.1  0.3 567890 67890 ?        S    13:55   0:01 /usr/sbin/mysqld"
    echo "root       345  0.0  0.2 345678 34567 ?        S    13:55   0:00 /usr/sbin/nginx"
    echo "root       456  0.0  0.1 234567 23456 ?        S    13:55   0:00 /usr/bin/redis-server 0.0.0.0:6379"
    echo "postgres   567  0.0  0.2 456789 45678 ?        Ss   13:55   0:00 /usr/lib/postgresql/14/bin/postgres"
    echo "mongodb    678  0.1  0.4 678901 67890 ?        Ss   13:55   0:02 /usr/bin/mongod"
    echo "www-data   789  0.0  0.1 123456 12345 ?        S    13:55   0:00 php-fpm: pool www"
    echo "root       890  0.0  0.0  98765  9876 ?        Ss   13:55   0:00 /usr/sbin/cron"
    echo "admin      991  0.0  0.1  87654  8765 pts/0    Ss   14:23   0:00 -bash"
else
    /bin/ps "$@"
fi
"""
    
    with open('/tmp/ps_fake', 'w') as f:
        f.write(ps_script)
    
    # Copy files to container
    files = [
        ('/tmp/mysql_fake', '/usr/local/bin/mysql'),
        ('/tmp/netstat_fake', '/usr/local/bin/netstat'),
        ('/tmp/ps_fake', '/usr/local/bin/ps'),
    ]
    
    for src, dest in files:
        tar_data = create_tar_archive(src, os.path.basename(dest))
        container.put_archive(os.path.dirname(dest), tar_data)
        container.exec_run(f"chmod +x {dest}")
        print(f"  ✓ {os.path.basename(dest)} installed")
    
    # Create fake web content (skipped - directories not in minimal container)
    # web_content = {
    #     '/var/www/html/admin/index.html': '<html><head><title>Admin Panel</title></head><body><h1>Admin Panel</h1><p>Server: production-01</p><p>Version: 2.4.1</p></body></html>',
    #     '/var/www/html/api/status.json': '{"status":"ok","server":"production-01","version":"2.4.1","services":{"database":"connected","redis":"connected"},"users":1247}',
    # }
    #
    # for path, content in web_content.items():
    #     with open('/tmp/web_file', 'w') as f:
    #         f.write(content)
    #     tar_data = create_tar_archive('/tmp/web_file', os.path.basename(path))
    #     container.put_archive(os.path.dirname(path), tar_data)
    #     print(f"  ✓ {os.path.basename(path)} created")
    print("  ⚠ Web content skipped (no web directories)")
    
    # Create fake cron jobs
    cron_content = """# Fake cron jobs
*/5 * * * * /usr/local/bin/backup.sh
0 * * * * /usr/local/bin/log_rotate.sh
30 2 * * * /usr/local/bin/security_scan.sh
"""
    
    with open('/tmp/cron_fake', 'w') as f:
        f.write(cron_content)
    
    container.exec_run(f"cat /tmp/cron_fake >> /etc/crontab 2>/dev/null || echo '{cron_content}' >> /etc/crontab")
    print("  ✓ Fake cron jobs added")
    
    print("\n✅ Fake services injection complete!")
    print("\n📝 Test these commands in your SSH session:")
    print("   mysql -u root -p")
    print("   netstat -tulpn")
    print("   ps aux")
    print("   crontab -l")

if __name__ == "__main__":
    inject_services()
