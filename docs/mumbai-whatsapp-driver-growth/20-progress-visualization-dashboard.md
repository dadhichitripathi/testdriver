# Progress Visualization Dashboard

This gives you a real visual dashboard from your live CSV trackers.

## What this solves

You can now see progress in charts instead of only rows:
- follower growth trend
- daily acquisition trend
- view rate vs target
- reactivation conversion by cohort
- helpdesk SLA trend
- incentive completion trend
- partner/location performance

## Inputs

- KPI CSV: `docs/mumbai-whatsapp-driver-growth/05-kpi-tracker-template.csv`
- Partner CSV: `docs/mumbai-whatsapp-driver-growth/16-partner-location-tracker-template.csv`

## Generate dashboard

From repo root:

```bash
python3 tools/generate_progress_dashboard.py
```

Custom paths:

```bash
python3 tools/generate_progress_dashboard.py \
  --kpi-csv docs/mumbai-whatsapp-driver-growth/05-kpi-tracker-template.csv \
  --partner-csv docs/mumbai-whatsapp-driver-growth/16-partner-location-tracker-template.csv \
  --output reports/mumbai-whatsapp-progress-dashboard.html
```

## Output

- `reports/mumbai-whatsapp-progress-dashboard.html`

Open this file in a browser and review during daily/weekly ops meetings.

## Review cadence

- Daily quick review (10 min):
  - followers
  - view rate
  - FRT
- Weekly review (30 min):
  - reactivation conversion by cohort
  - incentive completion
  - partner performance ranking

## Data hygiene rules

- Fill date and week for every row.
- Avoid blank reactivation columns when outreach is done.
- Enter helpdesk FRT in minutes.
- Ensure partner scans and joins are updated daily.
