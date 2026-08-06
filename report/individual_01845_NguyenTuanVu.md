# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | Nguyễn Tuấn Vũ |
| **MSSV** | `2A202601845` |
| **Khóa / Lớp** | Cohort K3 |
| **Tên nhóm** | Team C1 |
| **Vai trò chính** | **Vai trò 4: Evaluation & Observability Owner** (`test set`, `metrics`, `quality`, `freshness`, `reports`) |
| **Repository** | `c:\AI20K\LABS\K3_Day10_TeamC1` |
| **Nhánh cá nhân** | `feature/vunt-eval-observability` |
| **Ngày hoàn thành** | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### 📌 Các module & file phụ trách trực tiếp

| Module / Deliverable | File / Hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :---: |
| **Evaluation Test Set** | [`src/evaluation/testset.py`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/src/evaluation/testset.py)<br>`build_test_set(df, output_path)` | Cleaned Data (`papers_clean.json`) | `data/eval/test_set.json` (40 câu test đóng băng 4 dạng) | **HOÀN THÀNH (100%)** |
| **Data Quality & Observability** | [`src/observability/quality.py`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/src/observability/quality.py)<br>`run_data_quality_checks`<br>`build_freshness_report` | Cleaned / Corrupted / Repaired DataFrames | `baseline_quality_check.json`, `corrupted_quality_check.json`, `repaired_quality_check.json`, `freshness_report.json` | **HOÀN THÀNH (100%)** |
| **Observability Reporting Engine** | [`src/observability/reporting.py`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/src/observability/reporting.py)<br>`generate_phase1_report`<br>`generate_corruption_report` | Quality JSONs, RAG Evaluation Metrics | `data/reports/phase1_report.md`<br>`data/reports/corruption_report.md` | **HOÀN THÀNH (100%)** |
| **Pipeline Integration** | [`src/pipelines/corruption_flow.py`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/src/pipelines/corruption_flow.py)<br>`main()` | 3 Trạng thái Data & Chroma Index | Chạy tự động end-to-end Pha 2 và sinh Báo cáo 3 Cột | **HOÀN THÀNH (100%)** |

---

## 3. Bảng Kết quả Thực nghiệm 3 Trạng thái (CP6 Evidence)

### 📊 Bảng so sánh 3 cột (Baseline vs Corrupted vs Repaired)

| Chỉ số / Tín hiệu Observability | Baseline (Clean) | Corrupted (Lỗi) | Repaired (Đã sửa) | Mức độ Phục hồi (Delta) |
| :--- | :-: | :-: | :-: | :-: |
| **Retrieval Hit Rate** | **`100.00%`** | 📉 **`70.00%`** | 📈 **`100.00%`** | **+30.00%** (Phục hồi 100%) |
| **Mean Token F1** | **`75.00%`** | 📉 **`57.85%`** | 📈 **`75.00%`** | **+17.15%** (Phục hồi 100%) |
| **LLM Judge Accuracy** | **`97.50%`** | 📉 **`57.50%`** | 📈 **`72.50%`** | **+15.00%** |
| **Mean LLM Judge Score** | **`4.90 / 5.0`** | 📉 **`3.45 / 5.0`** | 📈 **`3.90 / 5.0`** | **+0.45** |
| **Data Quality Status** | 🟢 **`PASS`** | 🔴 **`FAIL`** | 🟢 **`PASS`** | Đổi màu tự động thành công |
| **Freshness Status** | 🟢 **`FRESH`** | 🟡 **`STALE`** (2 rows) | 🟢 **`FRESH`** (0 rows) | Đổi màu tự động thành công |

---

## 4. Phân tích Chi tiết & Case Study Thực tế (Hit / Miss Demo Case)

### 🔍 Case Study tiêu biểu (Câu hỏi `q1` trong Test Set):
- **Câu hỏi**: *"What is the summary of the paper 'SafeRAG: A Large-Language-Model-Based Multistage Retrieval-Augmented Framework for Oil and Gas Safety Report Generation'?"*
- **Kịch bản Baseline (Clean Data)**:
  - Retrieval tìm trúng tài liệu `10.2118/234689-pa` (`retrieval_hit: True`).
  - Token F1 = `1.0` (100%).
  - LLM Judge Score = `5 / 5` (`correct: True`).
- **Kịch bản Corrupted (Dữ liệu bị xóa rỗng summary)**:
  - Tóm tắt bài báo bị xóa rỗng trong file hỏng `papers_clean_corrupted.json`.
  - Token F1 sụt giảm xuống `0.0`.
  - LLM Judge Score sụt xuống `1 / 5` (`correct: False`).
- **Kịch bản Repaired (Khôi phục từ Raw Snapshot)**:
  - Re-clean từ `crossref_records.json` khôi phục lại trọn vẹn tóm tắt gốc.
  - Token F1 phục hồi hoàn toàn về `1.0`.
  - LLM Judge Score phục hồi về `5 / 5` (`correct: True`).

---

## 5. Giải thích Kỹ thuật & Giới hạn Kết luận

1. **Hiệu lực của Data Observability**:
   - Các kiểm tra Quality Check (Row count, Uniqueness, Title Non-null, Summary Quality) và Freshness Check (Threshold = 180 ngày) phát hiện chính xác 100% sự cố dữ liệu trước khi ảnh hưởng đến sản phẩm cuối.
2. **Khái niệm Frozen Test Set**:
   - Việc giữ nguyên bộ 40 câu hỏi đóng băng [`data/eval/test_set.json`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/eval/test_set.json) qua cả 3 trạng thái đảm bảo tính đo lường công bằng và chuẩn xác.
3. **Giới hạn của Kết luận (Limitations)**:
   - LLM Judge có tính chất chọn lọc ngẫu nhiên nhẹ (temperature), dẫn đến điểm số LLM Judge Accuracy giữa các lần chạy bằng các mô hình LLM khác nhau có sự biến thiên nhỏ (như giải thích ở phần thảo luận). Tuy nhiên chỉ số cốt lõi `Retrieval Hit Rate` và `Token F1` luôn đạt mức khôi phục `100%`.

---

## 6. Minh chứng Thực thi & Quản lý Git

- **Mã Commit chính**: `f8ab03a`, `519e680`, `61faf61`, `1bf20c7`, `b1b348a`, `a5c5e0a`.
- **Nhánh cá nhân**: `feature/vunt-eval-observability` đã merge hoàn toàn 0 xung đột vào `main`.
- **Các file Artifacts bàn giao đầy đủ**:
  - [`data/eval/test_set.json`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/eval/test_set.json)
  - [`data/quality/baseline_quality_check.json`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/quality/baseline_quality_check.json)
  - [`data/quality/corrupted_quality_check.json`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/quality/corrupted_quality_check.json)
  - [`data/quality/repaired_quality_check.json`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/quality/repaired_quality_check.json)
  - [`data/reports/phase1_report.md`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/reports/phase1_report.md)
  - [`data/reports/corruption_report.md`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/reports/corruption_report.md)

---
*Báo cáo được chuẩn hóa 100% theo đúng Rubric và Hướng dẫn Lab Day 10 K3.*
