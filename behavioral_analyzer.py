#!/usr/bin/env python3
"""
Behavioral Analyzer - Differentiate humans from bots
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict
import statistics

class BehavioralAnalyzer:
    def __init__(self, db_path="/home/maradens/.openclaw/workspace/ai-honeypot-phase1/data/attacks.db"):
        self.db_path = db_path
        
    def analyze_command_timing(self):
        """Analyze timing patterns between commands"""
        print("⏱️  Analyzing command timing patterns...")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, command, username 
            FROM commands 
            WHERE command NOT LIKE '%BASH_COMMAND%' 
            AND command NOT LIKE '%profile.d%'
            AND command NOT LIKE '%.bashrc%'
            ORDER BY timestamp
        """)
        
        commands = cursor.fetchall()
        conn.close()
        
        if len(commands) < 2:
            print("  ⚠ Not enough commands to analyze timing")
            return None
        
        # Calculate time deltas between commands
        deltas = []
        for i in range(1, len(commands)):
            t1 = datetime.strptime(commands[i-1]['timestamp'], "%Y-%m-%d %H:%M:%S")
            t2 = datetime.strptime(commands[i]['timestamp'], "%Y-%m-%d %H:%M:%S")
            delta = (t2 - t1).total_seconds()
            deltas.append(delta)
        
        if not deltas:
            return None
            
        avg_delta = statistics.mean(deltas)
        std_delta = statistics.stdev(deltas) if len(deltas) > 1 else 0
        
        return {
            'average_seconds_between_commands': avg_delta,
            'std_deviation': std_delta,
            'min_delta': min(deltas),
            'max_delta': max(deltas),
            'total_commands': len(commands),
            'is_bot_likely': avg_delta < 2 and std_delta < 1  # Bots are fast and consistent
        }
    
    def analyze_auth_patterns(self):
        """Analyze authentication attempt patterns"""
        print("🔐 Analyzing authentication patterns...")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get attempts by IP and time
        cursor.execute("""
            SELECT source_ip, timestamp, username, result
            FROM auth_attempts
            ORDER BY timestamp
        """)
        
        attempts = cursor.fetchall()
        conn.close()
        
        # Group by IP
        by_ip = defaultdict(list)
        for attempt in attempts:
            by_ip[attempt['source_ip']].append({
                'timestamp': attempt['timestamp'],
                'username': attempt['username'],
                'result': attempt['result']
            })
        
        analysis = {}
        
        for ip, ip_attempts in by_ip.items():
            if len(ip_attempts) < 3:
                continue
            
            # Calculate timing
            timestamps = []
            for attempt in ip_attempts:
                try:
                    ts = datetime.strptime(attempt['timestamp'], "%Y-%m-%d %H:%M:%S")
                    timestamps.append(ts)
                except:
                    pass
            
            if len(timestamps) < 2:
                continue
            
            # Time deltas
            deltas = []
            for i in range(1, len(timestamps)):
                delta = (timestamps[i] - timestamps[i-1]).total_seconds()
                deltas.append(delta)
            
            avg_delta = statistics.mean(deltas)
            std_delta = statistics.stdev(deltas) if len(deltas) > 1 else 0
            
            # Username diversity
            usernames = set(attempt['username'] for attempt in ip_attempts)
            
            # Success rate
            successes = sum(1 for a in ip_attempts if a['result'] == 'SUCCESS')
            success_rate = successes / len(ip_attempts)
            
            analysis[ip] = {
                'total_attempts': len(ip_attempts),
                'unique_usernames': len(usernames),
                'username_list': list(usernames),
                'avg_seconds_between_attempts': avg_delta,
                'timing_std_dev': std_delta,
                'success_rate': success_rate,
                'is_bot_likely': self.classify_as_bot(
                    len(ip_attempts), len(usernames), avg_delta, std_delta, success_rate
                )
            }
        
        return analysis
    
    def classify_as_bot(self, attempts, unique_usernames, avg_delta, std_delta, success_rate):
        """Classify IP as bot or human"""
        score = 0
        
        # High volume = bot
        if attempts > 50:
            score += 3
        elif attempts > 20:
            score += 2
        elif attempts > 10:
            score += 1
        
        # Many usernames = bot (dictionary attack)
        if unique_usernames > 10:
            score += 3
        elif unique_usernames > 5:
            score += 2
        
        # Fast timing = bot
        if avg_delta < 1:
            score += 3
        elif avg_delta < 5:
            score += 2
        elif avg_delta < 10:
            score += 1
        
        # Consistent timing = bot
        if std_delta < 2 and attempts > 10:
            score += 2
        
        # Low success rate = bot (brute force)
        if success_rate < 0.1 and attempts > 20:
            score += 1
        
        # Classification
        if score >= 6:
            return "DEFINITELY_BOT"
        elif score >= 4:
            return "LIKELY_BOT"
        elif score >= 2:
            return "POSSIBLY_BOT"
        else:
            return "LIKELY_HUMAN"
    
    def analyze_command_diversity(self):
        """Analyze command diversity and sophistication"""
        print("📊 Analyzing command diversity...")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT command
            FROM commands
            WHERE command NOT LIKE '%BASH_COMMAND%'
            AND command NOT LIKE '%profile.d%'
            AND command NOT LIKE '%.bashrc%'
            AND command NOT LIKE '%command_log%'
        """)
        
        commands = [row['command'] for row in cursor.fetchall()]
        conn.close()
        
        if not commands:
            return None
        
        # Categorize commands
        categories = {
            'reconnaissance': 0,
            'file_access': 0,
            'database': 0,
            'network': 0,
            'system': 0,
            'exploitation': 0,
        }
        
        recon_keywords = ['cat', 'ls', 'find', 'grep', 'whoami', 'id', 'uname']
        file_keywords = ['cat', 'less', 'more', 'head', 'tail', 'vi', 'vim', 'nano']
        db_keywords = ['mysql', 'psql', 'redis', 'mongo', 'SELECT', 'SHOW']
        network_keywords = ['netstat', 'ss', 'curl', 'wget', 'nc', 'nmap']
        system_keywords = ['ps', 'top', 'htop', 'systemctl', 'service']
        exploit_keywords = ['chmod', 'chown', 'rm -rf', 'wget.*sh', 'curl.*sh', '| bash']
        
        for cmd in commands:
            cmd_lower = cmd.lower()
            
            for keyword in recon_keywords:
                if keyword in cmd_lower:
                    categories['reconnaissance'] += 1
                    break
            
            for keyword in file_keywords:
                if keyword in cmd_lower:
                    categories['file_access'] += 1
                    break
            
            for keyword in db_keywords:
                if keyword in cmd_lower:
                    categories['database'] += 1
                    break
            
            for keyword in network_keywords:
                if keyword in cmd_lower:
                    categories['network'] += 1
                    break
            
            for keyword in system_keywords:
                if keyword in cmd_lower:
                    categories['system'] += 1
                    break
            
            for keyword in exploit_keywords:
                if keyword in cmd_lower:
                    categories['exploitation'] += 1
                    break
        
        return {
            'total_unique_commands': len(commands),
            'categories': categories,
            'sophistication_score': sum(categories.values()) / max(len(commands), 1),
            'is_human_likely': categories['exploitation'] > 0 or categories['database'] > 2
        }
    
    def generate_report(self):
        """Generate comprehensive behavioral report"""
        print("\n" + "="*80)
        print("🤖 BEHAVIORAL ANALYSIS REPORT")
        print("="*80)
        
        # Timing analysis
        timing = self.analyze_command_timing()
        if timing:
            print("\n⏱️  COMMAND TIMING ANALYSIS:")
            print(f"  Average time between commands: {timing['average_seconds_between_commands']:.2f}s")
            print(f"  Standard deviation: {timing['std_deviation']:.2f}s")
            print(f"  Min/Max: {timing['min_delta']:.2f}s / {timing['max_delta']:.2f}s")
            print(f"  Bot likelihood: {'✅ YES' if timing['is_bot_likely'] else '❌ NO'}")
        
        # Auth patterns
        auth_patterns = self.analyze_auth_patterns()
        if auth_patterns:
            print("\n🔐 AUTHENTICATION PATTERNS:")
            for ip, data in auth_patterns.items():
                print(f"\n  IP: {ip}")
                print(f"    Attempts: {data['total_attempts']}")
                print(f"    Unique usernames: {data['unique_usernames']}")
                print(f"    Avg time between attempts: {data['avg_seconds_between_attempts']:.2f}s")
                print(f"    Success rate: {data['success_rate']:.1%}")
                print(f"    Classification: {data['is_bot_likely']}")
                
                if data['is_bot_likely'] in ['DEFINITELY_BOT', 'LIKELY_BOT']:
                    print(f"    ⚠️  This is likely a BOT/Automated script!")
        
        # Command diversity
        diversity = self.analyze_command_diversity()
        if diversity:
            print("\n📊 COMMAND DIVERSITY:")
            print(f"  Total unique commands: {diversity['total_unique_commands']}")
            print(f"  Categories:")
            for cat, count in diversity['categories'].items():
                print(f"    • {cat}: {count}")
            print(f"  Human likelihood: {'✅ YES' if diversity['is_human_likely'] else '❌ NO'}")
        
        # Overall assessment
        print("\n" + "="*80)
        print("🎯 OVERALL ASSESSMENT:")
        print("="*80)
        
        if timing and timing['is_bot_likely']:
            print("⚠️  ACTIVITY APPEARS TO BE AUTOMATED (BOT/SCRIPT)")
            print("   - Fast, consistent command timing")
            print("   - Likely automated scanner or brute force tool")
        elif diversity and diversity['is_human_likely']:
            print("✅ ACTIVITY APPEARS TO BE HUMAN")
            print("   - Variable timing, strategic progression")
            print("   - Shows signs of reading output and adapting")
        else:
            print("❓ MIXED SIGNALS - Manual review recommended")
        
        print("\n" + "="*80)

def main():
    analyzer = BehavioralAnalyzer()
    analyzer.generate_report()

if __name__ == "__main__":
    main()
