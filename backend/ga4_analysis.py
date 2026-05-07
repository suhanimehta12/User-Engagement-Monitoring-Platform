"""
ga4_analysis.py
───────────────
Core analytics module: loads GA4 data, generates simulated
time-series, computes KPIs, and produces matplotlib/seaborn charts.

Run standalone:  python backend/ga4_analysis.py
Used by:         app.py (Streamlit)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings, os

warnings.filterwarnings("ignore")

# ── Theme ──────────────────────────────────────────────────────────────────────
BG      = "#F5F2EE"
SURFACE = "#FFFFFF"
ACCENT  = "#E8440A"
ACCENT2 = "#2563EB"
ACCENT3 = "#059669"
ACCENT4 = "#7C3AED"
ACCENT5 = "#D97706"
TEXT    = "#1A1612"
MUTED   = "#9A9390"
PALETTE = [ACCENT, ACCENT2, ACCENT3, ACCENT4, ACCENT5, "#0891B2"]

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": "#E5E0DA",
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": TEXT,
    "grid.color": "#EDE9E3",
    "grid.alpha": 0.8,
    "font.family": "monospace",
    "legend.facecolor": SURFACE,
    "legend.edgecolor": "#E5E0DA",
})


def load_ga4(path: str = "data/ga4_data.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df["Event count per active user"] = pd.to_numeric(
        df["Event count per active user"], errors="coerce"
    )
    df = df.sort_values("Event count", ascending=False).reset_index(drop=True)
    return df


def simulate_timeseries(df: pd.DataFrame, days: int = 30, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    event_bases = dict(zip(df["Event name"], df["Event count"]))
    dates = [datetime.today() - timedelta(days=i) for i in range(days - 1, -1, -1)]
    rows = []
    for d in dates:
        weekend_boost = 1.3 if d.weekday() >= 5 else 1.0
        for event, base in event_bases.items():
            daily_base = base / days
            noise = np.random.normal(0, daily_base * 0.35)
            count = max(0, int((daily_base + noise) * weekend_boost))
            rows.append({"date": d.strftime("%Y-%m-%d"), "event": event, "count": count})
    return pd.DataFrame(rows)


def compute_kpis(df: pd.DataFrame) -> dict:
    total = int(df["Event count"].sum())
    scroll_row = df[df["Event name"] == "scroll"]
    scroll_pct = round(scroll_row["Event count"].values[0] / total * 100, 1) if not scroll_row.empty else 0
    return {
        "total_events": total,
        "unique_event_types": len(df),
        "total_users": int(df["Total users"].max()),
        "avg_events_per_user": round(float(df["Event count per active user"].mean()), 2),
        "top_event": df.loc[df["Event count"].idxmax(), "Event name"],
        "top_event_count": int(df["Event count"].max()),
        "scroll_dominance_pct": scroll_pct,
    }


def plot_horizontal_bar(df: pd.DataFrame, out: str = "plots/bar_chart.png"):
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(df))]
    bars = ax.barh(df["Event name"], df["Event count per active user"],
                   color=colors, edgecolor="none", height=0.55)
    for bar, val in zip(bars, df["Event count per active user"]):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", ha="left", fontsize=9, color=TEXT)
    ax.set_xlabel("Events per Active User", color=MUTED)
    ax.set_title("Event Engagement Rate by Type", color=TEXT, fontsize=13, pad=15)
    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.spines[:].set_visible(False)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"  ✓ Saved {out}")


def plot_donut(df: pd.DataFrame, out: str = "plots/donut_chart.png"):
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        df["Event count"], labels=df["Event name"],
        colors=PALETTE[:len(df)], autopct="%1.1f%%", startangle=140,
        wedgeprops={"linewidth": 3, "edgecolor": BG}, pctdistance=0.8,
    )
    for t in texts: t.set_color(TEXT); t.set_fontsize(10)
    for a in autotexts: a.set_color(BG); a.set_fontsize(8); a.set_fontweight("bold")
    centre = plt.Circle((0, 0), 0.55, color=BG)
    ax.add_artist(centre)
    ax.text(0, 0, f"{int(df['Event count'].sum()):,}", ha="center", va="center",
            fontsize=18, color=ACCENT, fontweight="bold")
    ax.text(0, -0.18, "total events", ha="center", va="center", fontsize=9, color=MUTED)
    ax.set_title("Event Count Distribution", color=TEXT, fontsize=13, pad=15)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"  ✓ Saved {out}")


def plot_timeseries(ts: pd.DataFrame, out: str = "plots/timeseries.png"):
    pivot = ts.pivot_table(index="date", columns="event", values="count", aggfunc="sum")
    pivot.index = pd.to_datetime(pivot.index)
    fig, ax = plt.subplots(figsize=(14, 5))
    for i, col in enumerate(pivot.columns):
        c = PALETTE[i % len(PALETTE)]
        ax.plot(pivot.index, pivot[col], label=col, color=c, linewidth=2, alpha=0.9)
        ax.fill_between(pivot.index, pivot[col], alpha=0.06, color=c)
    ax.set_title("30-Day Engagement Trend", color=TEXT, fontsize=13, pad=15)
    ax.set_xlabel("Date", color=MUTED)
    ax.set_ylabel("Event Count", color=MUTED)
    ax.legend(fontsize=9, ncol=3)
    ax.grid(linestyle="--", alpha=0.3)
    ax.spines[:].set_visible(False)
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%m/%d"))
    plt.tight_layout()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"  ✓ Saved {out}")


def plot_scatter(df: pd.DataFrame, out: str = "plots/scatter.png"):
    fig, ax = plt.subplots(figsize=(8, 6))
    for i, row in df.iterrows():
        c = PALETTE[i % len(PALETTE)]
        size = row["Event count"] / df["Event count"].max() * 2000
        ax.scatter(row["Event count per active user"], row["Total users"],
                   s=size, c=c, alpha=0.75, edgecolors=BG, linewidths=1.5)
        ax.annotate(row["Event name"],
                    (row["Event count per active user"], row["Total users"]),
                    xytext=(6, 4), textcoords="offset points", fontsize=8, color=TEXT)
    ax.set_xlabel("Events per Active User", color=MUTED)
    ax.set_ylabel("Total Users", color=MUTED)
    ax.set_title("User Reach vs. Event Activity", color=TEXT, fontsize=13, pad=15)
    ax.grid(linestyle="--", alpha=0.3)
    ax.spines[:].set_visible(False)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"  ✓ Saved {out}")


if __name__ == "__main__":
    print("\n── GA4 Analytics Engine ──────────────────────────────")
    df = load_ga4("data/ga4_data.csv")
    ts = simulate_timeseries(df, days=30)
    kpis = compute_kpis(df)

    print("\n📊 KPIs:")
    for k, v in kpis.items():
        print(f"  {k}: {v}")

    print("\n📈 Generating charts …")
    plot_horizontal_bar(df)
    plot_donut(df)
    plot_timeseries(ts)
    plot_scatter(df)

    print("\n✅ Analysis complete. Charts saved to plots/")
