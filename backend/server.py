"""
server.py
Lightweight FastAPI / HTTP server to serve the Executive Command Center mobile web app and API locally.
"""

import os
import json
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FRONTEND_DIR = BASE_DIR

app = FastAPI(title="Executive Intelligence Hub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/briefing/today")
def get_today_briefing():
    today_file = os.path.join(DATA_DIR, "briefing_today.json")
    if os.path.exists(today_file):
        with open(today_file, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Today's briefing has not been generated yet.")

@app.get("/api/briefing/archive")
def get_archive():
    archive_file = os.path.join(DATA_DIR, "archive.json")
    if os.path.exists(archive_file):
        with open(archive_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def run_scan_task():
    try:
        from run_daily_scan import main as run_scan
        run_scan()
    except Exception as e:
        print(f"Error during async scan task: {e}")

@app.post("/api/briefing/refresh")
def trigger_refresh(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_scan_task)
    return {"status": "success", "message": "Live intelligence scan initiated in background."}

class AngleRequest(BaseModel):
    headline: str
    summary: str
    pl_impact: str

@app.post("/api/generate-angle")
def generate_angle(req: AngleRequest):
    # Generates a customized LinkedIn thought leadership draft
    draft = f"""🚀 Strategic Lens on Indian BFSI & FinTech: {req.headline}

In scaling digital businesses and retail distribution models, regulatory shifts and market structural changes aren't roadblocks—they are unit-economics moats for teams that execute fast.

Key takeaway:
{req.summary}

The P&L & Commercial Reality:
{req.pl_impact}

For digital leaders and platforms, the playbook is clear: optimize turnaround time, reduce onboarding friction, and build automated self-service rails before margin compression forces your hand.

How is your team positioning for this shift?

#FinTech #BFSI #Growth #DigitalLending #WealthTech #Leadership #Strategy"""
    return {"draft": draft}

# Mount static frontend
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("Starting Executive Intelligence Hub at http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
