# Budget and ROI Formulas

Use with `17-budget-and-roi-model.csv` in Google Sheets.

## Suggested formulas (row 2)

### Total_Cost (column I)

`=SUM(C2:H2)`

### Estimated_Contribution_Total (column N)

`=IFERROR(L2*M2,0)`

Where:
- `L2` = Estimated_GMV_per_Trip (or use contribution per trip model)
- `M2` = Estimated_Contribution_per_Trip

If `L2` stores trips and `M2` stores contribution per trip, adjust accordingly:

`=IFERROR(K2*M2,0)`

### ROI_pct (column O)

`=IFERROR((N2-I2)/I2,0)`

Format as percentage.

## Practical interpretation

- ROI > 0: operating contribution exceeds campaign costs.
- ROI = 0: break-even.
- ROI < 0: optimize costs or improve reactivation quality.

## Weekly decision rules

1. If ROI negative for 2 consecutive weeks:
   - reduce low-performing field locations
   - pause low-impact experiments
   - improve reactivation contact quality
2. If ROI positive and rising:
   - scale top captain clusters
   - increase partner deployment in high-conversion zones
   - extend helpdesk coverage in peak windows

## Minimum data quality checks

- Every week must have non-empty total cost.
- Reactivated drivers must match KPI tracker weekly rollup.
- Trips from reactivated drivers should be validated against internal ops data.
