# KPI Summary Tool (CLI)

This tool generates a quick weekly or overall summary from the KPI tracker CSV.

## File location

- Script: `tools/kpi_summary.py`
- Input CSV: `docs/mumbai-whatsapp-driver-growth/05-kpi-tracker-template.csv`

## Usage

From repository root:

```bash
python3 tools/kpi_summary.py docs/mumbai-whatsapp-driver-growth/05-kpi-tracker-template.csv
```

Weekly filter:

```bash
python3 tools/kpi_summary.py docs/mumbai-whatsapp-driver-growth/05-kpi-tracker-template.csv --week 8
```

## Output includes

- New followers and community members
- Average channel view rate
- Reactivation conversion by cohort (7d/15d/30+d)
- Helpdesk average first response time and SLA breaches
- Incentive completion rate
- Fraud incidents and open escalations

## When to run

- Daily end of day (optional quick check)
- Weekly review (recommended)

Use output directly in your weekly operations review call notes.
