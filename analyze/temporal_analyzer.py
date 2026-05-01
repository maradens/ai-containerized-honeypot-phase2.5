#!/usr/bin/env python3
"""
Temporal Pattern Analyzer - Detect bots over days/weeks
"""

import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta

def analyze_long_term_patterns(db_path="/home/maradens/.openclaw/workspace/ai-honeypot-phase1/data/attacks.db"):
    """Analyze attack patterns over time"""
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get daily stats by IP
    cursor.execute("""
        SELECT 
            source_ip,
            DATE(timestamp) as date,
            COUNT(*) as attempts,
            SUM(CASE WHEN result='SUCCESS' THEN 1 ELSE 0 END) as successes
        FROM auth_attempts
        GROUP BY source_ip, DATE(timestamp)
        ORDER BY source_ip, date
    """)
    
    daily_by_ip = defaultdict(list)
    for row in cursor.fetchall():
        daily_by_ip[row['source_ip']].append({
            'date': row['date'],
            'attempts': row['attempts'],
            'successes': row['successes']
        })
    
    conn.close()
    
    print("="*80)
    print("📅 LONG-TERM TEMPORAL ANALYSIS")
    print("="*80)
    
    for ip, days in daily_by_ip.items():
        if len(days) < 2:
            continue
            
        print(f"\n🔍 IP: {ip}")
        print(f"   Days active: {len(days)}")
        
        # Check for consistency
        attempts_list = [d['attempts'] for d in days]
        avg_attempts = sum(attempts_list) / len(attempts_list)
        
        # Calculate variance
        if len(attempts_list) > 1:
            variance = sum((x - avg_attempts) ** 2 for x in attempts_list) / len(attempts_list)
            std_dev = variance ** 0.5
            
            # Low variance = bot
            if std_dev < avg_attempts * 0.1:  # <10% variance
                print(f"   ⚠️  CONSISTENT VOLUME (Bot signature)")
                print(f"      Avg: {avg_attempts:.0f}, StdDev: {std_dev:.0f}")
            else:
                print(f"   ✅ Variable volume (Human signature)")
                print(f"      Avg: {avg_attempts:.0f}, StdDev: {std_dev:.0f}")
        
        # Show pattern
        print(f"   Daily attempts:")
        for day in days[:7]:  # First 7 days
            print(f"      {day['date']}: {day['attempts']} attempts ({day['successes']} success)")
        
        if len(days) > 7:
            print(f"      ... and {len(days) - 7} more days")

def main():
    analyze_long_term_patterns()

if __name__ == "__main__":
    main()
