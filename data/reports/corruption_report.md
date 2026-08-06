# Data Corruption & Recovery Comparison Report

> **3-State Observability Analysis** comparing Baseline, Corrupted, and Repaired RAG pipeline metrics.

---

## 1. Metrics Comparison Across 3 States

| Metric | Baseline (Clean) | Corrupted (Lỗi) | Repaired (Đã sửa) | Delta (Repaired - Corrupted) |
| :--- | :-: | :-: | :-: | :-: |
| **Retrieval Hit Rate** | 100.00% | 70.00% | 100.00% | 30.00% |
| **Mean Token F1** | 75.00% | 57.85% | 75.00% | 17.15% |
| **LLM Judge Accuracy** | 100.00% | 57.50% | 72.50% | 15.00% |
| **Mean LLM Judge Score** | 5.00 / 5 | 3.45 / 5 | 3.90 / 5 | +0.45 |

---

## 2. Observability & Quality Signals

| Signal | Baseline | Corrupted | Repaired |
| :--- | :-: | :-: | :-: |
| **Quality Status** | PASS | FAIL | PASS |
| **Freshness Status** | FRESH | STALE | FRESH |
| **Stale Rows** | 0 | 2 | 0 |

---

## 3. Causal Impact & Recovery Findings
1. **Corruption Impact**: Injecting data flaws (missing summaries, stale publication dates, content noise) caused quality signals to turn **FAIL/STALE** and directly reduced RAG retrieval accuracy and LLM judge scores.
2. **Snapshot Repair Recovery**: Rebuilding the pipeline from saved raw Crossref records successfully restored data quality checks and returned RAG performance metrics back to baseline levels.

---
*Report generated automatically by Data Observability Module.*
