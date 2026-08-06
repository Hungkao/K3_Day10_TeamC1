from __future__ import annotations

from pathlib import Path
from typing import Any
import pandas as pd

from core.config import Settings
from core.utils import write_json


def run_data_quality_checks(df: pd.DataFrame | list[dict[str, Any]], settings: Settings, report_name: str) -> dict[str, Any]:
    """Runs data quality checks on the dataset and writes report to data/quality/{report_name}.json.

    Checks:
    1. Row count.
    2. paper_id not null and unique.
    3. title not null.
    4. summary missing or short length.
    5. freshness using age_days.
    6. Write JSON result to data/quality/ directory.
    """
    if isinstance(df, list):
        df = pd.DataFrame(df)

    total_rows = len(df)
    if total_rows == 0:
        payload = {
            "report_name": report_name,
            "status": "FAIL",
            "reason": "Dataset is empty.",
            "total_rows": 0
        }
        report_file = settings.paths.quality_dir / f"{report_name}.json"
        write_json(report_file, payload)
        return payload

    # 1. Row count check
    row_count = total_rows

    # 2. paper_id not null and unique check
    paper_ids = df["paper_id"].dropna().astype(str).str.strip() if "paper_id" in df.columns else pd.Series(dtype=str)
    paper_id_null_count = total_rows - len(paper_ids)
    duplicate_paper_id_count = int(paper_ids.duplicated().sum())

    # 3. title not null check
    titles = df["title"].dropna().astype(str).str.strip() if "title" in df.columns else pd.Series(dtype=str)
    missing_title_count = total_rows - len(titles)

    # 4. summary length check
    summaries = df["summary"].fillna("").astype(str).str.strip() if "summary" in df.columns else pd.Series(dtype=str)
    missing_summary_count = int((summaries == "").sum())
    short_summary_count = int((summaries.str.len() < 100).sum())

    # 5. Freshness check by age_days
    threshold = settings.freshness_threshold_days
    if "age_days" in df.columns:
        stale_count = int((df["age_days"] > threshold).sum())
    else:
        stale_count = 0

    # Overall Quality Status
    has_critical_error = (
        paper_id_null_count > 0 or
        duplicate_paper_id_count > 0 or
        missing_title_count > 0 or
        missing_summary_count > 0
    )
    status = "FAIL" if has_critical_error else "PASS"

    payload = {
        "report_name": report_name,
        "status": status,
        "metrics": {
            "total_rows": row_count,
            "paper_id_null_count": paper_id_null_count,
            "duplicate_paper_id_count": duplicate_paper_id_count,
            "missing_title_count": missing_title_count,
            "missing_summary_count": missing_summary_count,
            "short_summary_count": short_summary_count,
            "stale_row_count": stale_count,
            "freshness_threshold_days": threshold
        }
    }

    report_file = settings.paths.quality_dir / f"{report_name}.json"
    write_json(report_file, payload)
    return payload


def build_freshness_report(df: pd.DataFrame | list[dict[str, Any]], settings: Settings, report_path: str | Path | None = None) -> dict[str, Any]:
    """Generates a freshness report measuring published dates and stale record count.

    Payload fields:
    - latest_published
    - oldest_published
    - stale_rows
    - total_rows
    - is_fresh
    """
    if isinstance(df, list):
        df = pd.DataFrame(df)

    output_path = Path(report_path) if report_path else settings.paths.freshness_report
    total_rows = len(df)

    if total_rows == 0:
        payload = {
            "latest_published": None,
            "oldest_published": None,
            "stale_rows": 0,
            "total_rows": 0,
            "is_fresh": False,
            "threshold_days": settings.freshness_threshold_days
        }
        write_json(output_path, payload)
        return payload

    published_series = df["published"].dropna().astype(str).str.strip() if "published" in df.columns else pd.Series(dtype=str)
    
    latest_published = str(published_series.max()) if not published_series.empty else None
    oldest_published = str(published_series.min()) if not published_series.empty else None

    threshold = settings.freshness_threshold_days
    if "age_days" in df.columns:
        stale_rows = int((df["age_days"] > threshold).sum())
    else:
        stale_rows = 0

    is_fresh = (stale_rows == 0)

    payload = {
        "latest_published": latest_published,
        "oldest_published": oldest_published,
        "stale_rows": stale_rows,
        "total_rows": total_rows,
        "is_fresh": is_fresh,
        "threshold_days": threshold
    }

    write_json(output_path, payload)
    return payload
