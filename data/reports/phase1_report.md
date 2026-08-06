# Baseline Data Pipeline & Observability Report (Phase 1)

## 1. Source Summary
- **Source API:** Crossref REST API
- **Query:** agentic retrieval augmented generation large language model
- **Total Records:** 24

## 2. Baseline RAG Performance Metrics
- **Evaluated Samples:** 40
- **Retrieval Hit Rate:** 1.0000 (100.00%)
- **Mean Token F1 Score:** 0.7500
- **LLM Judge Accuracy:** 0.9750 (97.50%)
- **Mean LLM Judge Score:** 4.90 / 5.0

## 3. Data Quality Audit
- **Overall Status:** PASS
- **Total Dataset Rows:** 24
- **row_count:** PASS — Total rows: 24
- **paper_id_integrity:** PASS — Null IDs: 0, Duplicate IDs: 0
- **title_non_null:** PASS — Null titles: 0
- **summary_quality:** PASS — Missing summaries: 0, Short summaries (<100 chars): 0
- **freshness_threshold:** PASS — Stale rows (> 180 days): 0

## 4. Freshness Audit
- **Freshness Status:** FRESH
- **Latest Published:** 2026-08-05
- **Oldest Published:** 2026-02-12
- **Stale Rows (>180 days):** 0
