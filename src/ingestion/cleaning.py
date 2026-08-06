from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import logging
import re
from typing import Any

import pandas as pd

from ingestion.crossref import PaperRecord

logger = logging.getLogger(__name__)


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Clean raw records into a structured DataFrame ready for embedding and indexing."""
    if not records:
        logger.warning("Empty records list provided to build_clean_dataframe.")
        return pd.DataFrame(
            columns=[
                "paper_id",
                "title",
                "summary",
                "authors",
                "categories",
                "primary_category",
                "published",
                "updated",
                "abs_url",
                "pdf_url",
                "comment",
                "authors_joined",
                "categories_joined",
                "summary_chars",
                "text_for_embedding",
                "age_days",
            ]
        )

    raw_count = len(records)
    logger.info("Starting cleaning pipeline for %d raw records.", raw_count)

    dict_records = [asdict(r) for r in records]
    df = pd.DataFrame(dict_records)

    def clean_str(val: Any) -> str:
        if not val or pd.isna(val):
            return ""
        s = str(val)
        s = re.sub(r"<[^>]+>", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    df["title"] = df["title"].apply(clean_str)
    df["summary"] = df["summary"].apply(clean_str)

    def normalize_list(val: Any) -> list[str]:
        if isinstance(val, list):
            return [clean_str(x) for x in val if clean_str(x)]
        elif isinstance(val, str) and val.strip():
            return [clean_str(val)]
        return []

    df["authors"] = df["authors"].apply(normalize_list)
    df["categories"] = df["categories"].apply(normalize_list)

    df["authors_joined"] = df["authors"].apply(lambda lst: ", ".join(lst) if lst else "")
    df["categories_joined"] = df["categories"].apply(lambda lst: ", ".join(lst) if lst else "")
    df["primary_category"] = df["categories"].apply(lambda lst: lst[0] if lst else "")

    df["summary_chars"] = df["summary"].apply(len)

    if run_date.tzinfo is not None:
        run_date_naive = run_date.replace(tzinfo=None)
    else:
        run_date_naive = run_date

    def calc_age_days(published_str: str) -> int:
        if not published_str:
            return 9999
        try:
            pub_dt = datetime.fromisoformat(str(published_str).split("T")[0])
            delta = (run_date_naive - pub_dt).days
            return max(0, delta)
        except Exception:
            return 9999

    df["published"] = df["published"].astype(str)
    df["updated"] = df["updated"].astype(str)
    df["age_days"] = df["published"].apply(calc_age_days)

    def build_embedding_text(row: pd.Series) -> str:
        parts = []
        if row["title"]:
            parts.append(f"Title: {row['title']}")
        if row["authors_joined"]:
            parts.append(f"Authors: {row['authors_joined']}")
        if row["categories_joined"]:
            parts.append(f"Categories: {row['categories_joined']}")
        if row["published"]:
            parts.append(f"Published: {row['published']}")
        if row["summary"]:
            parts.append(f"Summary: {row['summary']}")
        return "\n".join(parts)

    df["text_for_embedding"] = df.apply(build_embedding_text, axis=1)

    valid_mask = (df["paper_id"].astype(str).str.strip() != "") & (
        (df["title"].astype(str).str.strip() != "") | (df["summary"].astype(str).str.strip() != "")
    )
    filtered_df = df[valid_mask].copy()
    dropped_invalid_count = raw_count - len(filtered_df)

    clean_df = filtered_df.drop_duplicates(subset=["paper_id"], keep="first").copy()
    dropped_dup_count = len(filtered_df) - len(clean_df)

    logger.info(
        "Cleaning summary: Raw=%d, Dropped Invalid=%d, Dropped Duplicates=%d, Cleaned=%d",
        raw_count,
        dropped_invalid_count,
        dropped_dup_count,
        len(clean_df),
    )

    clean_df.sort_values(by="published", ascending=False, inplace=True)
    clean_df.reset_index(drop=True, inplace=True)

    return clean_df

