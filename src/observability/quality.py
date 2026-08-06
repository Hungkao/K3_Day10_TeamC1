from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from core.config import Settings
from core.utils import write_json


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Execute data quality checks on the clean dataframe and save JSON report."""
    total_rows = len(df)

    row_count_check = {
        "check": "row_count",
        "passed": total_rows > 0,
        "details": f"Total rows: {total_rows}",
    }

    null_ids = df["paper_id"].isna().sum() + (df["paper_id"].astype(str).str.strip() == "").sum()
    duplicate_ids = df.duplicated(subset=["paper_id"]).sum()
    paper_id_check = {
        "check": "paper_id_integrity",
        "passed": bool(null_ids == 0 and duplicate_ids == 0),
        "details": f"Null IDs: {null_ids}, Duplicate IDs: {duplicate_ids}",
    }

    null_titles = df["title"].isna().sum() + (df["title"].astype(str).str.strip() == "").sum()
    title_check = {
        "check": "title_non_null",
        "passed": bool(null_titles == 0),
        "details": f"Null titles: {null_titles}",
    }

    short_summaries = (df["summary"].astype(str).str.strip().str.len() < 10).sum()
    summary_check = {
        "check": "summary_quality",
        "passed": bool(short_summaries == 0),
        "details": f"Short/empty summaries (<10 chars): {short_summaries}",
    }

    threshold = settings.freshness_threshold_days
    stale_rows = int((df["age_days"] > threshold).sum()) if "age_days" in df.columns else 0
    freshness_check = {
        "check": "freshness_threshold",
        "passed": bool(stale_rows == 0),
        "details": f"Stale rows (> {threshold} days): {stale_rows}",
    }

    checks = [row_count_check, paper_id_check, title_check, summary_check, freshness_check]
    all_passed = all(c["passed"] for c in checks)

    report = {
        "report_name": report_name,
        "total_rows": total_rows,
        "all_passed": all_passed,
        "checks": checks,
    }

    out_dir = settings.paths.quality_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{report_name}.json"
    write_json(report_path, report)

    return report


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path: Path | None = None) -> dict[str, Any]:
    """Build freshness report payload and save to settings.paths.freshness_report."""
    total_rows = len(df)
    if total_rows == 0:
        report = {
            "latest_published": None,
            "oldest_published": None,
            "stale_rows": 0,
            "total_rows": 0,
            "is_fresh": False,
            "freshness_threshold_days": settings.freshness_threshold_days,
        }
    else:
        published_dates = pd.to_datetime(df["published"], errors="coerce").dropna()
        latest_published = published_dates.max().strftime("%Y-%m-%d") if not published_dates.empty else None
        oldest_published = published_dates.min().strftime("%Y-%m-%d") if not published_dates.empty else None

        threshold = settings.freshness_threshold_days
        stale_rows = int((df["age_days"] > threshold).sum()) if "age_days" in df.columns else 0
        is_fresh = stale_rows == 0

        report = {
            "latest_published": latest_published,
            "oldest_published": oldest_published,
            "stale_rows": stale_rows,
            "total_rows": total_rows,
            "is_fresh": is_fresh,
            "freshness_threshold_days": threshold,
        }

    target_path = report_path or settings.paths.freshness_report
    target_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(target_path, report)

    return report

