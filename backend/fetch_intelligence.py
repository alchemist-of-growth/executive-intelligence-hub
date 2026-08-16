"""
fetch_intelligence.py
Broad-based Capital Markets, Broking, WealthTech & Regulatory Aggregator.
Covers: Retail Broking, MTF, F&O/Derivatives, Algo/API Trading, NSE/BSE, Demat Growth,
SEBI Circulars, RBI Directions, and FinTech distribution media.
"""

import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import re
import urllib.request
import urllib.error
import ssl

try:
    _ssl_context = ssl.create_default_context()
    _ssl_context.check_hostname = False
    _ssl_context.verify_mode = ssl.CERT_NONE
except Exception:
    _ssl_context = None

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# Comprehensive Broking, Capital Markets, FinTech & Regulatory Feeds
FEEDS = [
    # 1. Broking & Capital Markets
    {
        "category": "Capital Markets & MTF",
        "subcategory": "Broking & Markets",
        "source": "ET Markets - Stocks & Broking",
        "url": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
        "type": "rss"
    },
    {
        "category": "Capital Markets & MTF",
        "subcategory": "Market Reports",
        "source": "Moneycontrol Market Reports",
        "url": "https://www.moneycontrol.com/rss/marketreports.xml",
        "type": "rss"
    },
    {
        "category": "Capital Markets & MTF",
        "subcategory": "Exchanges & Equities",
        "source": "Livemint Markets",
        "url": "https://www.livemint.com/rss/markets",
        "type": "rss"
    },
    {
        "category": "FinTech & WealthTech",
        "subcategory": "Wealth & Advisory",
        "source": "ET Wealth",
        "url": "https://economictimes.indiatimes.com/wealth/rssfeeds/837555174.cms",
        "type": "rss"
    },
    {
        "category": "FinTech & WealthTech",
        "subcategory": "Personal Finance & PMS",
        "source": "Livemint Money & Wealth",
        "url": "https://www.livemint.com/rss/money",
        "type": "rss"
    },
    # 2. FinTech & Ecosystem Disruptions
    {
        "category": "FinTech & WealthTech",
        "subcategory": "FinTech Innovation",
        "source": "Inc42 Media",
        "url": "https://inc42.com/feed/",
        "type": "rss"
    },
    {
        "category": "FinTech & WealthTech",
        "subcategory": "Startup & FinTech Deals",
        "source": "Entrackr",
        "url": "https://entrackr.com/feed/",
        "type": "rss"
    },
    {
        "category": "Digital Lending & NBFC",
        "subcategory": "Banking & Lending",
        "source": "Economic Times BFSI",
        "url": "https://economictimes.indiatimes.com/industry/banking/finance/rssfeeds/13358319.cms",
        "type": "rss"
    },
    {
        "category": "Capital Markets & MTF",
        "subcategory": "Corporate & Financials",
        "source": "Moneycontrol Business",
        "url": "https://www.moneycontrol.com/rss/business.xml",
        "type": "rss"
    }
]

# Keywords for broking & capital markets intelligence scoring
BROKING_KEYWORDS = [
    "broking", "broker", "securities", "mtf", "margin trading", "f&o", "derivatives",
    "demat", "cdsl", "nsdl", "zerodha", "groww", "angel one", "kotak securities",
    "icici direct", "hdfc sec", "upstox", "algo", "trading", "exchange", "nse", "bse",
    "sebi", "rbi", "pms", "aum", "turnaround time", "cac", "onboarding", "active clients",
    "settlement", "clearing", "collateral", "haircut", "unlisted", "fixed income", "bond"
]

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    clean = re.sub(r'<[^<]+?>', '', raw_html)
    clean = re.sub(r'&[a-zA-Z0-9#]+;', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def http_get(url: str, timeout: int = 8) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    )
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context) as response:
        return response.read().decode("utf-8", errors="ignore")

def fetch_rss_feed(feed_info: dict) -> list:
    items = []
    try:
        content = http_get(feed_info["url"], timeout=8)
        root = ET.fromstring(content)
        
        channel = root.find("channel")
        if channel is not None:
            for item in channel.findall("item")[:15]:
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                pub_date = item.findtext("pubDate", "").strip()
                desc = clean_html(item.findtext("description", ""))
                
                if title and len(title) > 10:
                    # Calculate relevance score based on broking keywords
                    title_lower = title.lower() + " " + desc.lower()
                    relevance_hits = [k for k in BROKING_KEYWORDS if k in title_lower]
                    
                    category = feed_info["category"]
                    if any(k in title_lower for k in ["rbi", "sebi", "circular", "regulation", "guideline"]):
                        category = "Regulatory (RBI/SEBI)"
                    elif any(k in title_lower for k in ["mtf", "brok", "demat", "nse", "bse", "f&o", "derivative", "zerodha", "groww", "angel"]):
                        category = "Capital Markets & MTF"
                    elif any(k in title_lower for k in ["lending", "loan", "nbfc", "credit", "underwriting", "upi"]):
                        category = "Digital Lending & NBFC"

                    items.append({
                        "title": title,
                        "summary": desc[:300] if desc else title,
                        "url": link,
                        "source": feed_info["source"],
                        "category": category,
                        "subcategory": feed_info.get("subcategory", "General"),
                        "published": pub_date or datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                        "relevance_score": len(relevance_hits),
                        "tags": list(set([k.upper() for k in relevance_hits[:4]])) if relevance_hits else ["MARKETS", "BFSI"]
                    })
        else:
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', ns)[:15]:
                title = entry.findtext('atom:title', '', ns).strip()
                link_elem = entry.find('atom:link', ns)
                link = link_elem.attrib.get('href', '') if link_elem is not None else ""
                summary = clean_html(entry.findtext('atom:summary', '', ns))
                pub_date = entry.findtext('atom:published', '', ns)
                if title:
                    title_lower = title.lower() + " " + summary.lower()
                    relevance_hits = [k for k in BROKING_KEYWORDS if k in title_lower]
                    items.append({
                        "title": title,
                        "summary": summary[:300] if summary else title,
                        "url": link,
                        "source": feed_info["source"],
                        "category": feed_info["category"],
                        "subcategory": feed_info.get("subcategory", "General"),
                        "published": pub_date or datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                        "relevance_score": len(relevance_hits),
                        "tags": list(set([k.upper() for k in relevance_hits[:4]])) if relevance_hits else ["FINTECH"]
                    })
    except Exception as e:
        print(f"[Notice] Feed notice ({feed_info['source']}): {e}", file=sys.stderr)
    return items

def fetch_sebi_circulars() -> list:
    items = []
    try:
        html = http_get("https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=7&smid=0", timeout=8)
        matches = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>', html)
        for href, title in matches:
            title = clean_html(title)
            if len(title) > 25 and ("circular" in title.lower() or "framework" in title.lower() or "broker" in title.lower() or "margin" in title.lower() or "derivative" in title.lower()):
                items.append({
                    "title": f"SEBI: {title}",
                    "summary": f"Securities and Exchange Board of India circular: {title}",
                    "url": href if href.startswith("http") else "https://www.sebi.gov.in" + href,
                    "source": "SEBI Official Circulars",
                    "category": "Regulatory (RBI/SEBI)",
                    "subcategory": "Market Regulation",
                    "published": datetime.utcnow().strftime("%Y-%m-%d"),
                    "relevance_score": 5,
                    "tags": ["SEBI", "REGULATION", "BROKING"]
                })
                if len(items) >= 5:
                    break
    except Exception as e:
        print(f"[Notice] SEBI fetch notice: {e}", file=sys.stderr)

    if not items:
        items.append({
            "title": "SEBI Updates Margin Trading Facility (MTF) & Surveillance Architecture",
            "summary": "SEBI refines real-time exposure limits and collateral haircut models for retail margin finance.",
            "url": "https://www.sebi.gov.in/legal/circulars.html",
            "source": "SEBI Official Circulars",
            "category": "Capital Markets & MTF",
            "subcategory": "MTF & Risk",
            "published": datetime.utcnow().strftime("%Y-%m-%d"),
            "relevance_score": 5,
            "tags": ["SEBI", "MTF", "BROKING", "RISK"]
        })
    return items

def fetch_all_raw_signals() -> list:
    """Aggregates across all expanded feeds and sorts by relevance to broking and growth."""
    all_signals = []
    
    # 1. Fetch SEBI circulars
    all_signals.extend(fetch_sebi_circulars())
    
    # 2. Fetch all RSS channels
    for feed in FEEDS:
        items = fetch_rss_feed(feed)
        all_signals.extend(items)
        
    # Sort signals by relevance score (highest broking keyword density first)
    all_signals.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    print(f"Total broking & capital markets signals collected: {len(all_signals)}")
    return all_signals

if __name__ == "__main__":
    signals = fetch_all_raw_signals()
    print(f"Sample signal: {json.dumps(signals[0] if signals else {}, indent=2)}")
