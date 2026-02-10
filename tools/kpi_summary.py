#!/usr/bin/env python3
"""
Generate a concise KPI summary from the WhatsApp driver growth tracker CSV.

Usage:
  python tools/kpi_summary.py docs/mumbai-whatsapp-driver-growth/05-kpi-tracker-template.csv
  python tools/kpi_summary.py <csv_path> --week 8
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Iterable


def as_float(raw: str | None) -> float | None:
    if raw is None:
        return None
    value = raw.strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


@dataclass
class Totals:
    rows: int = 0
    channel_new_followers: float = 0.0
    channel_view_rates: list[float] | None = None
    community_new_members: float = 0.0

    inactive_7_contacted: float = 0.0
    inactive_7_reactivated: float = 0.0
    inactive_15_contacted: float = 0.0
    inactive_15_reactivated: float = 0.0
    inactive_30_contacted: float = 0.0
    inactive_30_reactivated: float = 0.0

    helpdesk_frt_values: list[float] | None = None
    helpdesk_frt_breaches: int = 0

    incentive_eligible: float = 0.0
    incentive_completed: float = 0.0
    fraud_incidents: float = 0.0
    open_escalations: float = 0.0

    def __post_init__(self) -> None:
        if self.channel_view_rates is None:
            self.channel_view_rates = []
        if self.helpdesk_frt_values is None:
            self.helpdesk_frt_values = []


def add_value(total: float, row: dict[str, str], key: str) -> float:
    value = as_float(row.get(key))
    return total + (value or 0.0)


def format_pct(numerator: float, denominator: float) -> str:
    if denominator <= 0:
        return "n/a"
    return f"{(numerator / denominator) * 100:.1f}%"


def load_rows(path: Path) -> Iterable[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield row


def summarize(path: Path, week: int | None) -> Totals:
    totals = Totals()
    for row in load_rows(path):
        row_week = as_float(row.get("Week"))
        if week is not None and row_week != float(week):
            continue

        totals.rows += 1
        totals.channel_new_followers = add_value(
            totals.channel_new_followers, row, "Channel_New_Followers"
        )
        totals.community_new_members = add_value(
            totals.community_new_members, row, "Community_New_Members"
        )

        totals.inactive_7_contacted = add_value(
            totals.inactive_7_contacted, row, "Inactive_7d_Contacted"
        )
        totals.inactive_7_reactivated = add_value(
            totals.inactive_7_reactivated, row, "Inactive_7d_Reactivated"
        )
        totals.inactive_15_contacted = add_value(
            totals.inactive_15_contacted, row, "Inactive_15d_Contacted"
        )
        totals.inactive_15_reactivated = add_value(
            totals.inactive_15_reactivated, row, "Inactive_15d_Reactivated"
        )
        totals.inactive_30_contacted = add_value(
            totals.inactive_30_contacted, row, "Inactive_30d_Contacted"
        )
        totals.inactive_30_reactivated = add_value(
            totals.inactive_30_reactivated, row, "Inactive_30d_Reactivated"
        )

        totals.incentive_eligible = add_value(
            totals.incentive_eligible, row, "Incentive_Eligible_Drivers"
        )
        totals.incentive_completed = add_value(
            totals.incentive_completed, row, "Incentive_Completed_Drivers"
        )
        totals.fraud_incidents = add_value(
            totals.fraud_incidents, row, "Spam_Fraud_Incidents"
        )
        totals.open_escalations = add_value(
            totals.open_escalations, row, "Open_Escalations"
        )

        view_rate = as_float(row.get("Channel_24h_Median_View_Rate_pct"))
        if view_rate is not None:
            totals.channel_view_rates.append(view_rate)

        frt = as_float(row.get("Helpdesk_First_Response_Time_Min"))
        if frt is not None:
            totals.helpdesk_frt_values.append(frt)
            if frt > 120:
                totals.helpdesk_frt_breaches += 1

    return totals


def print_summary(path: Path, totals: Totals, week: int | None) -> None:
    title_scope = f"Week {week}" if week is not None else "All rows"
    print("OLA Auto Mumbai WhatsApp KPI Summary")
    print(f"Source: {path}")
    print(f"Scope: {title_scope}")
    print(f"Rows considered: {totals.rows}")
    print("")

    avg_view_rate = (
        f"{mean(totals.channel_view_rates):.1f}%"
        if totals.channel_view_rates
        else "n/a"
    )
    avg_frt = (
        f"{mean(totals.helpdesk_frt_values):.1f} min"
        if totals.helpdesk_frt_values
        else "n/a"
    )

    total_contacted = (
        totals.inactive_7_contacted
        + totals.inactive_15_contacted
        + totals.inactive_30_contacted
    )
    total_reactivated = (
        totals.inactive_7_reactivated
        + totals.inactive_15_reactivated
        + totals.inactive_30_reactivated
    )

    print("- Growth")
    print(f"  - New followers: {totals.channel_new_followers:.0f}")
    print(f"  - Community new members: {totals.community_new_members:.0f}")
    print(f"  - Average 24h median view rate: {avg_view_rate}")
    print("")

    print("- Reactivation")
    print(
        "  - 7d cohort conversion: "
        + format_pct(totals.inactive_7_reactivated, totals.inactive_7_contacted)
        + f" ({totals.inactive_7_reactivated:.0f}/{totals.inactive_7_contacted:.0f})"
    )
    print(
        "  - 15d cohort conversion: "
        + format_pct(totals.inactive_15_reactivated, totals.inactive_15_contacted)
        + f" ({totals.inactive_15_reactivated:.0f}/{totals.inactive_15_contacted:.0f})"
    )
    print(
        "  - 30+d cohort conversion: "
        + format_pct(totals.inactive_30_reactivated, totals.inactive_30_contacted)
        + f" ({totals.inactive_30_reactivated:.0f}/{totals.inactive_30_contacted:.0f})"
    )
    print(
        "  - Overall conversion: "
        + format_pct(total_reactivated, total_contacted)
        + f" ({total_reactivated:.0f}/{total_contacted:.0f})"
    )
    print("")

    print("- Operations quality")
    print(f"  - Average helpdesk first response time: {avg_frt}")
    print(f"  - Helpdesk SLA breaches (>120 min): {totals.helpdesk_frt_breaches}")
    print(f"  - Fraud incidents: {totals.fraud_incidents:.0f}")
    print(f"  - Open escalations: {totals.open_escalations:.0f}")
    print("")

    print("- Incentive performance")
    print(
        "  - Incentive completion rate: "
        + format_pct(totals.incentive_completed, totals.incentive_eligible)
        + f" ({totals.incentive_completed:.0f}/{totals.incentive_eligible:.0f})"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize WhatsApp driver growth KPI tracker CSV."
    )
    parser.add_argument("csv_path", type=Path, help="Path to KPI tracker CSV file")
    parser.add_argument(
        "--week",
        type=int,
        default=None,
        help="Filter output to a specific week number (optional)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.csv_path.exists():
        raise SystemExit(f"CSV not found: {args.csv_path}")

    totals = summarize(args.csv_path, args.week)
    print_summary(args.csv_path, totals, args.week)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
