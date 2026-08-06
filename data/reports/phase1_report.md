# Phase 1 Baseline Report — Data Pipeline & Observability

> **Baseline Report** evaluating data ingestion, cleaning, retrieval metrics, and data observability signals.

---

## 1. Source Summary
- **Source API**: Crossref REST API
- **Query**: `agentic retrieval augmented generation large language model`
- **Max Results Ingested**: 24
- **Cleaned Records Count**: 24

---

## 2. RAG Evaluation Metrics (Baseline)
- **Total Test Samples**: `40`
- **Retrieval Hit Rate**: `100.00%` (1.0000)
- **Mean Token F1**: `95.00%` (0.9500)
- **LLM Judge Accuracy**: `100.00%` (1.0000)
- **Mean LLM Judge Score**: `4.80 / 5.0`

---

## 3. Data Observability & Freshness Signals
- **Data Quality Status**: **PASS**
- **Total Rows Checked**: `24`
- **Missing / Null Titles**: `0`
- **Missing Summaries**: `0`
- **Duplicate Paper IDs**: `0`

### Freshness Status
- **Latest Published Date**: `2026-08-05`
- **Oldest Published Date**: `2026-02-12`
- **Stale Rows (> threshold)**: `0`
- **Is Dataset Fresh?**: **True**

---
*Report generated automatically by Data Observability Module.*
