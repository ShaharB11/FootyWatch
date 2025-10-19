# server.py
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import services as svc

app = FastAPI(title="FootyWatch (Football-Data.org)")

# CORS לפיתוח
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# הגשת ה-UI הסטטי
if os.path.isdir("static"):
    app.mount("/app", StaticFiles(directory="static", html=True), name="app")

@app.get("/health")
def health():
    return {"ok": True}

# -------- ליגה לפי שם: משחקים קרובים --------
@app.get("/api/fd/league-matches")
def fd_league_matches(
    league_name: str = Query(..., min_length=2),
    days: int = Query(7, ge=1, le=30)
):
    out = svc.fd_upcoming_league_matches_by_name(league_name, days=days)
    if out is None:
        raise HTTPException(status_code=502, detail="Provider error")
    return out

# -------- קבוצה לפי שם (בתוך ליגה): משחקים קרובים --------
@app.get("/api/fd/team-matches")
def fd_team_matches(
    team_name: str = Query(..., min_length=2),
    league_name: str = Query("English Premier League"),
    days: int = Query(7, ge=1, le=60),
):
    out = svc.fd_upcoming_team_matches(team_name, league_name, days=days)
    if out is None:
        raise HTTPException(status_code=502, detail="Provider error")
    return out
