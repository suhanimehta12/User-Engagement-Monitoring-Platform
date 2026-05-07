# 📊 GA4 User Engagement Analytics Dashboard

> A production-ready analytics dashboard built with **Streamlit**, **Chart.js**, **Tailwind CSS**, and **Python** — visualising Google Analytics 4 engagement data with a clean editorial UI.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/cloud)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Feature | Details |
|---|---|
| **KPI Cards** | Total events, users, avg events/user, top event |
| **Insight Strip** | Key stats pulled directly from GA4 data |
| **Time-Series Chart** | 30-day simulated engagement trend with filter buttons |
| **Donut Chart** | Event distribution with custom legend |
| **Horizontal Bar** | Events per active user by event type |
| **Bubble Chart** | User reach × activity scatter |
| **Data Table** | Summary with engagement score bars |
| **CSV Export** | One-click download of processed data |

---

## 🏗️ Project Structure

```
ga4-dashboard/
├── app.py                    ← Streamlit entry point (frontend + backend)
├── requirements.txt          ← Python dependencies
├── .gitignore
├── data/
│   └── ga4_data.csv          ← GA4 export data
├── backend/
│   └── ga4_analysis.py       ← Analytics engine (standalone or imported)
├── .streamlit/
│   └── config.toml           ← Streamlit theme config
└── README.md
```

---

## 🚀 Run Locally

### Step 1 — Clone / unzip

```bash
# If cloned from GitHub:
git clone https://github.com/YOUR_USERNAME/ga4-dashboard.git
cd ga4-dashboard

# If using the zip:
unzip ga4-dashboard.zip
cd ga4-dashboard
```

### Step 2 — Create virtual environment (recommended)

```bash
python -m venv venv

# Activate:
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Run the dashboard

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser. 🎉

---

## ☁️ Deploy Live (Free — Streamlit Community Cloud)

> **Prerequisite**: Push this project to a public GitHub repo first.

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit — GA4 dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ga4-dashboard.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository**: `YOUR_USERNAME/ga4-dashboard`
   - **Branch**: `main`
   - **Main file**: `app.py`
5. Click **"Deploy"** → live in ~60 seconds ✅

Your dashboard will be live at:
```
https://YOUR_USERNAME-ga4-dashboard-app-XXXXX.streamlit.app
```

---

## 🐳 Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t ga4-dashboard .
docker run -p 8501:8501 ga4-dashboard
```

---

## 🔌 Using Real GA4 Data

Replace `data/ga4_data.csv` with a real GA4 export. The CSV must follow this schema:

```csv
Event name,Event count,Total users,Event count per active user,Total revenue
scroll,903,5,180.6,0
page_view,463,10,46.3,0
```

Or connect the GA4 API directly (add to `backend/ga4_analysis.py`):

```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

client = BetaAnalyticsDataClient()  # set GOOGLE_APPLICATION_CREDENTIALS env var
request = RunReportRequest(
    property="properties/YOUR_PROPERTY_ID",
    date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
    dimensions=[Dimension(name="eventName")],
    metrics=[
        Metric(name="eventCount"),
        Metric(name="totalUsers"),
        Metric(name="eventCountPerUser"),
    ],
)
response = client.run_report(request)
```

---

## 📈 Key Insights from Sample Data

- **Scroll** dominates at **47.9%** of total events — users engage deeply with content
- **Page View** accounts for **24.6%** — healthy traffic ratio
- **Scroll events per active user = 180.6** — extremely high engagement depth
- `first_visit` and `session_start` parity confirms single-session new users

---

## 🛠️ Tech Stack

- **Python 3.11** — backend analytics engine
- **Streamlit 1.35** — web server & component rendering
- **Pandas / NumPy** — data processing & simulation
- **Matplotlib / Seaborn** — static chart generation
- **Chart.js 4.4** — interactive frontend charts
- **Tailwind CSS (CDN)** — utility-first styling
- **Vanilla JS** — zero-framework interactivity
- **Google Fonts** — Clash Display + DM Mono typography

---

## 📄 License

MIT © 2025
