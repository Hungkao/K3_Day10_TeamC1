from __future__ import annotations

from pathlib import Path
from typing import Any
import pandas as pd

from core.config import Settings
from core.utils import write_json


def run_data_quality_checks(df: pd.DataFrame | list[dict[str, Any]], settings: Settings, report_name: str) -> dict[str, Any]:
    """Execute data quality checks on the clean dataframe and save JSON report to data/quality/{report_name}.json."""
    if isinstance(df, list):
        df = pd.DataFrame(df)

    total_rows = len(df)

    row_count_check = {
        "check": "row_count",
        "passed": total_rows > 0,
        "details": f"Total rows: {total_rows}",
    }

    if total_rows == 0:
        paper_ids = pd.Series(dtype=str)
        titles = pd.Series(dtype=str)
        summaries = pd.Series(dtype=str)
    else:
        paper_ids = df["paper_id"].dropna().astype(str).str.strip() if "paper_id" in df.columns else pd.Series(dtype=str)
        titles = df["title"].dropna().astype(str).str.strip() if "title" in df.columns else pd.Series(dtype=str)
        summaries = df["summary"].fillna("").astype(str).str.strip() if "summary" in df.columns else pd.Series(dtype=str)

    null_ids = total_rows - len(paper_ids)
    duplicate_ids = int(paper_ids.duplicated().sum()) if not paper_ids.empty else 0
    paper_id_check = {
        "check": "paper_id_integrity",
        "passed": bool(null_ids == 0 and duplicate_ids == 0),
        "details": f"Null IDs: {null_ids}, Duplicate IDs: {duplicate_ids}",
    }

    null_titles = total_rows - len(titles)
    title_check = {
        "check": "title_non_null",
        "passed": bool(null_titles == 0),
        "details": f"Null titles: {null_titles}",
    }

    missing_summaries = int((summaries == "").sum()) if not summaries.empty else 0
    short_summaries = int((summaries.str.len() < 100).sum()) if not summaries.empty else 0
    summary_check = {
        "check": "summary_quality",
        "passed": bool(missing_summaries == 0 and short_summaries == 0),
        "details": f"Missing summaries: {missing_summaries}, Short summaries (<100 chars): {short_summaries}",
    }

    threshold = settings.freshness_threshold_days
    stale_rows = int((df["age_days"] > threshold).sum()) if "age_days" in df.columns and not df.empty else 0
    freshness_check = {
        "check": "freshness_threshold",
        "passed": bool(stale_rows == 0),
        "details": f"Stale rows (> {threshold} days): {stale_rows}",
    }

    checks = [row_count_check, paper_id_check, title_check, summary_check, freshness_check]
    all_passed = all(c["passed"] for c in checks)
    status = "PASS" if all_passed else "FAIL"

    report = {
        "report_name": report_name,
        "status": status,
        "all_passed": all_passed,
        "total_rows": total_rows,
        "checks": checks,
        "metrics": {
            "total_rows": total_rows,
            "paper_id_null_count": null_ids,
            "duplicate_paper_id_count": duplicate_ids,
            "missing_title_count": null_titles,
            "missing_summary_count": missing_summaries,
            "short_summary_count": short_summaries,
            "stale_row_count": stale_rows,
            "freshness_threshold_days": threshold
        }
    }

    out_dir = settings.paths.quality_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{report_name}.json"
    write_json(report_path, report)

    return report


def build_freshness_report(df: pd.DataFrame | list[dict[str, Any]], settings: Settings, report_path: Path | None = None) -> dict[str, Any]:
    """Build freshness report payload and save to settings.paths.freshness_report."""
    if isinstance(df, list):
        df = pd.DataFrame(df)

    total_rows = len(df)
    if total_rows == 0:
        report = {
            "latest_published": None,
            "oldest_published": None,
            "stale_rows": 0,
            "total_rows": 0,
            "is_fresh": False,
            "threshold_days": settings.freshness_threshold_days,
            "freshness_threshold_days": settings.freshness_threshold_days,
        }
    else:
        published_series = df["published"].dropna().astype(str).str.strip() if "published" in df.columns else pd.Series(dtype=str)
        published_dates = pd.to_datetime(published_series, errors="coerce").dropna()
        latest_published = published_dates.max().strftime("%Y-%m-%d") if not published_dates.empty else None
        oldest_published = published_dates.min().strftime("%Y-%m-%d") if not published_dates.empty else None

        threshold = settings.freshness_threshold_days
        stale_rows = int((df["age_days"] > threshold).sum()) if "age_days" in df.columns else 0
        is_fresh = (stale_rows == 0)

        report = {
            "latest_published": latest_published,
            "oldest_published": oldest_published,
            "stale_rows": stale_rows,
            "total_rows": total_rows,
            "is_fresh": is_fresh,
            "threshold_days": threshold,
            "freshness_threshold_days": threshold,
        }

    target_path = report_path or settings.paths.freshness_report
    target_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(target_path, report)

    return report
