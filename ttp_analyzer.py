#!/usr/bin/env python3
"""
TTP Analyzer - Extract MITRE ATT&CK TTPs from honeypot logs
"""

import sqlite3
import json
from collections import defaultdict
from datetime import datetime

# MITRE ATT&CK TTP mapping
TTP_PATTERNS = {
    # Reconnaissance
    "T1592": {
        "name": "Gather Victim Host Information",
        "tactic": "Reconnaissance",
        "patterns": ["netstat", "ifconfig", "hostname", "uname", "cat /etc/hosts"]
    },
    "T1590": {
        "name": "Gather Victim Network Information",
        "tactic": "Reconnaissance",
        "patterns": ["netstat -tulpn", "netstat -an", "ss -tulpn", "route", "ip route"]
    },
    "T1082": {
        "name": "System Information Discovery",
        "tactic": "Discovery",
        "patterns": ["ps aux", "ps -ef", "uname -a", "cat /etc/passwd", "cat /etc/os-release"]
    },
    "T1083": {
        "name": "File and Directory Discovery",
        "tactic": "Discovery",
        "patterns": ["find / -name", "ls -la", "tree", "locate"]
    },
    
    # Credential Access
    "T1110": {
        "name": "Brute Force",
        "tactic": "Credential Access",
        "patterns": ["ssh", "login"],
        "source": "auth_attempts"
    },
    "T1552": {
        "name": "Unsecured Credentials",
        "tactic": "Credential Access",
        "patterns": [
            "cat /root/.aws/credentials",
            "cat /root/.ssh/id_rsa",
            "cat /root/.git-credentials",
            "cat /root/.kube/config",
            "cat ~/.aws",
            "cat ~/.ssh",
            "cat .env",
            "cat /etc/shadow"
        ]
    },
    "T1528": {
        "name": "Steal Web Session Cookie",
        "tactic": "Credential Access",
        "patterns": ["curl.*cookie", "wget.*save-cookies", "cat.*cookie"]
    },
    
    # Collection
    "T1213": {
        "name": "Data from Information Repositories",
        "tactic": "Collection",
        "patterns": [
            "SELECT.*FROM.*users",
            "SELECT.*FROM.*credentials",
            "SELECT.*FROM.*api_keys",
            "mysql.*-u",
            "psql.*SELECT",
            "redis-cli.*GET"
        ]
    },
    "T1005": {
        "name": "Data from Local System",
        "tactic": "Collection",
        "patterns": [
            "cat.*.sql",
            "cat.*backup",
            "cat.*dump",
            "tar.*-czf"
        ]
    },
    
    # Command and Control
    "T1071": {
        "name": "Application Layer Protocol",
        "tactic": "Command and Control",
        "patterns": ["curl http", "wget http", "nc -e", "bash -i"]
    },
    
    # Persistence
    "T1053": {
        "name": "Scheduled Task/Job",
        "tactic": "Persistence",
        "patterns": ["crontab -e", "echo.*>> /etc/crontab", "systemctl enable"]
    },
    
    # Defense Evasion
    "T1070": {
        "name": "Indicator Removal",
        "tactic": "Defense Evasion",
        "patterns": ["rm.*history", "history -c", ">> /dev/null", "chmod 777"]
    },
    
    # Impact
    "T1490": {
        "name": "Inhibit System Recovery",
        "tactic": "Impact",
        "patterns": ["rm -rf", "mkfs", "dd if=/dev/zero"]
    },
}

class TTPAnalyzer:
    def __init__(self, db_path="/home/maradens/.openclaw/workspace/ai-honeypot-phase1/data/attacks.db"):
        self.db_path = db_path
        self.detected_ttps = defaultdict(list)
        
    def analyze_commands(self):
        """Analyze command logs for TTPs"""
        print("🔍 Analyzing commands for TTPs...")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT command, username, timestamp FROM commands WHERE command NOT LIKE '%BASH_COMMAND%'")
        commands = cursor.fetchall()
        
        for cmd_row in commands:
            command = cmd_row['command'].lower()
            
            for ttp_id, ttp_info in TTP_PATTERNS.items():
                for pattern in ttp_info['patterns']:
                    if pattern.lower() in command:
                        self.detected_ttps[ttp_id].append({
                            'command': cmd_row['command'],
                            'username': cmd_row['username'],
                            'timestamp': cmd_row['timestamp']
                        })
        
        conn.close()
        
        return self.detected_ttps
    
    def analyze_auth_attempts(self):
        """Analyze auth attempts for brute force"""
        print("🔍 Analyzing auth attempts for T1110 (Brute Force)...")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT source_ip, COUNT(*) as attempts, 
                   SUM(CASE WHEN result='FAILED' THEN 1 ELSE 0 END) as failed
            FROM auth_attempts 
            GROUP BY source_ip 
            HAVING attempts >= 3
        """)
        
        brute_force_sources = cursor.fetchall()
        
        for row in brute_force_sources:
            self.detected_ttps['T1110'].append({
                'source_ip': row['source_ip'],
                'total_attempts': row['attempts'],
                'failed_attempts': row['failed']
            })
        
        conn.close()
    
    def generate_report(self):
        """Generate TTP report"""
        print("\n" + "="*80)
        print("📊 MITRE ATT&CK TTP REPORT")
        print("="*80)
        
        if not self.detected_ttps:
            print("\nNo TTPs detected yet.")
            print("Run attacks first to collect data!")
            return
        
        # Group by tactic
        tactics = defaultdict(list)
        for ttp_id, instances in self.detected_ttps.items():
            tactic = TTP_PATTERNS[ttp_id]['tactic']
            tactics[tactic].append((ttp_id, instances))
        
        for tactic, ttps in sorted(tactics.items()):
            print(f"\n📁 {tactic}")
            print("-" * 80)
            
            for ttp_id, instances in ttps:
                ttp_info = TTP_PATTERNS[ttp_id]
                print(f"\n  🔹 {ttp_id}: {ttp_info['name']}")
                print(f"     Count: {len(instances)} instances")
                
                # Show examples
                if len(instances) > 0:
                    example = instances[0]
                    if 'command' in example:
                        cmd = example['command'][:60] + "..." if len(example['command']) > 60 else example['command']
                        print(f"     Example: {cmd}")
                    if 'source_ip' in example:
                        print(f"     Source: {example['source_ip']} ({example['total_attempts']} attempts)")
        
        print("\n" + "="*80)
        print(f"Total TTPs detected: {len(self.detected_ttps)}")
        print("="*80)
        
        return self.detected_ttps
    
    def export_to_json(self, output_path="ttp_report.json"):
        """Export TTP data to JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'ttps': {}
        }
        
        for ttp_id, instances in self.detected_ttps.items():
            ttp_info = TTP_PATTERNS[ttp_id]
            report['ttps'][ttp_id] = {
                'name': ttp_info['name'],
                'tactic': ttp_info['tactic'],
                'count': len(instances),
                'instances': instances[:10]  # First 10 instances
            }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n✅ TTP report exported to: {output_path}")

def main():
    analyzer = TTPAnalyzer()
    
    # Analyze
    analyzer.analyze_commands()
    analyzer.analyze_auth_attempts()
    
    # Generate report
    analyzer.generate_report()
    
    # Export
    analyzer.export_to_json()

if __name__ == "__main__":
    main()
