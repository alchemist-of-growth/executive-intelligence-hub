"""
run_daily_scan.py
Master execution pipeline for the 08:30 AM morning executive intelligence scan.
Generates:
1. `data/briefing_today.json`: Curated 8-minute executive briefing with P&L analysis & LinkedIn hooks.
2. `data/broking_stream.json`: Broad-based continuous scroll/wire of all capital markets & broking news.
3. `data/archive.json`: Historical archive catalogue.
"""

import os
import sys
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

from fetch_intelligence import fetch_all_raw_signals
from synthesize_briefing import synthesize_with_gemini

def main():
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp_str}] Starting Comprehensive Broking & Sector Intelligence Scan...")
    
    # 1. Fetch live broad-based signals
    raw_signals = fetch_all_raw_signals()
    
    # 2. Synthesize Curated 8-Minute Executive Briefing via Gemini
    briefing = synthesize_with_gemini(raw_signals)
    
    # Write briefing_today.json
    today_file = os.path.join(DATA_DIR, "briefing_today.json")
    with open(today_file, "w", encoding="utf-8") as f:
        json.dump(briefing, f, indent=2, ensure_ascii=False)
    print(f"✓ Wrote curated briefing to {today_file}")
    
    # 3. Build & Maintain the Continuous Broking Stream / Scroll Archive
    stream_file = os.path.join(DATA_DIR, "broking_stream.json")
    existing_stream = []
    if os.path.exists(stream_file):
        try:
            with open(stream_file, "r", encoding="utf-8") as f:
                existing_stream = json.load(f)
        except Exception:
            existing_stream = []
            
    # Combine fresh signals with existing stream, deduplicating by URL or title
    seen_titles = set()
    combined_stream = []
    
    for sig in raw_signals + existing_stream:
        title_key = sig.get("title", "").strip().lower()
        if title_key and title_key not in seen_titles:
            seen_titles.add(title_key)
            combined_stream.append({
                "id": f"wire-{len(combined_stream)+1}",
                "title": sig.get("title"),
                "summary": sig.get("summary"),
                "url": sig.get("url"),
                "source": sig.get("source", "Capital Markets Wire"),
                "category": sig.get("category", "Capital Markets & MTF"),
                "subcategory": sig.get("subcategory", "Broking"),
                "published": sig.get("published", datetime.now().strftime("%Y-%m-%d")),
                "tags": sig.get("tags", ["BROKING", "BFSI"]),
                "relevance_score": sig.get("relevance_score", 1)
            })
            
    # Keep the top 60 most relevant / recent items for smooth scrolling
    combined_stream = combined_stream[:60]
    with open(stream_file, "w", encoding="utf-8") as f:
        json.dump(combined_stream, f, indent=2, ensure_ascii=False)
    print(f"✓ Wrote {len(combined_stream)} items to Broking Continuous Scroll ({stream_file})")
    
    # 4. Update archive.json
    archive_file = os.path.join(DATA_DIR, "archive.json")
    archive_data = []
    if os.path.exists(archive_file):
        try:
            with open(archive_file, "r", encoding="utf-8") as f:
                archive_data = json.load(f)
        except Exception:
            archive_data = []
            
    date_key = briefing.get("date", datetime.now().strftime("%B %d, %Y"))
    archive_data = [item for item in archive_data if item.get("date") != date_key]
    archive_data.insert(0, {
        "date": date_key,
        "generated_at": briefing.get("generated_at"),
        "top_macro_signals": briefing.get("top_macro_signals", []),
        "card_count": len(briefing.get("briefing_cards", [])),
        "stream_count": len(combined_stream)
    })
    
    archive_data = archive_data[:30]
    with open(archive_file, "w", encoding="utf-8") as f:
        json.dump(archive_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Updated historical archive catalog ({archive_file})")
    print("="*60)
    print(f"✓ Executive Intelligence & Broking Wire Ready: {len(briefing.get('briefing_cards', []))} Briefing Cards + {len(combined_stream)} Broking Stream Items")
    print("="*60)

if __name__ == "__main__":
    main()
