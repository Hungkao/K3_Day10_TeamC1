from __future__ import annotations

from datetime import datetime, timezone
import logging

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
    """Executes the Phase 2 Corruption, Repair, and Comparison Flow end-to-end."""
    settings = load_settings()
    logger.info("=== STARTING PHASE 2: CORRUPTION & REPAIR FLOW ===")

    # 1. Load Baseline Clean Dataset
    if not settings.paths.clean_csv.exists():
        raise RuntimeError("Clean dataset not found. Please run Phase 1 baseline pipeline first.")
    
    logger.info(f"Loading baseline clean dataset from {settings.paths.clean_csv}...")
    baseline_df = load_cleaned_dataframe(settings.paths.clean_csv)

    # 2. Corrupt Clean Dataframe & Save Corrupted Artifacts
    logger.info("Corrupting clean dataframe...")
    corrupted_df = corrupt_clean_dataframe(baseline_df, settings.paths.corruption_log)
    settings.paths.corrupted_clean_csv.parent.mkdir(parents=True, exist_ok=True)
    corrupted_df.to_csv(settings.paths.corrupted_clean_csv, index=False)
    corrupted_df.to_json(settings.paths.corrupted_clean_json, orient="records", indent=2)

    # 3. Build Chroma Vector Index for Corrupted Data ('papers-corrupted')
    logger.info(f"Building Chroma Index '{settings.corrupted_collection_name}'...")
    corrupted_index = LocalEmbeddingIndex.build(
        corrupted_df,
        settings,
        embeddings_output_path=settings.paths.corrupted_embeddings_json,
    )

    # 4. Evaluate Corrupted Dataset on Same Fixed Test Set
    logger.info("Evaluating RAG Pipeline on corrupted dataset...")
    corrupted_eval = evaluate_pipeline(
        settings,
        corrupted_index,
        settings.paths.eval_testset,
        settings.paths.corrupted_metrics,
        settings.paths.corrupted_answers,
    )
    logger.info(f"Corrupted Metrics Summary: {corrupted_eval.summary}")

    # 5. Run Quality Checks & Freshness Report on Corrupted Data
    logger.info("Running Data Quality and Freshness Checks on corrupted dataset...")
    corrupted_quality = run_data_quality_checks(corrupted_df, settings, "corrupted_quality_check")
    corrupted_freshness = build_freshness_report(
        corrupted_df,
        settings,
        settings.paths.quality_dir / "corrupted_freshness_report.json",
    )

    # 6. Repair Dataset Programmatically from Raw Records Lineage
    logger.info(f"Repairing dataset from raw records lineage: {settings.paths.raw_records_json}...")
    raw_records = load_raw_records(settings.paths.raw_records_json)
    repaired_df = build_clean_dataframe(raw_records, datetime.now(timezone.utc))

    settings.paths.repaired_clean_csv.parent.mkdir(parents=True, exist_ok=True)
    repaired_df.to_csv(settings.paths.repaired_clean_csv, index=False)
    repaired_df.to_json(settings.paths.repaired_clean_json, orient="records", indent=2)

    # 7. Build Chroma Vector Index for Repaired Data ('papers-repaired')
    logger.info(f"Building Chroma Index '{settings.repaired_collection_name}'...")
    repaired_index = LocalEmbeddingIndex.build(
        repaired_df,
        settings,
        embeddings_output_path=settings.paths.repaired_embeddings_json,
    )

    # 8. Evaluate Repaired Dataset on Same Fixed Test Set
    logger.info("Evaluating RAG Pipeline on repaired dataset...")
    repaired_eval = evaluate_pipeline(
        settings,
        repaired_index,
        settings.paths.eval_testset,
        settings.paths.repaired_metrics,
        settings.paths.repaired_answers,
    )
    logger.info(f"Repaired Metrics Summary: {repaired_eval.summary}")

    # 9. Run Quality Checks & Freshness Report on Repaired Data
    logger.info("Running Data Quality and Freshness Checks on repaired dataset...")
    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality_check")
    repaired_freshness = build_freshness_report(
        repaired_df,
        settings,
        settings.paths.quality_dir / "repaired_freshness_report.json",
    )

    # 10. Generate Comparison Report Across 3 States
    logger.info(f"Generating Comparison Report to {settings.paths.comparison_report}...")
    baseline_metrics = read_json(settings.paths.baseline_metrics)
    generate_corruption_report(
        settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_eval.summary,
        repaired_metrics=repaired_eval.summary,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness,
    )

    logger.info("=== PHASE 2 CORRUPTION & REPAIR FLOW COMPLETED SUCCESSFULLY! ===")


if __name__ == "__main__":
    main()

