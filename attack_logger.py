#!/usr/bin/env python3
"""
Attack Logger - Logs honeypot attacks to external SQLite database
Runs outside the container, captures data from Docker
"""

import docker
import sqlite3
import json
import os
from datetime import datetime
import re
import threading
import time

class AttackLogger:
    def __init__(self, db_path="/home/maradens/.openclaw/workspace/ai-honeypot-phase1/data/attacks.db"):
        self.client = docker.from_env()
        self.db_path = db_path
        self.setup_database()
        print(f"🗄️  Attack Logger initialized (database: {db_path})")
        
    def setup_database(self):
        """Create database tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Auth attempts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auth_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                username TEXT,
                result TEXT,
                source_ip TEXT,
                container_id TEXT,
                port INTEGER,
                session_id TEXT,
                authentication_method TEXT
            )
        ''')
        
        # Commands table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                command TEXT,
                container_id TEXT,
                session_id TEXT,
                username TEXT,
                output TEXT
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME,
                end_time DATETIME,
                duration_seconds INTEGER,
                source_ip TEXT,
                username TEXT,
                container_id TEXT,
                commands_count INTEGER DEFAULT 0
            )
        ''')
        
        # Fingerprints table (for future use)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source_ip TEXT,
                user_agent TEXT,
                ssh_version TEXT,
                container_id TEXT,
                is_scanner BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
        print("  ✓ Database tables created/verified")
        
    def parse_wtmp(self, container):
        """Parse /var/log/wtmp for successful logins"""
        try:
            result = container.exec_run("last -n 50", demux=True)
            output = result.output[0].decode() if result.output[0] else ""
            
            # Parse last output format:
            # root     pts/0        172.17.0.1       Thu Apr  9 14:14    still logged in
            # root     pts/0        172.17.0.1       Thu Apr  9 14:12 - 14:14  (00:02)
            lines = output.strip().split('\n')
            
            for line in lines:
                if not line.strip() or line.startswith('root     ') and 'wtmp begins' in line:
                    continue
                    
                parts = line.split()
                if len(parts) >= 4:
                    username = parts[0]
                    # terminal = parts[1]
                    source_ip = parts[2]
                    # Date parts: Day Month Date Time
                    day = parts[3]
                    month = parts[4]
                    date = parts[5]
                    time_str = parts[6] if len(parts) > 6 else "00:00"
                    
                    # Skip if looks like header/footer
                    if username in ['root', 'wtmp', '~']:
                        if 'begins' in line or 'still' not in line and '-' not in line:
                            continue
                    
                    timestamp = f"{day} {month} {date} {time_str}"
                    result = "SUCCESS"
                    
                    self.log_auth_attempt(
                        container.id[:12],
                        username,
                        result,
                        source_ip,
                        "password",
                        timestamp
                    )
                
        except Exception as e:
            print(f"  ⚠ Error parsing wtmp: {e}")
            import traceback
            traceback.print_exc()
            
    def parse_btmp(self, container):
        """Parse /var/log/btmp for failed login attempts"""
        try:
            result = container.exec_run("lastb -n 50", demux=True)
            output = result.output[0].decode() if result.output[0] else ""
            
            # Parse lastb output format:
            # root     ssh:notty    172.17.0.1       Thu Apr  9 14:12 - 14:12  (00:00)
            lines = output.strip().split('\n')
            
            for line in lines:
                if not line.strip() or 'btmp begins' in line:
                    continue
                    
                parts = line.split()
                if len(parts) >= 4:
                    username = parts[0]
                    # terminal = parts[1] (ssh:notty)
                    source_ip = parts[2]
                    # Date parts: Day Month Date Time
                    day = parts[3]
                    month = parts[4]
                    date = parts[5]
                    time_str = parts[6] if len(parts) > 6 else "00:00"
                    
                    timestamp = f"{day} {month} {date} {time_str}"
                    
                    self.log_auth_attempt(
                        container.id[:12],
                        username,
                        "FAILED",
                        source_ip,
                        "password",
                        timestamp
                    )
                
        except Exception as e:
            print(f"  ⚠ Error parsing btmp: {e}")
            import traceback
            traceback.print_exc()
            
    def log_auth_attempt(self, container_id, username, result, source_ip, method, timestamp=None):
        """Log authentication attempt to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get port from container
            port = self._get_container_port(container_id)
            
            if timestamp:
                # Convert timestamp to datetime
                # Format: "Thu Apr  9 14:14"
                try:
                    dt = datetime.strptime(f"2026 {timestamp}", "%Y %b %d %H:%M")
                except:
                    dt = datetime.now()
            else:
                dt = datetime.now()
                
            cursor.execute('''
                INSERT INTO auth_attempts (username, result, source_ip, container_id, port, authentication_method, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, result, source_ip, container_id, port, method, dt))
            
            conn.commit()
            conn.close()
            
            print(f"  ✓ Logged {result} attempt: {username} from {source_ip}")
            
        except Exception as e:
            print(f"  ✗ Error logging auth attempt: {e}")
            
    def _get_container_port(self, container_id):
        """Get the host port for a container"""
        try:
            container = self.client.containers.get(container_id)
            ports = container.attrs['NetworkSettings']['Ports']
            
            # Find port 22 mapping
            if '22/tcp' in ports and ports['22/tcp']:
                return ports['22/tcp'][0]['HostPort']
            return None
        except:
            return None
            
    def parse_commands(self, container):
        """Parse command logs from container"""
        try:
            result = container.exec_run("cat /var/log/attacks/command_log 2>/dev/null", demux=True)
            output = result.output[0].decode() if result.output[0] else ""
            
            if not output.strip():
                print("  ℹ No commands logged yet")
                return
                
            lines = output.strip().split('\n')
            logged = 0
            
            for line in lines:
                if not line.strip():
                    continue
                    
                # Format: timestamp|user|command
                parts = line.split('|', 2)
                if len(parts) >= 3:
                    timestamp = parts[0]
                    username = parts[1]
                    command = parts[2] if len(parts) > 2 else ""
                    
                    # Insert into database
                    self.log_command(
                        container.id[:12],
                        username,
                        command,
                        timestamp
                    )
                    logged += 1
            
            print(f"  ✓ Logged {logged} commands")
            
        except Exception as e:
            print(f"  ⚠ Error parsing commands: {e}")
            
    def log_command(self, container_id, username, command, timestamp=None):
        """Log command execution to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if timestamp:
                # Convert timestamp if needed
                try:
                    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                except:
                    dt = datetime.now()
            else:
                dt = datetime.now()
                
            cursor.execute('''
                INSERT INTO commands (command, container_id, username, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (command, container_id, username, dt))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            # Silently fail for command logging
            pass
            
    def scan_container_logs(self, container_name="honeypot-manual-test"):
        """Scan a container and log all auth attempts and commands"""
        print(f"\n🔍 Scanning container: {container_name}")
        
        try:
            container = self.client.containers.get(container_name)
            print(f"  Container status: {container.status}")
            
            # Parse successful logins
            print("  → Parsing successful logins (wtmp)...")
            self.parse_wtmp(container)
            
            # Parse failed logins
            print("  → Parsing failed logins (btmp)...")
            self.parse_btmp(container)
            
            # Parse commands
            print("  → Parsing commands...")
            self.parse_commands(container)
            
            print(f"✅ Scanning complete!")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            
    def get_statistics(self):
        """Display attack statistics from database"""
        print("\n" + "="*60)
        print("📊 ATTACK STATISTICS")
        print("="*60)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total attempts
            cursor.execute("SELECT COUNT(*) FROM auth_attempts")
            total = cursor.fetchone()[0]
            print(f"\nTotal attempts: {total}")
            
            # Successful vs Failed
            cursor.execute("SELECT result, COUNT(*) FROM auth_attempts GROUP BY result")
            results = cursor.fetchall()
            print("\nBy result:")
            for result, count in results:
                print(f"  {result}: {count}")
            
            # Top usernames targeted
            cursor.execute("""
                SELECT username, COUNT(*) as attempts,
                       SUM(CASE WHEN result='FAILED' THEN 1 ELSE 0 END) as failed,
                       SUM(CASE WHEN result='SUCCESS' THEN 1 ELSE 0 END) as success
                FROM auth_attempts 
                GROUP BY username 
                ORDER BY attempts DESC
                LIMIT 10
            """)
            usernames = cursor.fetchall()
            print("\nTop targeted usernames:")
            for username, attempts, failed, success in usernames:
                print(f"  {username:15} | Attempts: {attempts:3} | Failed: {failed:3} | Success: {success:3}")
            
            # Top source IPs
            cursor.execute("""
                SELECT source_ip, COUNT(*) as attempts,
                       SUM(CASE WHEN result='FAILED' THEN 1 ELSE 0 END) as failed
                FROM auth_attempts 
                GROUP BY source_ip 
                ORDER BY attempts DESC
                LIMIT 10
            """)
            ips = cursor.fetchall()
            print("\nTop source IPs:")
            for ip, attempts, failed in ips:
                print(f"  {ip:20} | Attempts: {attempts:3} | Failed: {failed:3}")
            
            # Timeline
            cursor.execute("""
                SELECT DATE(timestamp) as date, COUNT(*) as attempts
                FROM auth_attempts 
                GROUP BY date 
                ORDER BY date DESC
                LIMIT 7
            """)
            timeline = cursor.fetchall()
            print("\nLast 7 days activity:")
            for date, attempts in timeline:
                print(f"  {date}: {attempts} attempts")
            
            conn.close()
            
        except Exception as e:
            print(f"  ✗ Error getting statistics: {e}")
            
        print("="*60)
        
    def export_to_json(self, output_file="/home/maradens/.openclaw/workspace/ai-honeypot-phase1/data/attacks.json"):
        """Export all attack data to JSON"""
        print(f"\n📄 Exporting to {output_file}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            data = {
                "auth_attempts": [],
                "exported_at": datetime.now().isoformat()
            }
            
            cursor.execute("SELECT * FROM auth_attempts")
            for row in cursor.fetchall():
                data["auth_attempts"].append(dict(row))
                
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            print(f"  ✓ Exported {len(data['auth_attempts'])} records")
            
            conn.close()
            
        except Exception as e:
            print(f"  ✗ Error exporting: {e}")
            
    def monitor_container(self, container_name="honeypot-manual-test", interval=30):
        """Continuously monitor container for new attacks"""
        print(f"\n👀 Starting continuous monitoring of {container_name}")
        print(f"   Checking every {interval} seconds")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while True:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning...")
                self.scan_container_logs(container_name)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
    else:
        action = "scan"
        
    logger = AttackLogger()
    
    if action == "scan":
        logger.scan_container_logs()
        logger.get_statistics()
        
    elif action == "stats":
        logger.get_statistics()
        
    elif action == "export":
        logger.export_to_json()
        
    elif action == "monitor":
        if len(sys.argv) > 2:
            container = sys.argv[2]
        else:
            container = "honeypot-manual-test"
        logger.monitor_container(container)
        
    else:
        print("Usage: python attack_logger.py [scan|stats|export|monitor]")
        print("  scan    - Scan container once and show stats")
        print("  stats   - Show statistics only")
        print("  export  - Export data to JSON")
        print("  monitor - Continuously monitor container")
