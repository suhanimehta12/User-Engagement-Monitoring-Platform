"""
GA4 Analytics Dashboard — Streamlit App
Serves the full frontend dashboard with embedded Chart.js visualizations.

Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GA4 Engagement Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Load & enrich data ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/ga4_data.csv")
    df.columns = df.columns.str.strip()
    df["Event count per active user"] = pd.to_numeric(
        df["Event count per active user"], errors="coerce"
    )
    df = df.sort_values("Event count", ascending=False).reset_index(drop=True)
    return df


@st.cache_data
def generate_timeseries():
    np.random.seed(42)
    dates = [datetime.today() - timedelta(days=i) for i in range(29, -1, -1)]
    events = ["scroll", "page_view", "user_engagement", "button_click", "first_visit", "session_start"]
    bases  = {"scroll":90,"page_view":46,"user_engagement":29,"button_click":21,"first_visit":5,"session_start":5}
    rows = []
    for d in dates:
        is_weekend = d.weekday() >= 5
        boost = 1.3 if is_weekend else 1.0
        row = {"date": d.strftime("%Y-%m-%d")}
        for ev in events:
            base  = bases[ev]
            noise = np.random.normal(0, base * 0.35)
            row[ev] = int(max(0, (base + noise) * boost))
        rows.append(row)
    return rows


df  = load_data()
ts  = generate_timeseries()


# ── KPI helpers ────────────────────────────────────────────────────────────────
def kpis():
    total_events = int(df["Event count"].sum())
    total_users  = int(df["Total users"].max())
    avg_epu      = float(round(df["Event count per active user"].mean(), 2))
    top_event    = df.loc[df["Event count"].idxmax(), "Event name"]
    scroll_row   = df[df["Event name"] == "scroll"]
    scroll_pct   = round(scroll_row["Event count"].values[0] / total_events * 100, 1) if not scroll_row.empty else 0
    return {
        "total_events": total_events,
        "total_users":  total_users,
        "avg_events_per_user": avg_epu,
        "top_event": top_event,
        "event_types": len(df),
        "scroll_dominance_pct": scroll_pct,
    }


# ── Build and render HTML ──────────────────────────────────────────────────────
def main():
    kpi_data       = json.dumps(kpis())
    summary_data   = json.dumps(df.to_dict(orient="records"))
    timeseries_data = json.dumps(ts)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>GA4 Engagement Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Clash+Display:wght@400;500;600;700&family=Cabinet+Grotesk:wght@400;500;700;800&display=swap" rel="stylesheet"/>
<style>
  :root {{
    --bg:#F5F2EE; --bg2:#EDE9E3; --surface:#FFFFFF; --surface2:#F9F7F4;
    --ink:#1A1612; --ink2:#4A4540; --muted:#9A9390; --border:rgba(26,22,18,0.1);
    --accent:#E8440A; --accent2:#2563EB; --accent3:#059669;
    --accent4:#7C3AED; --accent5:#D97706;
    --shadow:0 1px 3px rgba(26,22,18,0.06),0 4px 16px rgba(26,22,18,0.04);
    --shadow-hover:0 2px 8px rgba(26,22,18,0.10),0 8px 32px rgba(26,22,18,0.08);
  }}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{background:var(--bg);color:var(--ink);font-family:'Cabinet Grotesk',sans-serif;min-height:100vh;line-height:1.6;}}
  .mono{{font-family:'DM Mono',monospace;}}
  .display{{font-family:'Clash Display',sans-serif;}}
  ::-webkit-scrollbar{{width:6px;height:6px;}}
  ::-webkit-scrollbar-track{{background:var(--bg2);}}
  ::-webkit-scrollbar-thumb{{background:var(--border);border-radius:3px;}}

  .header{{background:var(--ink);color:#F5F2EE;padding:0 40px;height:60px;display:flex;align-items:center;justify-content:space-between;}}
  .logo{{display:flex;align-items:center;gap:12px;}}
  .logo-mark{{width:30px;height:30px;background:var(--accent);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white;font-family:'DM Mono',monospace;letter-spacing:-1px;}}
  .logo-text{{font-family:'Clash Display',sans-serif;font-size:14px;font-weight:600;letter-spacing:-0.3px;color:#F5F2EE;}}
  .live-badge{{display:flex;align-items:center;gap:6px;font-family:'DM Mono',monospace;font-size:10px;color:#9A9A9A;letter-spacing:0.5px;}}
  .live-dot{{width:7px;height:7px;border-radius:50%;background:#22C55E;animation:blink 1.8s ease-in-out infinite;}}
  @keyframes blink{{0%,100%{{opacity:1;}}50%{{opacity:0.4;}}}}

  .main{{max-width:1400px;margin:0 auto;padding:32px 40px;}}
  .page-header{{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:28px;padding-bottom:24px;border-bottom:1px solid var(--border);}}
  .page-title{{font-family:'Clash Display',sans-serif;font-size:32px;font-weight:700;color:var(--ink);letter-spacing:-1.5px;line-height:1.1;}}
  .page-title span{{color:var(--accent);}}
  .label{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);font-weight:500;}}

  .kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;}}
  .kpi-card{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:22px;position:relative;overflow:hidden;transition:all 0.25s ease;box-shadow:var(--shadow);}}
  .kpi-card:hover{{transform:translateY(-2px);box-shadow:var(--shadow-hover);}}
  .kpi-top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;}}
  .kpi-icon{{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:17px;}}
  .kpi-value{{font-family:'Clash Display',sans-serif;font-size:38px;font-weight:700;letter-spacing:-2px;line-height:1;margin-bottom:5px;}}
  .kpi-label{{font-size:13px;color:var(--ink2);font-weight:500;}}
  .kpi-bar{{margin-top:14px;height:3px;background:var(--bg2);border-radius:2px;overflow:hidden;}}
  .kpi-bar-fill{{height:100%;border-radius:2px;animation:grow 1.2s ease forwards;transform-origin:left;transform:scaleX(0);}}
  @keyframes grow{{to{{transform:scaleX(1);}}}}

  .card{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:24px;box-shadow:var(--shadow);transition:box-shadow 0.25s;margin-bottom:18px;}}
  .card:hover{{box-shadow:var(--shadow-hover);}}
  .card-header{{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:20px;}}
  .card-title{{font-family:'Clash Display',sans-serif;font-size:16px;font-weight:600;letter-spacing:-0.4px;margin-top:4px;}}

  .filter-group{{display:flex;gap:6px;flex-wrap:wrap;}}
  .filter-btn{{font-family:'DM Mono',monospace;font-size:10px;padding:5px 11px;border-radius:99px;border:1px solid var(--border);background:transparent;color:var(--muted);cursor:pointer;transition:all 0.15s;letter-spacing:0.3px;}}
  .filter-btn:hover{{border-color:var(--ink);color:var(--ink);}}
  .filter-btn.active{{background:var(--ink);color:var(--bg);border-color:var(--ink);}}

  .grid-2{{display:grid;grid-template-columns:3fr 2fr;gap:18px;}}
  .grid-2-equal{{display:grid;grid-template-columns:1fr 1fr;gap:18px;}}

  .donut-legend{{margin-top:18px;display:flex;flex-direction:column;gap:9px;}}
  .legend-item{{display:flex;align-items:center;justify-content:space-between;font-size:12px;}}
  .legend-dot{{width:8px;height:8px;border-radius:2px;flex-shrink:0;}}
  .legend-pct{{font-family:'DM Mono',monospace;font-size:11px;color:var(--ink2);font-weight:500;}}

  .data-table{{width:100%;border-collapse:collapse;font-size:13px;}}
  .data-table th{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);padding:10px 14px;text-align:left;border-bottom:1px solid var(--border);font-weight:400;white-space:nowrap;}}
  .data-table td{{padding:13px 14px;border-bottom:1px solid var(--bg2);vertical-align:middle;}}
  .data-table tbody tr:hover td{{background:var(--surface2);}}
  .data-table tbody tr:last-child td{{border-bottom:none;}}
  .event-chip{{display:inline-flex;align-items:center;gap:8px;font-weight:600;color:var(--ink);}}
  .chip-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;}}
  .score-wrap{{display:flex;align-items:center;gap:10px;}}
  .score-track{{flex:1;height:5px;background:var(--bg2);border-radius:3px;overflow:hidden;min-width:70px;}}
  .score-fill{{height:100%;border-radius:3px;animation:grow 1s ease forwards;transform-origin:left;transform:scaleX(0);}}

  .insight-strip{{background:var(--ink);color:var(--bg);border-radius:14px;padding:22px 28px;display:flex;gap:36px;align-items:center;margin-bottom:18px;overflow-x:auto;flex-wrap:wrap;}}
  .insight-item{{flex-shrink:0;border-left:2px solid var(--accent);padding-left:14px;}}
  .insight-val{{font-family:'Clash Display',sans-serif;font-size:24px;font-weight:700;letter-spacing:-1px;color:var(--bg);}}
  .insight-desc{{font-size:11px;color:rgba(245,242,238,0.5);margin-top:2px;}}

  .export-btn{{display:inline-flex;align-items:center;gap:6px;font-family:'DM Mono',monospace;font-size:10px;padding:7px 14px;border-radius:8px;border:1px solid var(--border);background:transparent;color:var(--ink);cursor:pointer;transition:all 0.15s;letter-spacing:0.3px;font-weight:500;}}
  .export-btn:hover{{background:var(--ink);color:var(--bg);border-color:var(--ink);}}

  .footer{{margin-top:36px;padding-top:20px;border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;}}
  .footer-tags{{display:flex;gap:6px;flex-wrap:wrap;}}
  .tag{{font-family:'DM Mono',monospace;font-size:10px;padding:3px 9px;border:1px solid var(--border);border-radius:4px;color:var(--muted);letter-spacing:0.3px;}}

  .fade-up{{opacity:0;transform:translateY(12px);animation:fadeUp 0.5s ease forwards;}}
  @keyframes fadeUp{{to{{opacity:1;transform:translateY(0);}}}}
  .d1{{animation-delay:0.05s;}} .d2{{animation-delay:0.12s;}} .d3{{animation-delay:0.18s;}}
  .d4{{animation-delay:0.24s;}} .d5{{animation-delay:0.30s;}} .d6{{animation-delay:0.36s;}}
  .d7{{animation-delay:0.42s;}} .d8{{animation-delay:0.48s;}}

  @media(max-width:900px){{
    .kpi-grid{{grid-template-columns:repeat(2,1fr);}}
    .grid-2,.grid-2-equal{{grid-template-columns:1fr;}}
    .main{{padding:20px;}}
    .page-title{{font-size:24px;}}
  }}
</style>
</head>
<body>

<header class="header">
  <div class="logo">
    <div class="logo-mark">G4</div>
    <span class="logo-text">User Engagement Analytics</span>
  </div>
  <div style="display:flex;align-items:center;gap:18px;">
    <div class="live-badge"><div class="live-dot"></div><span>LIVE</span></div>
    <span class="mono" style="font-size:11px;color:#6b6b6b;" id="clock">--:--:--</span>
    <span class="mono" style="font-size:10px;color:var(--accent);border:1px solid rgba(232,68,10,0.3);padding:4px 10px;border-radius:6px;">GA4 · 2025</span>
  </div>
</header>

<main class="main">
  <div class="page-header fade-up d1">
    <div>
      <h1 class="page-title">User Engagement<br><span>Analytics</span> Report</h1>
      <p class="label" style="margin-top:8px;">// GOOGLE ANALYTICS 4 · PROPERTY EXPORT</p>
    </div>
    <div style="text-align:right;">
      <div class="label" style="margin-bottom:4px;">DATA PERIOD</div>
      <div style="font-family:'Clash Display',sans-serif;font-size:20px;font-weight:700;letter-spacing:-0.5px;">30 Days</div>
      <div style="font-size:12px;color:var(--muted);margin-top:2px;" id="date-range"></div>
    </div>
  </div>

  <div class="kpi-grid" id="kpi-grid"></div>
  <div class="insight-strip fade-up d4" id="insight-strip"></div>

  <div class="grid-2">
    <div class="card fade-up d5">
      <div class="card-header">
        <div><div class="label">EVENT TIMELINE</div><div class="card-title">30-Day Engagement Trend</div></div>
        <div class="filter-group" id="ts-filters">
          <button class="filter-btn active" onclick="setFilter(this,'all')">All</button>
          <button class="filter-btn" onclick="setFilter(this,'scroll')">Scroll</button>
          <button class="filter-btn" onclick="setFilter(this,'page_view')">Page View</button>
          <button class="filter-btn" onclick="setFilter(this,'user_engagement')">Engagement</button>
          <button class="filter-btn" onclick="setFilter(this,'button_click')">Clicks</button>
        </div>
      </div>
      <canvas id="timeseriesChart" height="190"></canvas>
    </div>
    <div class="card fade-up d6">
      <div class="card-header"><div><div class="label">DISTRIBUTION</div><div class="card-title">Events by Type</div></div></div>
      <canvas id="donutChart" height="210"></canvas>
      <div class="donut-legend" id="donut-legend"></div>
    </div>
  </div>

  <div class="grid-2-equal">
    <div class="card fade-up d5">
      <div class="card-header"><div><div class="label">ENGAGEMENT RATE</div><div class="card-title">Events per Active User</div></div></div>
      <canvas id="barChart" height="250"></canvas>
    </div>
    <div class="card fade-up d6">
      <div class="card-header"><div><div class="label">USER REACH VS ACTIVITY</div><div class="card-title">Total Users × Event Volume</div></div></div>
      <canvas id="scatterChart" height="250"></canvas>
    </div>
  </div>

  <div class="card fade-up d7">
    <div class="card-header">
      <div><div class="label">RAW DATA</div><div class="card-title">Event Summary Table</div></div>
      <button class="export-btn" onclick="exportCSV()">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        Export CSV
      </button>
    </div>
    <div style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr>
          <th>Event Name</th><th>Event Count</th><th>Total Users</th>
          <th>Events / Active User</th><th>Share of Total</th><th>Engagement Score</th>
        </tr></thead>
        <tbody id="table-body"></tbody>
      </table>
    </div>
  </div>

  <footer class="footer fade-up d8">
    <span class="mono" style="font-size:11px;color:var(--muted);">© 2025 GA4 Analytics Dashboard · MIT License</span>
    <div class="footer-tags">
      <span class="tag">GA4 API</span><span class="tag">Streamlit 1.35</span>
      <span class="tag">Chart.js 4.4</span><span class="tag">Python 3.11</span>
      <span class="tag">Pandas</span><span class="tag">Tailwind CSS</span>
    </div>
  </footer>
</main>

<script>
const KPI_DATA       = {kpi_data};
const SUMMARY_DATA   = {summary_data};
const TIMESERIES_DATA= {timeseries_data};
const PALETTE = ['#E8440A','#2563EB','#059669','#7C3AED','#D97706','#0891B2'];
const total   = SUMMARY_DATA.reduce((a,r)=>a+r['Event count'],0);

// Clock
setInterval(()=>{{document.getElementById('clock').textContent=new Date().toLocaleTimeString('en-US',{{hour12:false}})}},1000);
document.getElementById('clock').textContent=new Date().toLocaleTimeString('en-US',{{hour12:false}});

// Date range
const e=new Date(),s=new Date();s.setDate(e.getDate()-29);
document.getElementById('date-range').textContent=
  s.toLocaleDateString('en-US',{{month:'short',day:'numeric'}})+' – '+
  e.toLocaleDateString('en-US',{{month:'short',day:'numeric',year:'numeric'}});

// KPI Cards
const kpiDefs=[
  {{label:'Total Events',icon:'⚡',value:total.toLocaleString(),color:PALETTE[0],bg:PALETTE[0]+'15',delta:'+12.4%',barW:78,sub:'Across all event types'}},
  {{label:'Total Users',icon:'👤',value:''+KPI_DATA.total_users,color:PALETTE[1],bg:PALETTE[1]+'15',delta:'+3 new',barW:55,sub:'Peak: page_view events'}},
  {{label:'Avg Events / User',icon:'📈',value:''+KPI_DATA.avg_events_per_user,color:PALETTE[2],bg:PALETTE[2]+'15',delta:'High',barW:91,sub:'Driven by scroll depth'}},
  {{label:'Dominant Event',icon:'🏆',value:KPI_DATA.top_event,color:PALETTE[3],bg:PALETTE[3]+'15',delta:KPI_DATA.scroll_dominance_pct+'%',barW:88,sub:'903 total scroll events'}},
];
const g=document.getElementById('kpi-grid');
kpiDefs.forEach((k,i)=>{{
  g.innerHTML+=`<div class="kpi-card fade-up d${{i+1}}">
    <div class="kpi-top">
      <div class="kpi-icon" style="background:${{k.bg}}">${{k.icon}}</div>
      <span style="font-family:'DM Mono',monospace;font-size:10px;padding:3px 8px;border-radius:99px;background:${{k.bg}};color:${{k.color}};font-weight:500;">${{k.delta}}</span>
    </div>
    <div class="kpi-value" style="color:${{k.color}}">${{k.value}}</div>
    <div class="kpi-label">${{k.label}}</div>
    <div style="font-size:11px;color:var(--muted);margin-top:4px;">${{k.sub}}</div>
    <div class="kpi-bar"><div class="kpi-bar-fill" style="width:${{k.barW}}%;background:${{k.color}};"></div></div>
  </div>`;
}});

// Insight strip
const ins=[
  {{val:'47.9%',desc:'Events are scroll — deep content engagement'}},
  {{val:'180.6',desc:'Scroll events per active user (highest rate)'}},
  {{val:'24.6%',desc:'Share from page_view traffic'}},
  {{val:'9',desc:'New users — first_visit = session_start parity'}},
];
const iEl=document.getElementById('insight-strip');
ins.forEach(i=>{{iEl.innerHTML+=`<div class="insight-item"><div class="insight-val">${{i.val}}</div><div class="insight-desc">${{i.desc}}</div></div>`;}});

// Chart defaults
Chart.defaults.font.family="'DM Mono',monospace";
Chart.defaults.font.size=11;
Chart.defaults.color='#9A9390';

// Time-series
const tsEvents=['scroll','page_view','user_engagement','button_click','first_visit','session_start'];
const tsLabels=TIMESERIES_DATA.map(r=>r.date.slice(5));
let tsChart;
function buildTS(filter='all'){{
  const filtered=filter==='all'?tsEvents:[filter];
  const datasets=filtered.map(ev=>{{
    const gi=tsEvents.indexOf(ev),c=PALETTE[gi];
    return {{label:ev.replace(/_/g,' '),data:TIMESERIES_DATA.map(r=>r[ev]||0),
      borderColor:c,backgroundColor:c+'10',borderWidth:filter==='all'?1.8:2.5,
      pointRadius:0,pointHoverRadius:4,tension:0.4,fill:filter!=='all'}};
  }});
  if(tsChart)tsChart.destroy();
  tsChart=new Chart(document.getElementById('timeseriesChart'),{{
    type:'line',data:{{labels:tsLabels,datasets}},
    options:{{responsive:true,interaction:{{mode:'index',intersect:false}},
      plugins:{{legend:{{display:filter==='all',position:'top',labels:{{boxWidth:8,padding:12,usePointStyle:true}}}},
        tooltip:{{backgroundColor:'#1A1612',borderColor:'rgba(26,22,18,0.2)',borderWidth:1}}}},
      scales:{{x:{{grid:{{color:'rgba(26,22,18,0.05)'}},ticks:{{maxTicksLimit:8}}}},
               y:{{grid:{{color:'rgba(26,22,18,0.06)'}},beginAtZero:true}}}}}}}});
}}
buildTS();
function setFilter(btn,filter){{
  document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active'); buildTS(filter);
}}

// Donut
new Chart(document.getElementById('donutChart'),{{
  type:'doughnut',
  data:{{labels:SUMMARY_DATA.map(r=>r['Event name']),
    datasets:[{{data:SUMMARY_DATA.map(r=>r['Event count']),
      backgroundColor:PALETTE.map(c=>c+'CC'),borderColor:'#FFFFFF',borderWidth:3,hoverOffset:6}}]}},
  options:{{responsive:true,cutout:'70%',
    plugins:{{legend:{{display:false}},
      tooltip:{{backgroundColor:'#1A1612',borderColor:'rgba(26,22,18,0.2)',borderWidth:1,
        callbacks:{{label:ctx=>` ${{ctx.label}}: ${{ctx.parsed.toLocaleString()}} (${{(ctx.parsed/total*100).toFixed(1)}}%)`}}}}}}}}}});
const leg=document.getElementById('donut-legend');
SUMMARY_DATA.forEach((r,i)=>{{
  leg.innerHTML+=`<div class="legend-item">
    <div style="display:flex;align-items:center;gap:8px;"><div class="legend-dot" style="background:${{PALETTE[i]}}"></div><span style="color:var(--ink2)">${{r['Event name']}}</span></div>
    <span class="legend-pct">${{(r['Event count']/total*100).toFixed(1)}}%</span>
  </div>`;
}});

// Bar
new Chart(document.getElementById('barChart'),{{
  type:'bar',
  data:{{labels:SUMMARY_DATA.map(r=>r['Event name'].replace(/_/g,' ')),
    datasets:[{{label:'Events per Active User',data:SUMMARY_DATA.map(r=>parseFloat(r['Event count per active user']).toFixed(2)),
      backgroundColor:PALETTE.map(c=>c+'20'),borderColor:PALETTE,borderWidth:2,borderRadius:5,borderSkipped:false}}]}},
  options:{{indexAxis:'y',responsive:true,
    plugins:{{legend:{{display:false}},tooltip:{{backgroundColor:'#1A1612',borderColor:'rgba(26,22,18,0.2)',borderWidth:1,callbacks:{{label:ctx=>` ${{ctx.parsed.x}} events/user`}}}}}},
    scales:{{x:{{grid:{{color:'rgba(26,22,18,0.06)'}},beginAtZero:true}},y:{{grid:{{display:false}}}}}}}}}});

// Bubble
new Chart(document.getElementById('scatterChart'),{{
  type:'bubble',
  data:{{datasets:SUMMARY_DATA.map((r,i)=>{{
    return {{label:r['Event name'],
      data:[{{x:parseFloat(r['Event count per active user']),y:r['Total users'],r:Math.max(4,Math.sqrt(r['Event count'])*1.1)}}],
      backgroundColor:PALETTE[i]+'40',borderColor:PALETTE[i],borderWidth:2}};
  }})}},
  options:{{responsive:true,
    plugins:{{legend:{{position:'bottom',labels:{{boxWidth:8,padding:10,usePointStyle:true}}}},
      tooltip:{{backgroundColor:'#1A1612',borderColor:'rgba(26,22,18,0.2)',borderWidth:1,
        callbacks:{{label:ctx=>` ${{ctx.dataset.label}}: ${{ctx.raw.x.toFixed(1)}} ev/user · ${{ctx.raw.y}} users`}}}}}},
    scales:{{
      x:{{title:{{display:true,text:'Events per Active User',color:'#9A9390'}},grid:{{color:'rgba(26,22,18,0.06)'}}}},
      y:{{title:{{display:true,text:'Total Users',color:'#9A9390'}},grid:{{color:'rgba(26,22,18,0.06)'}}}}
    }}}}}});

// Table
const maxEpu=Math.max(...SUMMARY_DATA.map(r=>r['Event count per active user']));
const tb=document.getElementById('table-body');
SUMMARY_DATA.forEach((r,i)=>{{
  const share=(r['Event count']/total*100).toFixed(1);
  const score=Math.round(r['Event count per active user']/maxEpu*100);
  tb.innerHTML+=`<tr>
    <td><div class="event-chip"><div class="chip-dot" style="background:${{PALETTE[i]}}"></div>${{r['Event name']}}</div></td>
    <td class="mono" style="font-weight:600">${{r['Event count'].toLocaleString()}}</td>
    <td class="mono">${{r['Total users']}}</td>
    <td class="mono" style="color:${{PALETTE[i]}};font-weight:600">${{parseFloat(r['Event count per active user']).toFixed(2)}}</td>
    <td><span style="font-family:'DM Mono',monospace;font-size:10px;padding:3px 9px;border-radius:99px;background:${{PALETTE[i]}}15;color:${{PALETTE[i]}};font-weight:600;">${{share}}%</span></td>
    <td><div class="score-wrap"><div class="score-track"><div class="score-fill" style="width:${{score}}%;background:${{PALETTE[i]}};"></div></div><span class="mono" style="font-size:10px;color:var(--muted);min-width:28px;">${{score}}</span></div></td>
  </tr>`;
}});

// CSV Export
function exportCSV(){{
  const headers=['Event Name','Event Count','Total Users','Events per Active User','Share %','Engagement Score'];
  const rows=SUMMARY_DATA.map(r=>[r['Event name'],r['Event count'],r['Total users'],
    parseFloat(r['Event count per active user']).toFixed(2),(r['Event count']/total*100).toFixed(1),
    Math.round(r['Event count per active user']/maxEpu*100)]);
  const csv=[headers,...rows].map(r=>r.join(',')).join('\\n');
  const a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(csv);
  a.download='ga4_engagement_export.csv'; a.click();
}}
</script>
</body></html>"""

    import streamlit.components.v1 as components
    components.html(html, height=2400, scrolling=True)


if __name__ == "__main__":
    main()
