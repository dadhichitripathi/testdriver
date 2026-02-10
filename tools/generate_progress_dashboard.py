#!/usr/bin/env python3
"""
Generate an HTML dashboard to visualize OLA Mumbai WhatsApp growth progress.

Usage:
  python3 tools/generate_progress_dashboard.py
  python3 tools/generate_progress_dashboard.py \
    --kpi-csv docs/mumbai-whatsapp-driver-growth/05-kpi-tracker-template.csv \
    --partner-csv docs/mumbai-whatsapp-driver-growth/16-partner-location-tracker-template.csv \
    --output reports/mumbai-whatsapp-progress-dashboard.html
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


def as_float(value: str | None) -> float | None:
    if value is None:
        return None
    raw = value.strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def as_str(value: str | None) -> str:
    return (value or "").strip()


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1f}%"


def fmt_num(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:,.0f}"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_date(date_raw: str) -> datetime:
    return datetime.strptime(date_raw, "%Y-%m-%d")


@dataclass
class WeeklyTotals:
    new_followers: float = 0.0
    community_new_members: float = 0.0
    view_rates: list[float] = field(default_factory=list)
    frt_values: list[float] = field(default_factory=list)
    frt_breaches: int = 0

    contacted_7: float = 0.0
    reactivated_7: float = 0.0
    contacted_15: float = 0.0
    reactivated_15: float = 0.0
    contacted_30: float = 0.0
    reactivated_30: float = 0.0

    eligible: float = 0.0
    completed: float = 0.0
    fraud_incidents: float = 0.0


def build_kpi_payload(rows: list[dict[str, str]]) -> dict[str, object]:
    rows = [row for row in rows if as_str(row.get("Date"))]
    rows.sort(key=lambda row: parse_date(as_str(row["Date"])))

    daily_dates: list[str] = []
    daily_followers_total: list[float | None] = []
    daily_new_followers: list[float] = []
    daily_new_members: list[float] = []
    daily_view_rate: list[float | None] = []
    daily_frt: list[float | None] = []
    daily_incentive_completion_pct: list[float | None] = []

    weekly: dict[int, WeeklyTotals] = defaultdict(WeeklyTotals)

    total_contacted = 0.0
    total_reactivated = 0.0
    frt_values_all: list[float] = []
    fraud_incidents_total = 0.0
    eligible_total = 0.0
    completed_total = 0.0
    followers_latest: float | None = None

    for row in rows:
        date = as_str(row.get("Date"))
        week_val = as_float(row.get("Week"))
        week = int(week_val) if week_val is not None else -1
        bucket = weekly[week]

        followers_total = as_float(row.get("Channel_Followers_Total"))
        new_followers = as_float(row.get("Channel_New_Followers")) or 0.0
        new_members = as_float(row.get("Community_New_Members")) or 0.0
        view_rate = as_float(row.get("Channel_24h_Median_View_Rate_pct"))
        frt = as_float(row.get("Helpdesk_First_Response_Time_Min"))

        contacted_7 = as_float(row.get("Inactive_7d_Contacted")) or 0.0
        reactivated_7 = as_float(row.get("Inactive_7d_Reactivated")) or 0.0
        contacted_15 = as_float(row.get("Inactive_15d_Contacted")) or 0.0
        reactivated_15 = as_float(row.get("Inactive_15d_Reactivated")) or 0.0
        contacted_30 = as_float(row.get("Inactive_30d_Contacted")) or 0.0
        reactivated_30 = as_float(row.get("Inactive_30d_Reactivated")) or 0.0

        eligible = as_float(row.get("Incentive_Eligible_Drivers")) or 0.0
        completed = as_float(row.get("Incentive_Completed_Drivers")) or 0.0
        fraud_incidents = as_float(row.get("Spam_Fraud_Incidents")) or 0.0

        daily_dates.append(date)
        daily_followers_total.append(followers_total)
        daily_new_followers.append(new_followers)
        daily_new_members.append(new_members)
        daily_view_rate.append(view_rate)
        daily_frt.append(frt)
        daily_incentive_completion_pct.append(
            (completed / eligible * 100.0) if eligible > 0 else None
        )

        bucket.new_followers += new_followers
        bucket.community_new_members += new_members
        if view_rate is not None:
            bucket.view_rates.append(view_rate)
        if frt is not None:
            bucket.frt_values.append(frt)
            if frt > 120:
                bucket.frt_breaches += 1

        bucket.contacted_7 += contacted_7
        bucket.reactivated_7 += reactivated_7
        bucket.contacted_15 += contacted_15
        bucket.reactivated_15 += reactivated_15
        bucket.contacted_30 += contacted_30
        bucket.reactivated_30 += reactivated_30

        bucket.eligible += eligible
        bucket.completed += completed
        bucket.fraud_incidents += fraud_incidents

        total_contacted += contacted_7 + contacted_15 + contacted_30
        total_reactivated += reactivated_7 + reactivated_15 + reactivated_30

        if frt is not None:
            frt_values_all.append(frt)

        fraud_incidents_total += fraud_incidents
        eligible_total += eligible
        completed_total += completed

        if followers_total is not None:
            followers_latest = followers_total

    weekly_labels: list[str] = []
    weekly_conv_7: list[float | None] = []
    weekly_conv_15: list[float | None] = []
    weekly_conv_30: list[float | None] = []
    weekly_frt_avg: list[float | None] = []
    weekly_incentive_completion: list[float | None] = []
    weekly_new_followers: list[float] = []
    weekly_fraud_incidents: list[float] = []

    for week in sorted(weekly):
        if week < 0:
            continue
        bucket = weekly[week]
        weekly_labels.append(f"W{week}")
        weekly_new_followers.append(bucket.new_followers)
        weekly_fraud_incidents.append(bucket.fraud_incidents)

        weekly_conv_7.append(
            (bucket.reactivated_7 / bucket.contacted_7 * 100.0)
            if bucket.contacted_7 > 0
            else None
        )
        weekly_conv_15.append(
            (bucket.reactivated_15 / bucket.contacted_15 * 100.0)
            if bucket.contacted_15 > 0
            else None
        )
        weekly_conv_30.append(
            (bucket.reactivated_30 / bucket.contacted_30 * 100.0)
            if bucket.contacted_30 > 0
            else None
        )
        weekly_frt_avg.append(
            (sum(bucket.frt_values) / len(bucket.frt_values))
            if bucket.frt_values
            else None
        )
        weekly_incentive_completion.append(
            (bucket.completed / bucket.eligible * 100.0) if bucket.eligible > 0 else None
        )

    overall_conversion = (total_reactivated / total_contacted * 100.0) if total_contacted > 0 else None
    avg_frt = (sum(frt_values_all) / len(frt_values_all)) if frt_values_all else None
    overall_incentive_completion = (completed_total / eligible_total * 100.0) if eligible_total > 0 else None

    headline = {
        "followers_latest": followers_latest,
        "overall_reactivated": total_reactivated,
        "overall_reactivation_conversion_pct": overall_conversion,
        "avg_helpdesk_frt_min": avg_frt,
        "incentive_completion_pct": overall_incentive_completion,
        "fraud_incidents_total": fraud_incidents_total,
    }

    charts = {
        "daily_dates": daily_dates,
        "daily_followers_total": daily_followers_total,
        "daily_new_followers": daily_new_followers,
        "daily_new_members": daily_new_members,
        "daily_view_rate": daily_view_rate,
        "daily_helpdesk_frt": daily_frt,
        "daily_incentive_completion_pct": daily_incentive_completion_pct,
        "weekly_labels": weekly_labels,
        "weekly_conv_7": weekly_conv_7,
        "weekly_conv_15": weekly_conv_15,
        "weekly_conv_30": weekly_conv_30,
        "weekly_frt_avg": weekly_frt_avg,
        "weekly_incentive_completion": weekly_incentive_completion,
        "weekly_new_followers": weekly_new_followers,
        "weekly_fraud_incidents": weekly_fraud_incidents,
    }

    return {
        "headline": headline,
        "charts": charts,
        "targets": {
            "view_rate_pct": 35,
            "helpdesk_frt_min": 120,
            "reactivation_7d_pct": 20,
            "incentive_completion_pct": 25,
        },
    }


def build_partner_payload(rows: list[dict[str, str]]) -> dict[str, object]:
    by_partner: dict[str, dict[str, float | str]] = {}
    for row in rows:
        partner_name = as_str(row.get("Partner_Name")) or "Unknown Partner"
        location = as_str(row.get("Location")) or "Unknown Location"
        key = f"{partner_name} | {location}"
        scans = as_float(row.get("QR_Scans")) or 0.0
        joins = as_float(row.get("Verified_Joins")) or 0.0

        if key not in by_partner:
            by_partner[key] = {"name": key, "scans": 0.0, "joins": 0.0}
        by_partner[key]["scans"] = float(by_partner[key]["scans"]) + scans
        by_partner[key]["joins"] = float(by_partner[key]["joins"]) + joins

    ranking = []
    for item in by_partner.values():
        scans = float(item["scans"])
        joins = float(item["joins"])
        conversion_pct = (joins / scans * 100.0) if scans > 0 else None
        ranking.append(
            {
                "name": item["name"],
                "scans": scans,
                "joins": joins,
                "conversion_pct": conversion_pct,
            }
        )

    ranking.sort(key=lambda x: x["joins"], reverse=True)
    top = ranking[:7]
    return {
        "labels": [item["name"] for item in top],
        "joins": [item["joins"] for item in top],
        "conversion_pct": [item["conversion_pct"] for item in top],
    }


def render_html(payload: dict[str, object]) -> str:
    data_json = json.dumps(payload, separators=(",", ":"))
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OLA Auto Mumbai WhatsApp Progress Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{
      --bg: #0b1020;
      --panel: #121a31;
      --panel2: #1a2442;
      --text: #e8edff;
      --muted: #98a6d3;
      --green: #22c55e;
      --amber: #f59e0b;
      --blue: #38bdf8;
      --red: #ef4444;
      --purple: #a78bfa;
    }}
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      background: linear-gradient(180deg, #0b1020, #0f1730);
      color: var(--text);
    }}
    .wrap {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 20px;
    }}
    h1 {{
      margin: 0 0 8px 0;
      font-size: 24px;
    }}
    .subtitle {{
      color: var(--muted);
      margin-bottom: 18px;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid #243053;
      border-radius: 10px;
      padding: 14px;
    }}
    .card .label {{
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
    }}
    .card .value {{
      font-size: 24px;
      font-weight: bold;
      line-height: 1.1;
    }}
    .chart-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid #243053;
      border-radius: 10px;
      padding: 12px;
      min-height: 280px;
    }}
    .panel h3 {{
      margin: 2px 0 10px 0;
      font-size: 14px;
      color: var(--muted);
      font-weight: 600;
    }}
    canvas {{
      width: 100% !important;
      height: 230px !important;
    }}
    .footnote {{
      margin-top: 16px;
      color: var(--muted);
      font-size: 12px;
    }}
    @media (max-width: 980px) {{
      .chart-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>OLA Auto Mumbai WhatsApp Progress Dashboard</h1>
    <div class="subtitle">Generated at {generated_at}</div>

    <div class="cards">
      <div class="card"><div class="label">Channel followers (latest)</div><div class="value" id="followers_latest">-</div></div>
      <div class="card"><div class="label">Reactivated drivers (total)</div><div class="value" id="overall_reactivated">-</div></div>
      <div class="card"><div class="label">Overall reactivation conversion</div><div class="value" id="overall_conv">-</div></div>
      <div class="card"><div class="label">Avg helpdesk FRT</div><div class="value" id="avg_frt">-</div></div>
      <div class="card"><div class="label">Incentive completion</div><div class="value" id="completion_pct">-</div></div>
      <div class="card"><div class="label">Fraud incidents (total)</div><div class="value" id="fraud_total">-</div></div>
    </div>

    <div class="chart-grid">
      <div class="panel"><h3>Daily channel followers</h3><canvas id="followersChart"></canvas></div>
      <div class="panel"><h3>Daily acquisition (followers vs community members)</h3><canvas id="acqChart"></canvas></div>
      <div class="panel"><h3>Daily view rate vs target</h3><canvas id="viewRateChart"></canvas></div>
      <div class="panel"><h3>Weekly reactivation conversion by cohort</h3><canvas id="reactivationChart"></canvas></div>
      <div class="panel"><h3>Weekly helpdesk FRT vs SLA</h3><canvas id="frtChart"></canvas></div>
      <div class="panel"><h3>Weekly incentive completion and fraud incidents</h3><canvas id="qualityChart"></canvas></div>
      <div class="panel"><h3>Top partner locations by verified joins</h3><canvas id="partnerChart"></canvas></div>
      <div class="panel"><h3>Daily incentive completion trend</h3><canvas id="completionChart"></canvas></div>
    </div>

    <div class="footnote">
      Targets: View rate >= 35%, 7d reactivation >= 20%, Helpdesk FRT <= 120 min, Incentive completion >= 25%.
    </div>
  </div>

  <script>
    const payload = {data_json};
    const h = payload.kpi.headline;
    const c = payload.kpi.charts;
    const t = payload.kpi.targets;
    const p = payload.partner;

    function fmtNum(v) {{
      if (v === null || v === undefined || Number.isNaN(v)) return "n/a";
      return new Intl.NumberFormat("en-IN", {{ maximumFractionDigits: 0 }}).format(v);
    }}

    function fmtPct(v) {{
      if (v === null || v === undefined || Number.isNaN(v)) return "n/a";
      return v.toFixed(1) + "%";
    }}

    function fmtMin(v) {{
      if (v === null || v === undefined || Number.isNaN(v)) return "n/a";
      return v.toFixed(1) + " min";
    }}

    document.getElementById("followers_latest").innerText = fmtNum(h.followers_latest);
    document.getElementById("overall_reactivated").innerText = fmtNum(h.overall_reactivated);
    document.getElementById("overall_conv").innerText = fmtPct(h.overall_reactivation_conversion_pct);
    document.getElementById("avg_frt").innerText = fmtMin(h.avg_helpdesk_frt_min);
    document.getElementById("completion_pct").innerText = fmtPct(h.incentive_completion_pct);
    document.getElementById("fraud_total").innerText = fmtNum(h.fraud_incidents_total);

    const common = {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{
          labels: {{ color: "#d5defe" }}
        }}
      }},
      scales: {{
        x: {{
          ticks: {{ color: "#98a6d3" }},
          grid: {{ color: "rgba(152,166,211,0.15)" }}
        }},
        y: {{
          ticks: {{ color: "#98a6d3" }},
          grid: {{ color: "rgba(152,166,211,0.15)" }}
        }}
      }}
    }};

    new Chart(document.getElementById("followersChart"), {{
      type: "line",
      data: {{
        labels: c.daily_dates,
        datasets: [
          {{ label: "Followers", data: c.daily_followers_total, borderColor: "#38bdf8", tension: 0.25 }}
        ]
      }},
      options: common
    }});

    new Chart(document.getElementById("acqChart"), {{
      type: "bar",
      data: {{
        labels: c.daily_dates,
        datasets: [
          {{ label: "Channel new followers", data: c.daily_new_followers, backgroundColor: "#22c55e" }},
          {{ label: "Community new members", data: c.daily_new_members, backgroundColor: "#a78bfa" }}
        ]
      }},
      options: common
    }});

    new Chart(document.getElementById("viewRateChart"), {{
      type: "line",
      data: {{
        labels: c.daily_dates,
        datasets: [
          {{ label: "View rate %", data: c.daily_view_rate, borderColor: "#f59e0b", tension: 0.25 }},
          {{ label: "Target %", data: c.daily_dates.map(() => t.view_rate_pct), borderColor: "#22c55e", borderDash: [5,5] }}
        ]
      }},
      options: common
    }});

    new Chart(document.getElementById("reactivationChart"), {{
      type: "bar",
      data: {{
        labels: c.weekly_labels,
        datasets: [
          {{ label: "7d conversion %", data: c.weekly_conv_7, backgroundColor: "#38bdf8" }},
          {{ label: "15d conversion %", data: c.weekly_conv_15, backgroundColor: "#a78bfa" }},
          {{ label: "30+d conversion %", data: c.weekly_conv_30, backgroundColor: "#f59e0b" }}
        ]
      }},
      options: common
    }});

    new Chart(document.getElementById("frtChart"), {{
      type: "line",
      data: {{
        labels: c.weekly_labels,
        datasets: [
          {{ label: "Avg FRT (min)", data: c.weekly_frt_avg, borderColor: "#ef4444", tension: 0.25 }},
          {{ label: "SLA (min)", data: c.weekly_labels.map(() => t.helpdesk_frt_min), borderColor: "#22c55e", borderDash: [5,5] }}
        ]
      }},
      options: common
    }});

    new Chart(document.getElementById("qualityChart"), {{
      data: {{
        labels: c.weekly_labels,
        datasets: [
          {{ type: "line", label: "Incentive completion %", data: c.weekly_incentive_completion, borderColor: "#22c55e", yAxisID: "y" }},
          {{ type: "bar", label: "Fraud incidents", data: c.weekly_fraud_incidents, backgroundColor: "#ef4444", yAxisID: "y1" }}
        ]
      }},
      options: {{
        ...common,
        scales: {{
          x: common.scales.x,
          y: {{
            position: "left",
            ticks: {{ color: "#98a6d3" }},
            grid: {{ color: "rgba(152,166,211,0.15)" }}
          }},
          y1: {{
            position: "right",
            ticks: {{ color: "#98a6d3" }},
            grid: {{ drawOnChartArea: false }}
          }}
        }}
      }}
    }});

    new Chart(document.getElementById("partnerChart"), {{
      type: "bar",
      data: {{
        labels: p.labels,
        datasets: [
          {{ label: "Verified joins", data: p.joins, backgroundColor: "#22c55e" }},
          {{ label: "Conversion %", data: p.conversion_pct, backgroundColor: "#38bdf8" }}
        ]
      }},
      options: {{
        ...common,
        indexAxis: "y"
      }}
    }});

    new Chart(document.getElementById("completionChart"), {{
      type: "line",
      data: {{
        labels: c.daily_dates,
        datasets: [
          {{ label: "Daily incentive completion %", data: c.daily_incentive_completion_pct, borderColor: "#22c55e", tension: 0.25 }},
          {{ label: "Target %", data: c.daily_dates.map(() => t.incentive_completion_pct), borderColor: "#f59e0b", borderDash: [5,5] }}
        ]
      }},
      options: common
    }});
  </script>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate progress dashboard HTML.")
    parser.add_argument(
        "--kpi-csv",
        default="docs/mumbai-whatsapp-driver-growth/05-kpi-tracker-template.csv",
        type=Path,
        help="Path to KPI tracker CSV",
    )
    parser.add_argument(
        "--partner-csv",
        default="docs/mumbai-whatsapp-driver-growth/16-partner-location-tracker-template.csv",
        type=Path,
        help="Path to partner location tracker CSV",
    )
    parser.add_argument(
        "--output",
        default="reports/mumbai-whatsapp-progress-dashboard.html",
        type=Path,
        help="Output HTML path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.kpi_csv.exists():
        raise SystemExit(f"KPI CSV not found: {args.kpi_csv}")
    if not args.partner_csv.exists():
        raise SystemExit(f"Partner CSV not found: {args.partner_csv}")

    kpi_rows = load_csv(args.kpi_csv)
    partner_rows = load_csv(args.partner_csv)

    payload = {
        "kpi": build_kpi_payload(kpi_rows),
        "partner": build_partner_payload(partner_rows),
    }
    html = render_html(payload)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
