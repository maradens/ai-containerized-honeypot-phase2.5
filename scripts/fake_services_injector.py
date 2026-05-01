#!/usr/bin/env python3
"""
Fake Services Injector - Makes single container appear like a full production server
"""

from honeypot_config import get_config
import docker
import os

class FakeServicesInjector:
    def __init__(self, container_name=get_config()["container_name"]):
        self.client = docker.from_env()
        self.container = self.client.containers.get(container_name)
        print(f"🎭 Fake Services Injector for: {container_name}")
        
    def create_fake_mysql(self):
        """Create fake MySQL command that responds with login prompt"""
        print("\n🗄️  Creating fake MySQL server...")
        
        mysql_fake = '''#!/bin/bash
# Fake MySQL server
echo "mysql Ver 8.0.36-0ubuntu0.20.04.1 for Linux (x86_64) using EditLine wrapper"
echo "Copyright (c) 2000, 2023, Oracle and/or its affiliates."
echo "All Rights Reserved."
echo ""
echo "Usage: mysql [OPTIONS] database_name"
echo ""
echo "Common options:"
echo "  -u, --user=USER         User name"
echo "  -p, --password[=PASS]   Password to use when connecting"
echo "  -h, --host=HOST         Server host name"
echo "  -P, --port=PORT         TCP/IP port"
echo ""
echo "Example: mysql -u root -p production_db"
'''
        
        self.container.exec_run("echo '#!/bin/bash' > /usr/local/bin/mysql")
        self.container.exec_run(f"echo '{mysql_fake[8:]}' >> /usr/local/bin/mysql")
        self.container.exec_run("chmod +x /usr/local/bin/mysql")
        print("  ✓ Fake MySQL created")
        
        # Also create a version that actually responds
        mysql_interactive = '''#!/bin/bash
echo "Welcome to the MySQL monitor.  Commands end with ; or \\g."
echo "Your MySQL connection id is 12345"
echo "Server version: 5.7.42-0ubuntu0.20.04.1 (Ubuntu)"
echo ""
echo "Oracle is a registered trademark of Oracle Corporation and/or its"
echo "affiliates. Other names may be trademarks of their respective owners."
echo ""
echo "Type 'help;' or '\\h' for help. Type '\\c' to clear the current statement."
echo ""
echo "mysql> "
# Fake response for common commands
read -p "mysql> " cmd
case "$cmd" in
    *show*tables*)
        echo "+------------------+";
        echo "| Tables_in_db     |";
        echo "+------------------+";
        echo "| users            |";
        echo "| admin_sessions   |";
        echo "| api_keys         |";
        echo "| credentials      |";
        echo "+------------------+";
        echo "";
        echo "5 rows in set (0.02 sec)";
        echo "";
        echo "mysql> ";
        ;;
    *select*
        echo "+----+----------+------------------+";
        echo "| id | username | password         |";
        echo "+----+----------+------------------+";
        echo "| 1  | admin    | $2y$10$example  |";
        echo "| 2  | user1    | $2y$10$example2 |";
        echo "+----+----------+------------------+";
        echo "";
        echo "2 rows in set (0.01 sec)";
        echo "";
        echo "mysql> ";
        ;;
    *)
        echo "ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)";
        echo "mysql> ";
        ;;
esac
'''
        
        self.container.exec_run("echo '#!/bin/bash' > /usr/local/bin/mysql_interactive")
        self.container.exec_run(f"echo '{mysql_interactive}' >> /usr/local/bin/mysql_interactive")
        self.container.exec_run("chmod +x /usr/local/bin/mysql_interactive")
        
    def create_fake_redis(self):
        """Create fake Redis client"""
        print("  → Creating fake Redis client...")
        
        redis_fake = '''#!/bin/bash
echo "127.0.0.1:6379>"
read -p "127.0.0.1:6379> " cmd
case "$cmd" in
    *GET*|*get*)
        echo "(nil)";
        echo "127.0.0.1:6379>";
        ;;
    *CONFIG*|*config*)
        echo "(error) ERR unknown command 'config', with args beginning with:' ";
        echo "127.0.0.1:6379>";
        ;;
    *INFO*)
        echo "# Server";
        echo "redis_version:6.0.16";
        echo "redis_mode:standalone";
        echo "os:Linux 5.4.0-ubuntu x86_64";
        echo "tcp_port:6379";
        echo "127.0.0.1:6379>";
        ;;
    *)
        echo "(error) ERR unknown command";
        echo "127.0.0.1:6379>";
        ;;
esac
'''
        
        self.container.exec_run("echo '#!/bin/bash' > /usr/local/bin/redis-cli")
        self.container.exec_run(f"echo '{redis_fake}' >> /usr/local/bin/redis-cli")
        self.container.exec_run("chmod +x /usr/local/bin/redis-cli")
        print("  ✓ Fake Redis created")
        
    def create_fake_psql(self):
        """Create fake PostgreSQL client"""
        print("  → Creating fake PostgreSQL client...")
        
        psql_fake = '''#!/bin/bash
echo "psql (14.10 (Ubuntu 14.10-0ubuntu0.22.04.1))"
echo "Type \"help\" for help."
echo "";
echo "postgres=> ";
read -p "postgres=> " cmd
case "$cmd" in
    *\\dt*)
        echo "          List of relations";
        echo " Schema |     Name     | Type  |  Owner   ";
        echo "--------+--------------+-------+----------";
        echo " public | users        | table | postgres ";
        echo " public | sessions     | table | postgres ";
        echo " public | api_keys     | table | postgres ";
        echo "--------+--------------+-------+----------";
        echo "(3 rows)";
        echo "";
        echo "postgres=> ";
        ;;
    *SELECT*)
        echo " id | username |     password_hash      ";
        echo "----+----------+------------------------";
        echo " 1  | admin    | $2b$12$examplehash    ";
        echo " 2  | user1    | $2b$12$examplehash2   ";
        echo "(2 rows)";
        echo "";
        echo "postgres=> ";
        ;;
    *)
        echo "ERROR:  permission denied for table users";
        echo "postgres=> ";
        ;;
esac
'''
        
        self.container.exec_run("echo '#!/bin/bash' > /usr/local/bin/psql")
        self.container.exec_run(f"echo '{psql_fake}' >> /usr/local/bin/psql")
        self.container.exec_run("chmod +x /usr/local/bin/psql")
        print("  ✓ Fake PostgreSQL created")
        
    def create_fake_netstat(self):
        """Override netstat to show fake services"""
        print("  → Creating fake network services...")
        
        # Backup original netstat
        self.container.exec_run("which netstat >/dev/null 2>&1 && cp $(which netstat) /usr/local/bin/netstat.real 2>/dev/null || echo 'netstat not found'")
        
        # Create fake netstat that shows services
        netstat_fake = '''#!/bin/bash
if [ -x /usr/local/bin/netstat.real ]; then
    /usr/local/bin/netstat.real "$@"
else
    # Fake netstat output
    echo "Active Internet connections (w/o servers)";
    echo "";
    echo "Proto Recv-Q Send-Q Local Address           Foreign Address         State";
    echo "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN";
    echo "tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN";
    echo "tcp        0      0 0.0.0.0:443             0.0.0.0:*               LISTEN";
    echo "tcp        0      0 0.0.0.0:3306            0.0.0.0:*               LISTEN";
    echo "tcp        0      0 0.0.0.0:6379            0.0.0.0:*               LISTEN";
    echo "tcp        0      0 0.0.0.0:5432            0.0.0.0:*               LISTEN";
    echo "tcp        0      0 0.0.0.0:27017           0.0.0.0:*               LISTEN";
    echo "tcp        0      0 127.0.0.1:8080          0.0.0.0:*               LISTEN";
    echo "tcp6       0      0 :::22                   :::*                    LISTEN";
    echo "tcp6       0      0 :::80                   :::*                    LISTEN";
    echo "tcp6       0      0 :::443                  :::*                    LISTEN";
    echo "tcp6       0      0 :::3306                 :::*                    LISTEN";
    echo "";
    echo "Active UNIX domain sockets (w/o servers)";
    echo "";
    echo "RefCount Protocol Server Address";
    echo "2      unix  /var/run/mysqld/mysqld.sock";
    echo "2      unix  /var/run/postgresql/.s.PGSQL.5432";
    echo "2      unix  /var/run/redis/redis-server.sock";
fi
'''
        
        self.container.exec_run("echo '#!/bin/bash' > /usr/local/bin/netstat")
        self.container.exec_run(f"echo '{netstat_fake}' >> /usr/local/bin/netstat")
        self.container.exec_run("chmod +x /usr/local/bin/netstat")
        print("  ✓ Fake network services created")
        
    def create_fake_ps(self):
        """Override ps to show fake processes"""
        print("  → Creating fake running processes...")
        
        ps_fake = '''#!/bin/bash
# Show real processes + fake ones
if [ "$1" = "aux" ] || [ "$1" = "-ef" ]; then
    echo "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND";
    echo "root         1  0.0  0.1  16544  3200 ?        Ss   13:55   0:00 /sbin/init";
    echo "root       123  0.0  0.2 224568 45632 ?        Ss   13:55   0:00 /usr/sbin/sshd -D";
    echo "root       234  0.1  0.3 567890 67890 ?        S    13:55   0:01 /usr/sbin/mysqld";
    echo "root       345  0.0  0.2 345678 34567 ?        S    13:55   0:00 /usr/sbin/nginx";
    echo "root       456  0.0  0.1 234567 23456 ?        S    13:55   0:00 /usr/bin/redis-server 0.0.0.0:6379";
    echo "postgres   567  0.0  0.2 456789 45678 ?        Ss   13:55   0:00 /usr/lib/postgresql/14/bin/postgres";
    echo "mongodb    678  0.1  0.4 678901 67890 ?        Ss   13:55   0:02 /usr/bin/mongod";
    echo "www-data   789  0.0  0.1 123456 12345 ?        S    13:55   0:00 php-fpm: pool www";
    echo "root       890  0.0  0.0  98765  9876 ?        Ss   13:55   0:00 /usr/sbin/cron";
    echo "admin      991  0.0  0.1  87654  8765 pts/0    Ss   14:23   0:00 -bash";
    echo "admin      992  0.0  0.0  76543  7654 pts/1    Ss   14:25   0:00 -bash";
else
    /bin/ps "$@"
fi
'''
        
        self.container.exec_run("echo '#!/bin/bash' > /usr/local/bin/ps")
        self.container.exec_run(f"echo '{ps_fake}' >> /usr/local/bin/ps")
        self.container.exec_run("chmod +x /usr/local/bin/ps")
        print("  ✓ Fake processes created")
        
    def create_fake_cron(self):
        """Create fake cron jobs"""
        print("  → Creating fake cron jobs...")
        
        fake_crontab = '''# Fake cron jobs for honeypot
*/5 * * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1
0 * * * * /usr/local/bin/log_rotate.sh >> /var/log/rotate.log 2>&1
30 2 * * * /usr/local/bin/security_scan.sh >> /var/log/security.log 2>&1
0 3 * * 0 /usr/local/bin/weekly_maintenance.sh >> /var/log/maintenance.log 2>&1
*/10 * * * * /usr/local/bin/monitor_services.sh >> /var/log/services.log 2>&1
'''
        
        self.container.exec_run(f"echo '{fake_crontab}' >> /etc/crontab")
        
        # Create fake scripts
        self.container.exec_run("echo '#!/bin/bash' > /usr/local/bin/backup.sh")
        self.container.exec_run("echo 'echo \"Running daily backup...\"' >> /usr/local/bin/backup.sh")
        self.container.exec_run("chmod +x /usr/local/bin/backup.sh")
        
        self.container.exec_run("echo '#!/bin/bash' > /usr/local/bin/log_rotate.sh")
        self.container.exec_run("echo 'echo \"Rotating logs...\"' >> /usr/local/bin/log_rotate.sh")
        self.container.exec_run("chmod +x /usr/local/bin/log_rotate.sh")
        
        print("  ✓ Fake cron jobs created")
        
    def create_fake_curl_responses(self):
        """Create fake responses for curl/wget to localhost"""
        print("  → Creating fake web server responses...")
        
        # Create fake web content
        self.container.exec_run("mkdir -p /var/www/html/admin")
        
        # Fake WordPress login
        wordpress_login = '''<!DOCTYPE html>
<html>
<head><title>WordPress Login</title></head>
<body>
<h1>WordPress</h1>
<form method="post">
    <input type="text" name="log" placeholder="Username"><br>
    <input type="password" name="pwd" placeholder="Password"><br>
    <input type="submit" value="Login">
</form>
</body>
</html>
'''
        self.container.exec_run(f"echo '{wordpress_login}' > /var/www/html/wp-login.php")
        
        # Fake admin panel
        admin_panel = '''<!DOCTYPE html>
<html>
<head><title>Admin Panel</title></head>
<body>
<h1>Admin Panel</h1>
<p>Welcome to the administration console.</p>
<ul>
    <li><a href="/admin/users">User Management</a></li>
    <li><a href="/admin/database">Database Admin</a></li>
    <li><a href="/admin/logs">System Logs</a></li>
    <li><a href="/admin/config">Configuration</a></li>
</ul>
<p><strong>Version:</strong> 2.4.1</p>
<p><strong>Server:</strong> Ubuntu 22.04 LTS</p>
</body>
</html>
'''
        self.container.exec_run(f"echo '{admin_panel}' > /var/www/html/admin/index.html")
        
        # Fake API endpoint
        fake_api = '''{"status":"ok","server":"production-01","version":"2.4.1","services":{"database":"connected","redis":"connected","cache":"active"},"users":1247,"uptime":"45d 12h 34m"}'''
        self.container.exec_run(f"echo '{fake_api}' > /var/www/html/api/status.json")
        
        print("  ✓ Fake web content created")
        
    def inject_all(self):
        """Run all fake service injections"""
        print("\n" + "="*60)
        print("🎭 STARTING FAKE SERVICES INJECTION")
        print("="*60)
        
        self.create_fake_mysql()
        self.create_fake_redis()
        self.create_fake_psql()
        self.create_fake_netstat()
        self.create_fake_ps()
        self.create_fake_cron()
        self.create_fake_curl_responses()
        
        print("\n" + "="*60)
        print("✅ FAKE SERVICES INJECTION COMPLETE!")
        print("="*60)
        print("\n🎯 Your honeypot now simulates:")
        print("   • MySQL server (port 3306)")
        print("   • Redis server (port 6379)")
        print("   • PostgreSQL server (port 5432)")
        print("   • MongoDB server (port 27017)")
        print("   • Web server (ports 80, 443, 8080)")
        print("   • Fake running processes")
        print("   • Fake cron jobs")
        print("   • Fake admin panels")
        print("\n📝 Test commands:")
        print("   mysql -u root -p")
        print("   redis-cli")
        print("   psql -U postgres")
        print("   netstat -tulpn")
        print("   ps aux")
        print("   crontab -l")
        print("\n🐝 Your honeypot is now much more realistic!")


if __name__ == "__main__":
    import sys
    
    container_name = sys.argv[1] if len(sys.argv) > 1 else "honeypot-manual-test"
    
    injector = FakeServicesInjector(container_name)
    injector.inject_all()
