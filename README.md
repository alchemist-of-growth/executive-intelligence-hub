# Executive Intelligence Hub
### Autonomous Morning Sector & Regulatory Briefing for FinTech & BFSI CXOs

An automated, scheduled intelligence system and mobile-optimized Progressive Web App (PWA) designed for an 8-minute morning habit stack (08:30 AM IST). 

Built for **Nishant Agarwal** (IIT Bombay | XLRI | SVP & Head of Digital Business & Strategy) to scan, distill, and strategize around:
* **RBI Notifications & Master Directions**
* **SEBI Regulatory Circulars & Consultation Papers**
* **FinTech & WealthTech Moves** (Inc42, Entrackr, ET BFSI, VCCircle, Moneycontrol)
* **Digital Lending & Broking/MTF Market Signals**

---

## 📱 Mobile Experience & Features

1. **8-Minute Morning Briefing Deck**: Top 3 Macro Signals + categorized cards with strategic **"P&L & Growth Impact"** breakdowns.
2. **Text-to-Speech (TTS) Audio Player**: Listen to your briefing hands-free during morning walks or commutes (with 1x, 1.25x, 1.5x speed controls).
3. **1-Tap LinkedIn Thought-Leadership Hook**: Instantly generates ready-to-post executive commentary tailored for CGO/CDO positioning.
4. **PWA Mobile Native Experience**: Installable on iPhone (Safari $\rightarrow$ "Add to Home Screen") and Android (Chrome $\rightarrow$ "Install App").
5. **Standalone GitHub Pages Hosting**: Zero server hosting cost, 24/7 global availability from your phone.
6. **Automated GitHub Actions Schedule**: Daily morning cron at 03:00 UTC (08:30 AM IST) that scrapes feeds, synthesizes intelligence via Gemini/Google Antigravity, and commits the fresh daily digest.

---

## 🚀 Quick Setup: Running Standalone on GitHub

### 1. Push to Your GitHub Repository
```bash
cd executive-intelligence-hub
git init
git add .
git commit -m "Initial commit: Executive Intelligence Hub PWA"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/executive-intelligence-hub.git
git push -u origin main
```

### 2. Enable GitHub Pages
1. Go to your repository on GitHub: **Settings $\rightarrow$ Pages**.
2. Under **Build and deployment $\rightarrow$ Source**, select **Deploy from a branch**.
3. Choose `main` branch and `/ (root)` folder, then click **Save**.
4. Your mobile app URL will be: `https://YOUR_USERNAME.github.io/executive-intelligence-hub/`.

### 3. Add Gemini API Key Secret for Daily Scheduled Scan
1. Go to **Settings $\rightarrow$ Secrets and variables $\rightarrow$ Actions**.
2. Click **New repository secret**.
3. Name: `GEMINI_API_KEY`
4. Value: Your Gemini API Key (from [Google AI Studio](https://aistudio.google.com/app/api-keys)).
5. Under **Settings $\rightarrow$ Actions $\rightarrow$ General $\rightarrow$ Workflow permissions**, select **"Read and write permissions"** so GitHub Actions can commit the fresh daily briefing JSON.

---

## 💻 Running Locally (Optional)

You can also run the scanner and preview server locally on your laptop:

```bash
# 1. Install dependencies
cd executive-intelligence-hub/backend
pip install -r requirements.txt

# 2. Run the intelligence scan
export GEMINI_API_KEY="your-gemini-key"
python run_daily_scan.py

# 3. Start local server
python server.py
# Open http://localhost:8000 on your laptop or phone (on the same Wi-Fi)
```

---

## 📂 Project Architecture

```
executive-intelligence-hub/
├── .github/
│   └── workflows/
│       └── daily_briefing.yml    # Daily 08:30 AM IST scheduled cron workflow
├── backend/
│   ├── fetch_intelligence.py     # Scrapes RBI, SEBI, Inc42, Entrackr, ET BFSI, etc.
│   ├── synthesize_briefing.py   # Gemini / Google Antigravity distillation engine
│   ├── run_daily_scan.py         # Master pipeline script
│   ├── server.py                 # Optional local FastAPI/HTTP server
│   └── requirements.txt          # Python dependencies
├── data/
│   ├── briefing_today.json       # Current day's briefing
│   └── archive.json              # Historical briefings archive
├── index.html                    # Mobile PWA entry point
├── styles.css                    # Executive UI & responsive mobile styles
├── app.js                        # Client-side audio player, filters & LinkedIn generator
├── manifest.json                 # PWA Web Manifest
├── service-worker.js             # Offline caching service worker
└── README.md
```
