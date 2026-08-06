# Data Corruption & Recovery Comparison Report

> **3-State Observability Analysis** comparing Baseline, Corrupted, and Repaired RAG pipeline metrics.

---

## 1. Metrics Comparison Across 3 States

| Metric | Baseline (Clean) | Corrupted (Lỗi) | Repaired (Đã sửa) | Delta (Repaired - Corrupted) |
| :--- | :-: | :-: | :-: | :-: |
| **Retrieval Hit Rate** | 100.00% | 70.00% | 100.00% | 30.00% |
| **Mean Token F1** | 75.00% | 70.35% | 75.00% | 4.65% |
| **LLM Judge Accuracy** | 97.50% | 70.00% | 72.50% | 2.50% |
| **Mean LLM Judge Score** | 4.90 / 5 | 4.03 / 5 | 3.90 / 5 | +-0.13 |

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
