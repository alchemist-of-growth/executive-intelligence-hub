"""
run_daily_scan.py
Master execution pipeline for the 08:30 AM morning executive intelligence scan.
"""

import os
import sys
import json
from datetime import datetime

# Adjust paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

from fetch_intelligence import fetch_all_raw_signals
from synthesize_briefing import synthesize_with_gemini

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Morning Executive Intelligence Scan...")
    
    # 1. Fetch live signals
    raw_signals = fetch_all_raw_signals()
    
    # 2. Synthesize with Gemini
    briefing = synthesize_with_gemini(raw_signals)
    
    # 3. Write briefing_today.json
    today_file = os.path.join(DATA_DIR, "briefing_today.json")
    with open(today_file, "w", encoding="utf-8") as f:
        json.dump(briefing, f, indent=2, ensure_ascii=False)
    print(f"✓ Successfully wrote daily briefing to {today_file}")
    
    # 4. Update archive.json
    archive_file = os.path.join(DATA_DIR, "archive.json")
    archive_data = []
    if os.path.exists(archive_file):
        try:
            with open(archive_file, "r", encoding="utf-8") as f:
                archive_data = json.load(f)
        except Exception:
            archive_data = []
            
    # Prepend today's briefing entry summary
    date_key = briefing.get("date", datetime.now().strftime("%Y-%m-%d"))
    # Filter out duplicate of same date
    archive_data = [item for item in archive_data if item.get("date") != date_key]
    archive_data.insert(0, {
        "date": date_key,
        "generated_at": briefing.get("generated_at"),
        "top_macro_signals": briefing.get("top_macro_signals", []),
        "card_count": len(briefing.get("briefing_cards", []))
    })
    
    # Keep last 30 days
    archive_data = archive_data[:30]
    with open(archive_file, "w", encoding="utf-8") as f:
        json.dump(archive_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Updated archive catalog at {archive_file}")
    print("="*60)
    print(f"✓ Executive Intelligence Briefing Ready ({len(briefing.get('briefing_cards', []))} high-signal cards)")
    print("="*60)

if __name__ == "__main__":
    main()
