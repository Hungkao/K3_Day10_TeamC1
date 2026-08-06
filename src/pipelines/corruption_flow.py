from __future__ import annotations

from datetime import datetime, timezone
import logging
import pandas as pd

from core.config import load_settings
from core.utils import read_json
from evaluation.metrics import evaluate_pipeline
from ingestion.cleaning import build_clean_dataframe, load_cleaned_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from ingestion.crossref import load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_corruption_report
from retrieval.index import LocalEmbeddingIndex

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Executes the complete Corruption, Evaluation, Repair & 3-State Comparison pipeline."""
    settings = load_settings()
    logger.info("=== STARTING PHASE 2: CORRUPTION, REPAIR & COMPARISON PIPELINE ===")

    # 1. Load Baseline Metrics & Clean Dataset
    logger.info("Step 1: Loading Baseline Metrics & Clean Dataset...")
    baseline_metrics = read_json(settings.paths.baseline_metrics)
    clean_df = load_cleaned_dataframe(settings.paths.clean_csv)

    # 2. Build or Load Corrupted Dataset
    if settings.paths.corrupted_clean_csv.exists() and settings.paths.corrupted_clean_json.exists():
        logger.info(f"Loading corrupted dataset from CSV: {settings.paths.corrupted_clean_csv}")
        corrupted_df = load_cleaned_dataframe(settings.paths.corrupted_clean_csv)
    else:
        logger.info("Simulating data corruption...")
        corrupted_df = corrupt_clean_dataframe(clean_df, settings.paths.corruption_log)
        corrupted_df.to_csv(settings.paths.corrupted_clean_csv, index=False)
        corrupted_df.to_json(settings.paths.corrupted_clean_json, orient="records", indent=2)

    # 3. Build Chroma Index 'papers-corrupted'
    logger.info(f"Step 2: Building Chroma Index '{settings.corrupted_collection_name}'...")
    corrupted_index = LocalEmbeddingIndex.build(corrupted_df, settings, settings.paths.corrupted_embeddings_json)

    # 4. Evaluate RAG on Corrupted Dataset
    logger.info("Step 3: Evaluating RAG Pipeline on Corrupted Dataset...")
    corrupted_bundle = evaluate_pipeline(
        settings,
        corrupted_index,
        settings.paths.eval_testset,
        settings.paths.corrupted_metrics,
        settings.paths.corrupted_answers,
    )
    logger.info(f"Corrupted Summary: {corrupted_bundle.summary}")

    # 5. Run Quality & Freshness Checks on Corrupted Dataset
    logger.info("Step 4: Running Observability Checks on Corrupted Dataset...")
    corrupted_quality = run_data_quality_checks(corrupted_df, settings, "corrupted_quality_check")
    corrupted_freshness = build_freshness_report(
        corrupted_df, settings, settings.paths.quality_dir / "corrupted_freshness_report.json"
    )

    # 6. Repair Data from Saved Raw Snapshot
    logger.info("Step 5: Repairing Dataset from Saved Raw Snapshot...")
    raw_records = load_raw_records(settings.paths.raw_records_json)
    repaired_df = build_clean_dataframe(raw_records, datetime.now(timezone.utc))
    repaired_df.to_csv(settings.paths.repaired_clean_csv, index=False)
    repaired_df.to_json(settings.paths.repaired_clean_json, orient="records", indent=2)

    # 7. Build Chroma Index 'papers-repaired'
    logger.info(f"Step 6: Building Chroma Index '{settings.repaired_collection_name}'...")
    repaired_index = LocalEmbeddingIndex.build(repaired_df, settings, settings.paths.repaired_embeddings_json)

    # 8. Evaluate RAG on Repaired Dataset
    logger.info("Step 7: Evaluating RAG Pipeline on Repaired Dataset...")
    repaired_bundle = evaluate_pipeline(
        settings,
        repaired_index,
        settings.paths.eval_testset,
        settings.paths.repaired_metrics,
        settings.paths.repaired_answers,
    )
    logger.info(f"Repaired Summary: {repaired_bundle.summary}")

    # 9. Run Quality & Freshness Checks on Repaired Dataset
    logger.info("Step 8: Running Observability Checks on Repaired Dataset...")
    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality_check")
    repaired_freshness = build_freshness_report(
        repaired_df, settings, settings.paths.quality_dir / "repaired_freshness_report.json"
    )

    # 10. Generate 3-State Comparison Markdown Report
    logger.info(f"Step 9: Exporting 3-State Comparison Report to {settings.paths.comparison_report}...")
    generate_corruption_report(
        settings.paths.comparison_report,
        baseline_metrics,
        corrupted_bundle.summary,
        repaired_bundle.summary,
        corrupted_quality,
        repaired_quality,
        corrupted_freshness,
        repaired_freshness,
    )

    logger.info("=== PHASE 2 CORRUPTION, REPAIR & COMPARISON PIPELINE COMPLETED SUCCESSFULLY! ===")


if __name__ == "__main__":
    main()
