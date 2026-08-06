from __future__ import annotations

from datetime import datetime, timezone
import logging

from core.config import load_settings
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe, load_cleaned_dataframe
from ingestion.crossref import fetch_source_records, load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_phase1_report
from retrieval.index import LocalEmbeddingIndex

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Executes the Phase 1 Baseline Pipeline end-to-end."""
    settings = load_settings()
    logger.info("=== STARTING PHASE 1: BASELINE PIPELINE ===")

    # 1. Load or Fetch Raw Records
    if settings.paths.raw_records_json.exists() and not settings.refresh_source:
        logger.info(f"Loading raw records from snapshot: {settings.paths.raw_records_json}")
        raw_records = load_raw_records(settings.paths.raw_records_json)
    else:
        logger.info("Fetching raw records from Crossref API...")
        raw_records = fetch_source_records(settings)

    # 2. Clean Data & Save Clean CSV/JSON
    if settings.paths.clean_csv.exists() and not settings.refresh_source:
        logger.info(f"Loading cleaned dataset from CSV: {settings.paths.clean_csv}")
        clean_df = load_cleaned_dataframe(settings.paths.clean_csv)
    else:
        logger.info("Cleaning raw records into DataFrame...")
        clean_df = build_clean_dataframe(raw_records, datetime.now(timezone.utc))
        settings.paths.clean_csv.parent.mkdir(parents=True, exist_ok=True)
        clean_df.to_csv(settings.paths.clean_csv, index=False)
        clean_df.to_json(settings.paths.clean_json, orient="records", indent=2)

    # 3. Build Chroma Vector Index 'papers-baseline'
    logger.info(f"Building Chroma Index '{settings.baseline_collection_name}'...")
    index = LocalEmbeddingIndex.build(clean_df, settings, settings.paths.embeddings_json)

    # 4. Create or Load Evaluation Test Set
    if settings.paths.eval_testset.exists() and not settings.refresh_test_set:
        logger.info(f"Using existing test set: {settings.paths.eval_testset}")
    else:
        logger.info("Building evaluation test set...")
        build_test_set(clean_df, settings.paths.eval_testset)

    # 5. Evaluate Baseline RAG Pipeline
    logger.info("Evaluating RAG Pipeline on baseline test set...")
    eval_bundle = evaluate_pipeline(
        settings,
        index,
        settings.paths.eval_testset,
        settings.paths.baseline_metrics,
        settings.paths.baseline_answers,
    )
    logger.info(f"Baseline Summary: {eval_bundle.summary}")

    # 6. Run Quality Checks & Freshness Report
    logger.info("Running Data Quality and Freshness Checks...")
    quality_res = run_data_quality_checks(clean_df, settings, "baseline_quality_check")
    freshness_res = build_freshness_report(clean_df, settings, settings.paths.freshness_report)

    # 7. Generate Phase 1 Markdown Report
    logger.info(f"Exporting Phase 1 Report to {settings.paths.baseline_report}...")
    generate_phase1_report(
        settings.paths.baseline_report,
        {"source_api": settings.source_api, "source_query": settings.source_query},
        eval_bundle.summary,
        quality_res,
        freshness_res,
    )

    logger.info("=== PHASE 1 BASELINE PIPELINE COMPLETED SUCCESSFULLY! ===")


if __name__ == "__main__":
    main()

