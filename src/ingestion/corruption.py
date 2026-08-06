from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import write_json

logger = logging.getLogger(__name__)


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path: Path | str) -> pd.DataFrame:
    """Simulate data corruption on clean dataframe and log corruption details."""
    if df.empty:
        logger.warning("Empty dataframe provided to corrupt_clean_dataframe.")
        return df.copy()

    corrupted_df = df.copy()
    raw_total = len(corrupted_df)
    corruption_events: list[dict[str, Any]] = []

    # 1. Drop latest records (e.g. top 3 rows after sorting by published desc)
    corrupted_df.sort_values(by="published", ascending=False, inplace=True)
    corrupted_df.reset_index(drop=True, inplace=True)

    dropped_count = min(3, len(corrupted_df))
    dropped_rows = corrupted_df.iloc[:dropped_count].copy()
    corrupted_df = corrupted_df.iloc[dropped_count:].copy().reset_index(drop=True)

    for _, row in dropped_rows.iterrows():
        corruption_events.append(
            {
                "paper_id": str(row["paper_id"]),
                "type": "drop_latest_record",
                "details": f"Dropped latest record published on {row['published']}",
            }
        )

    # 2. Blank summary on 3 rows
    if len(corrupted_df) >= 3:
        blank_indices = [0, 1, 2]
        for idx in blank_indices:
            pid = str(corrupted_df.at[idx, "paper_id"])
            corrupted_df.at[idx, "summary"] = ""
            corrupted_df.at[idx, "summary_chars"] = 0
            corruption_events.append(
                {
                    "paper_id": pid,
                    "type": "blank_summary",
                    "details": "Cleared summary text to empty string",
                }
            )

    # 3. Inject noise into summary on 2 rows
    if len(corrupted_df) >= 5:
        noise_indices = [3, 4]
        noise_text = " [CORRUPTED_NOISE: ### GIBBERISH DATA NOISE 9999 ###] "
        for idx in noise_indices:
            pid = str(corrupted_df.at[idx, "paper_id"])
            original_summary = str(corrupted_df.at[idx, "summary"])
            corrupted_df.at[idx, "summary"] = original_summary + noise_text
            corrupted_df.at[idx, "summary_chars"] = len(corrupted_df.at[idx, "summary"])
            corruption_events.append(
                {
                    "paper_id": pid,
                    "type": "inject_noise",
                    "details": "Appended noise text into summary",
                }
            )

    # 4. Truncate title on 2 rows
    if len(corrupted_df) >= 7:
        trunc_indices = [5, 6]
        for idx in trunc_indices:
            pid = str(corrupted_df.at[idx, "paper_id"])
            original_title = str(corrupted_df.at[idx, "title"])
            corrupted_df.at[idx, "title"] = original_title[:10] + "..."
            corruption_events.append(
                {
                    "paper_id": pid,
                    "type": "truncate_title",
                    "details": f"Truncated title from '{original_title}' to '{corrupted_df.at[idx, 'title']}'",
                }
            )

    # 5. Stale published date (e.g. set to 2015-01-01) on 2 rows
    if len(corrupted_df) >= 9:
        stale_indices = [7, 8]
        stale_date = "2015-01-01"
        for idx in stale_indices:
            pid = str(corrupted_df.at[idx, "paper_id"])
            original_date = str(corrupted_df.at[idx, "published"])
            corrupted_df.at[idx, "published"] = stale_date
            corrupted_df.at[idx, "age_days"] = 3800
            corruption_events.append(
                {
                    "paper_id": pid,
                    "type": "stale_published_date",
                    "details": f"Changed published date from '{original_date}' to '{stale_date}'",
                }
            )

    # 6. Add duplicate rows (duplicate 2 existing rows)
    if len(corrupted_df) >= 2:
        dup_rows = corrupted_df.iloc[:2].copy()
        for _, row in dup_rows.iterrows():
            corruption_events.append(
                {
                    "paper_id": str(row["paper_id"]),
                    "type": "duplicate_row",
                    "details": "Duplicated row in corrupted dataset",
                }
            )
        corrupted_df = pd.concat([corrupted_df, dup_rows], ignore_index=True)

    # 7. Rebuild text_for_embedding
    def rebuild_embedding_text(row: pd.Series) -> str:
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

    corrupted_df["text_for_embedding"] = corrupted_df.apply(rebuild_embedding_text, axis=1)

    # 8. Write corruption log
    log_payload = {
        "raw_total_rows": raw_total,
        "corrupted_total_rows": len(corrupted_df),
        "total_corruption_events": len(corruption_events),
        "events": corruption_events,
    }

    log_path = Path(output_log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(log_path, log_payload)

    logger.info("Corrupted dataframe created: %d rows, %d events logged to %s", len(corrupted_df), len(corruption_events), log_path)
    return corrupted_df

