#!/usr/bin/env python3
"""
Cross-Correlation Analyzer - Detect persistent attackers over time
Identifies bots/scripts that return regularly with same patterns
"""

import sqlite3
import json
from collections import defaultdict
from datetime import datetime, timedelta
import statistics

class CrossCorrelationAnalyzer:
    def __init__(self, db_path="/home/maradens/.openclaw/workspace/ai-honeypot-phase1/data/attacks.db"):
        self.db_path = db_path
        
    def analyze_ip_return_patterns(self):
        """Analyze if IPs return on regular schedules"""
        print("🔍 Analyzing IP return patterns...")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all unique IPs and their activity dates
        cursor.execute("""
            SELECT DISTINCT source_ip, DATE(timestamp) as activity_date
            FROM auth_attempts
            ORDER BY source_ip, activity_date
        """)
        
        ip_dates = defaultdict(list)
        for row in cursor.fetchall():
            ip_dates[row['source_ip']].append(row['activity_date'])
        
        conn.close()
        
        print("\n📅 IP RETURN PATTERNS:")
        print("="*80)
        
        persistent_attackers = []
        
        for ip, dates in ip_dates.items():
            if len(dates) < 2:
                continue
            
            # Sort dates
            date_objs = []
            for d in sorted(set(dates)):
                try:
                    date_objs.append(datetime.strptime(d, "%Y-%m-%d"))
                except:
                    pass
            
            if len(date_objs) < 2:
                continue
            
            # Calculate gaps between visits
            gaps = []
            for i in range(1, len(date_objs)):
                gap = (date_objs[i] - date_objs[i-1]).days
                gaps.append(gap)
            
            avg_gap = statistics.mean(gaps)
            std_gap = statistics.stdev(gaps) if len(gaps) > 1 else 0
            
            # Check for regularity
            is_regular = std_gap < 2  # Low variance = regular schedule
            
            print(f"\n🔍 IP: {ip}")
            print(f"   Active days: {len(date_objs)}")
            print(f"   First seen: {date_objs[0].strftime('%Y-%m-%d')}")
            print(f"   Last seen: {date_objs[-1].strftime('%Y-%m-%d')}")
            print(f"   Avg gap: {avg_gap:.1f} days")
            print(f"   Gap variance: {std_gap:.1f} days")
            
            if is_regular and len(date_objs) >= 3:
                print(f"   🚨 PATTERN: Returns every {avg_gap:.0f} days (REGULAR)")
                persistent_attackers.append({
                    'ip': ip,
                    'pattern': 'regular',
                    'interval_days': avg_gap,
                    'activity_days': len(date_objs)
                })
            elif len(date_objs) >= 5:
                print(f"   ⚠️  PATTERN: Frequent returner (irregular)")
                persistent_attackers.append({
                    'ip': ip,
                    'pattern': 'frequent_irregular',
                    'activity_days': len(date_objs)
                })
            else:
                print(f"   ℹ️  PATTERN: Occasional visitor")
        
        return persistent_attackers
    
    def analyze_username_patterns(self):
        """Analyze if same username lists are used repeatedly"""
        print("\n🔍 Analyzing username patterns...")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get usernames per IP
        cursor.execute("""
            SELECT source_ip, username
            FROM auth_attempts
            GROUP BY source_ip, username
        """)
        
        ip_usernames = defaultdict(set)
        for row in cursor.fetchall():
            ip_usernames[row['source_ip']].add(row['username'])
        
        conn.close()
        
        print("\n📝 USERNAME PATTERN ANALYSIS:")
        print("="*80)
        
        # Find common username sets
        username_sets = []
        for ip, usernames in ip_usernames.items():
            if len(usernames) >= 10:  # Only interesting if many usernames
                username_sets.append({
                    'ip': ip,
                    'usernames': sorted(list(usernames)),
                    'count': len(usernames)
                })
        
        # Group by username similarity
        if len(username_sets) >= 2:
            print(f"\nFound {len(username_sets)} IPs with 10+ unique usernames")
            
            # Find common usernames across IPs
            all_usernames = set()
            for item in username_sets:
                all_usernames.update(item['usernames'])
            
            print(f"\nTotal unique usernames used: {len(all_usernames)}")
            print(f"Most common usernames: {list(all_usernames)[:20]}")
            
            # Check for identical username lists (same bot/script)
            username_sets_sorted = []
            for item in username_sets:
                username_sets_sorted.append({
                    'ip': item['ip'],
                    'usernames': tuple(sorted(item['usernames']))
                })
            
            # Find duplicates
            seen_sets = {}
            for item in username_sets_sorted:
                key = item['usernames']
                if key in seen_sets:
                    seen_sets[key].append(item['ip'])
                else:
                    seen_sets[key] = [item['ip']]
            
            print("\n🔗 POSSIBLY SAME BOT/SCRIPT (identical username lists):")
            for usernames, ips in seen_sets.items():
                if len(ips) > 1:
                    print(f"   IPs sharing same username list: {ips}")
                    print(f"   Usernames ({len(usernames)}): {list(usernames)[:10]}...")
        
        return username_sets
    
    def analyze_time_of_day_patterns(self):
        """Analyze if attacks happen at consistent times"""
        print("\n🕐 Analyzing time-of-day patterns...")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get hour of day for each IP
        cursor.execute("""
            SELECT source_ip, 
                   strftime('%H', timestamp) as hour,
                   COUNT(*) as attempts
            FROM auth_attempts
            GROUP BY source_ip, strftime('%H', timestamp)
            HAVING attempts >= 5
        """)
        
        ip_hours = defaultdict(lambda: defaultdict(int))
        for row in cursor.fetchall():
            ip_hours[row['source_ip']][row['hour']] = row['attempts']
        
        conn.close()
        
        print("\n🕐 TIME-OF-DAY PATTERN ANALYSIS:")
        print("="*80)
        
        consistent_timers = []
        
        for ip, hours in ip_hours.items():
            if len(hours) < 3:
                continue
            
            # Find peak hours
            peak_hour = max(hours.items(), key=lambda x: x[1])
            peak_count = peak_hour[1]
            total = sum(hours.values())
            
            concentration = peak_count / total
            
            if concentration > 0.6:  # 60%+ in one hour
                print(f"\n🔍 IP: {ip}")
                print(f"   Peak hour: {peak_hour[0]}:00 ({peak_count} attempts)")
                print(f"   Concentration: {concentration:.1%} in peak hour")
                print(f"   ⚠️  PATTERN: Attacks at consistent time (BOT)")
                
                consistent_timers.append({
                    'ip': ip,
                    'peak_hour': peak_hour[0],
                    'concentration': concentration
                })
        
        return consistent_timers
    
    def generate_report(self):
        """Generate comprehensive cross-correlation report"""
        print("\n" + "="*80)
        print("🔗 CROSS-CORRELATION ANALYSIS REPORT")
        print("="*80)
        print("\nThis report identifies persistent attackers and coordinated activity")
        print("over days/weeks/months of monitoring.\n")
        
        # Analyze patterns
        persistent = self.analyze_ip_return_patterns()
        username_patterns = self.analyze_username_patterns()
        time_patterns = self.analyze_time_of_day_patterns()
        
        # Summary
        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        
        print(f"\nPersistent attackers (regular returns): {len(persistent)}")
        print(f"Shared username lists (same bot): {'Detected' if any(len(ips) > 1 for ips in self.analyze_username_patterns()) else 'None'}")
        print(f"Consistent time attackers: {len(time_patterns)}")
        
        # Threat assessment
        print("\n🎯 THREAT ASSESSMENT:")
        if len(persistent) > 5:
            print("   🚨 HIGH: Multiple persistent attackers detected")
            print("      → Likely botnet or organized scanning")
        elif len(persistent) > 0:
            print("   ⚠️  MEDIUM: Some persistent activity")
            print("      → Mix of bots and occasional scanners")
        else:
            print("   ✅ LOW: No persistent patterns yet")
            print("      → Need more data (days/weeks of monitoring)")
        
        print("\n" + "="*80)
        
        # Export
        report = {
            'timestamp': datetime.now().isoformat(),
            'persistent_attackers': persistent,
            'time_patterns': time_patterns,
            'summary': {
                'persistent_count': len(persistent),
                'time_pattern_count': len(time_patterns)
            }
        }
        
        with open('/home/maradens/.openclaw/workspace/ai-honeypot-phase1/cross_correlation_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print("✅ Report exported to: cross_correlation_report.json")
        print("="*80)

def main():
    analyzer = CrossCorrelationAnalyzer()
    analyzer.generate_report()

if __name__ == "__main__":
    main()
