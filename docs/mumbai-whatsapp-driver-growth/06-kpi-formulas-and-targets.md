# KPI Formulas and Targets (Google Sheets)

Assume `05-kpi-tracker-template.csv` is imported into a sheet named `Daily`.
If headers are in row 1, start formulas from row 2.

## Key calculated fields

### Reactivated_Drivers_Total
If not manually filled, calculate as:

`=IFERROR(Q2+S2+U2,0)`

Where:
- `Q` = Inactive_7d_Reactivated
- `S` = Inactive_15d_Reactivated
- `U` = Inactive_30d_Reactivated

### Incentive_Completion_pct

`=IFERROR(Y2/X2,0)`

Format as percentage.

### Helpdesk SLA breach flag

`=IF(N2>120,"BREACH","OK")`

Where `N` is first response time in minutes.

## Weekly rollup formulas

Create a new sheet `Weekly` with columns:

- Week
- New Followers
- Median View Rate
- Community New Members
- Reactivated Drivers
- Incentive Completion %
- Avg Helpdesk FRT

Example formulas (for week value in `A2`):

- New Followers  
  `=SUMIF(Daily!B:B,A2,Daily!F:F)`

- Median View Rate  
  `=MEDIAN(FILTER(Daily!I:I,Daily!B:B=A2,Daily!I:I<>""))`

- Community New Members  
  `=SUMIF(Daily!B:B,A2,Daily!L:L)`

- Reactivated Drivers  
  `=SUMIF(Daily!B:B,A2,Daily!V:V)`

- Incentive Completion %  
  `=IFERROR(SUMIF(Daily!B:B,A2,Daily!Y:Y)/SUMIF(Daily!B:B,A2,Daily!X:X),0)`

- Avg Helpdesk FRT  
  `=AVERAGE(FILTER(Daily!N:N,Daily!B:B=A2,Daily!N:N<>""))`

## Suggested first 30-day targets

- Channel followers: 500+
- Median 24h view rate: 35%+
- Community new members: 300+
- 7-day inactive reactivation conversion: 20%+
- 15-day inactive reactivation conversion: 12%+
- 30+ day inactive reactivation conversion: 8%+
- Helpdesk first response time: <=120 minutes
- Incentive completion (eligible base): 25%+

## Review cadence

- Daily 20-minute standup: yesterday vs target.
- Weekly 30-minute review: what changed and why.
- Monthly optimization: posting slots, copy style, zone-specific strategy.
