#!/usr/bin/env python3
"""
Simple database query tool for honeypot attacks
"""

import sqlite3
import sys

DB_PATH = "/home/maradens/.openclaw/workspace/ai-honeypot-phase1/data/attacks.db"

def run_query(query, params=None):
    """Run a SQL query and display results"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        # Display results
        print(f"\n{'='*80}")
        print(f"Query: {query[:60]}...")
        print(f"{'='*80}\n")
        
        if not rows:
            print("No results found.")
        else:
            # Print header
            print(" | ".join(f"{col:<20}" for col in columns))
            print("-" * 80)
            
            # Print rows
            for row in rows:
                print(" | ".join(f"{str(row[col])[:20]:<20}" for col in columns))
            
            print(f"\nTotal rows: {len(rows)}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("📊 Honeypot Database Query Tool")
        print("\nUsage:")
        print("  python query_db.py --recent        # Last 20 attempts")
        print("  python query_db.py --users         # Stats by username")
        print("  python query_db.py --failed        # Failed attempts only")
        print("  python query_db.py --timeline      # Activity timeline")
        print("  python query_db.py --custom \"SQL\"  # Custom query")
        print("\nExamples:")
        print("  python query_db.py --custom \"SELECT * FROM auth_attempts LIMIT 5\"")
        return
        
    if sys.argv[1] == "--recent":
        run_query("""
            SELECT timestamp, username, result, source_ip, port 
            FROM auth_attempts 
            ORDER BY timestamp DESC 
            LIMIT 20
        """)
        
    elif sys.argv[1] == "--users":
        run_query("""
            SELECT 
                username,
                COUNT(*) as total,
                SUM(CASE WHEN result='FAILED' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN result='SUCCESS' THEN 1 ELSE 0 END) as success
            FROM auth_attempts 
            GROUP BY username 
            ORDER BY total DESC
        """)
        
    elif sys.argv[1] == "--failed":
        run_query("""
            SELECT timestamp, username, source_ip 
            FROM auth_attempts 
            WHERE result='FAILED' 
            ORDER BY timestamp DESC
        """)
        
    elif sys.argv[1] == "--timeline":
        run_query("""
            SELECT 
                strftime('%Y-%m-%d %H:00', timestamp) as hour,
                COUNT(*) as attempts,
                SUM(CASE WHEN result='FAILED' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN result='SUCCESS' THEN 1 ELSE 0 END) as success
            FROM auth_attempts 
            GROUP BY hour 
            ORDER BY hour DESC
            LIMIT 24
        """)
        
    elif sys.argv[1] == "--custom" and len(sys.argv) > 2:
        custom_query = " ".join(sys.argv[2:])
        run_query(custom_query)
        
    else:
        print(f"Unknown option: {sys.argv[1]}")
        print("Use --help for usage")

if __name__ == "__main__":
    main()
