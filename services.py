# services.py
import os
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional

import httpx

FOOTBALL_DATA_TOKEN = os.getenv("FOOTBALL_DATA_TOKEN", "").strip()
FD_BASE = "https://api.football-data.org/v4"

def _client() -> httpx.Client:
    headers = {}
    if FOOTBALL_DATA_TOKEN:
        headers["X-Auth-Token"] = FOOTBALL_DATA_TOKEN
    return httpx.Client(timeout=25.0, headers=headers)

def _get(url: str, params: Dict = None) -> Dict:
    with _client() as c:
        r = c.get(url, params=params or {})
        r.raise_for_status()
        return r.json()

# ---------- עזרי זמן ----------
def _today_utc_date() -> date:
    return datetime.utcnow().date()

def _ymd(d: date) -> str:
    return d.strftime("%Y-%m-%d")

# ---------- איתור ליגה לפי *שם* → קוד תחרות (PL, PD, SA, BL1, FL1, UCL, וכו') ----------
def fd_competition_by_name(name: str) -> Optional[Dict]:
    """
    קורא /competitions ומחזיר {"code": "PL", "id": 2021, "name": "..."} התאמה גמישה בשם.
    """
    if not name:
        return None
    target = name.strip().lower()
    data = _get(f"{FD_BASE}/competitions")
    best = None
    for comp in data.get("competitions", []):
        nm = (comp.get("name") or "").strip()
        if not nm:
            continue
        if target in nm.lower() or nm.lower() in target:
            # מעדיפים Tier One ואז שם הכי דומה
            if best is None:
                best = comp
            else:
                if (comp.get("plan") == "TIER_ONE") and (best.get("plan") != "TIER_ONE"):
                    best = comp
    if not best:
        return None
    return {"code": best.get("code"), "id": best.get("id"), "name": best.get("name")}

# ---------- רשימת קבוצות של ליגה (לעזור לחיפוש קבוצה) ----------
def fd_teams_in_competition(code: str) -> List[Dict]:
    if not code:
        return []
    data = _get(f"{FD_BASE}/competitions/{code}/teams")
    out = []
    for t in data.get("teams", []):
        out.append({
            "id": t.get("id"),
            "name": t.get("name"),
            "shortName": t.get("shortName"),
            "tla": t.get("tla"),
            "crest": t.get("crest"),
        })
    return out

def fd_find_team_in_comp(code: str, team_name: str) -> Optional[Dict]:
    if not code or not team_name:
        return None
    cand = [t for t in fd_teams_in_competition(code) if team_name.lower() in (t["name"] or "").lower()]
    if cand:
        # החזרה של ההתאמה "הכי ארוכה" בשם
        cand.sort(key=lambda x: len(x["name"] or ""), reverse=True)
        return cand[0]
    #Fallback: חיפוש לפי shortName או TLA
    teams = fd_teams_in_competition(code)
    for t in teams:
        if team_name.lower() in (t.get("shortName") or "").lower() or team_name.lower() == (t.get("tla") or "").lower():
            return t
    return None

# ---------- משחקים קרובים *בליגה* לפי שם ליגה ----------
def fd_upcoming_league_matches_by_name(league_name: str, days: int = 7) -> List[Dict]:
    comp = fd_competition_by_name(league_name)
    if not comp or not comp.get("code"):
        return []
    code = comp["code"]  # לדוגמה "PL"
    today = _today_utc_date()
    to = today + timedelta(days=max(1, min(days, 30)))
    params = {
        "dateFrom": _ymd(today),
        "dateTo": _ymd(to),
        "status": "SCHEDULED",
        # אפשר להוסיף filters אחרים לפי הצורך (stage/matchday וכו')
    }
    data = _get(f"{FD_BASE}/competitions/{code}/matches", params)
    out = []
    for m in data.get("matches", []):
        out.append({
            "competition": comp["name"],
            "competitionCode": code,
            "utcDate": m.get("utcDate"),
            "status": m.get("status"),
            "matchday": m.get("matchday"),
            "home": m.get("homeTeam", {}).get("name"),
            "away": m.get("awayTeam", {}).get("name"),
            "venue": None,  # football-data לא תמיד נותן venue; אפשר לשדרג בהמשך
            "id": m.get("id"),
        })
    # מיון לפי זמן
    out.sort(key=lambda x: x["utcDate"] or "9999-12-31T00:00:00Z")
    return out

# ---------- משחקים קרובים *לקבוצה* (עם ליגה לבחירה או ברירת מחדל) ----------
def fd_upcoming_team_matches(team_name: str, league_name: str = "English Premier League", days: int = 7) -> List[Dict]:
    comp = fd_competition_by_name(league_name)
    if not comp or not comp.get("code"):
        return []
    code = comp["code"]
    team = fd_find_team_in_comp(code, team_name)
    if not team or not team.get("id"):
        return []
    team_id = team["id"]

    today = _today_utc_date()
    to = today + timedelta(days=max(1, min(days, 60)))
    params = {
        "dateFrom": _ymd(today),
        "dateTo": _ymd(to),
        "status": "SCHEDULED",
        "competitions": comp["id"],  # להגביל לליגה הזו
    }
    data = _get(f"{FD_BASE}/teams/{team_id}/matches", params)
    out = []
    for m in data.get("matches", []):
        out.append({
            "competition": m.get("competition", {}).get("name"),
            "competitionCode": code,
            "utcDate": m.get("utcDate"),
            "status": m.get("status"),
            "matchday": m.get("matchday"),
            "home": m.get("homeTeam", {}).get("name"),
            "away": m.get("awayTeam", {}).get("name"),
            "venue": None,
            "id": m.get("id"),
        })
    out.sort(key=lambda x: x["utcDate"] or "9999-12-31T00:00:00Z")
    return out
