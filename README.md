# ⚽ FootyWatch

**FootyWatch** is a lightweight web app that displays upcoming football (soccer) matches using the [Football-Data.org](https://www.football-data.org/) API.

The project is built with **FastAPI** on the backend and a simple **HTML + JavaScript** interface on the frontend, containerized with **Docker** and ready for one-click deployment to the cloud.

---

## 🚀 Features
- Fetch upcoming matches by **league** or **team**
- Live integration with Football-Data.org
- Minimal, clean interface built with vanilla JS
- Ready-to-deploy **Docker** container (“black box”)
- Optional hosting on **Render** (free tier)

---

## 🧩 Tech Stack
- **Backend:** FastAPI (Python 3.12)
- **Frontend:** HTML + JavaScript
- **API Client:** httpx
- **Hosting:** Render (Docker)
- **Data Source:** Football-Data.org

---

## ⚙️ Run Locally
```bash
git clone https://github.com/<your-username>/footywatch.git
cd footywatch
python -m venv .venv
# Activate (Windows)
.venv\Scripts\activate
# Activate (macOS/Linux)
source .venv/bin/activate

pip install -r requirements.txt
Create a .env file:

FOOTBALL_DATA_TOKEN=your_api_token_here


Run the app:

uvicorn server:app --reload


Open your browser:

http://127.0.0.1:8000/app

🐳 Run with Docker
docker build -t footywatch:latest .
docker run --rm -p 8000:8000 \
  -e FOOTBALL_DATA_TOKEN=your_api_token_here \
  footywatch:latest


Then visit:

http://localhost:8000/app

☁️ Deploy on Render (Free)

Push your repo to GitHub

Go to Render.com
 → New → Web Service

Select your repo

Choose Environment: Docker

Add an environment variable:

Key	Value
FOOTBALL_DATA_TOKEN	your_api_token_here

Click Create Web Service

Your app will be available at something like:
https://footywatch.onrender.com/app

🕒 Render free tier includes 750 monthly hours per workspace and may “sleep” after inactivity. The first request will wake it up (cold start).

📁 Project Structure
footywatch/
├─ server.py          # FastAPI routes + static files
├─ services.py        # Football-Data.org integration
├─ static/
│  └─ index.html      # Frontend (HTML + JS)
├─ requirements.txt   # Python dependencies
├─ Dockerfile         # Docker build instructions
└─ README.md

💡 Future Improvements

League standings view

Local timezone conversion

In-memory caching or scheduler

Database persistence (PostgreSQL / SQLite)

Author: Shahar baram
Industrial Engineering & Management – BGU
Project: FootyWatch (Football Data API Demo)