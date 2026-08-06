# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin       | Nội dung                                                   |
| --------------- | ---------------------------------------------------------- |
| Họ và tên       | Nguyễn Tuấn Vũ                                             |
| MSSV            | 2A202601845                                                |
| Khóa/Lớp        | K3                                                         |
| Tên nhóm        | Team C1                                                    |
| Vai trò chính   | Lead / Ingestion & Observability & Pipeline Integration     |
| Repository      | `c:\AI20K\LABS\K3_Day10_TeamC1`                            |
| Ngày hoàn thành | 2026-08-06                                                 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| ------------------ | ------------------ | -------------- | ----------------- | ------------------------------------- |
| Raw Data Ingestion | `src/ingestion/crossref.py` | Crossref API (`https://api.crossref.org/works`) | `data/raw/crossref_response.json`, `data/raw/crossref_records.json` | Đang triển khai |
| Cleaning & Data Modeling | `src/ingestion/cleaning.py` | Raw Records JSON | `data/clean/papers_clean.csv`, `data/clean/papers_clean.json` | Đang triển khai |
| Evaluation Test Set | `src/evaluation/testset.py` | Clean Data JSON | `data/eval/test_set.json` (Frozen QA set) | Đang triển khai |
| Data Observability | `src/observability/quality.py`, `src/observability/reporting.py` | Clean & Corrupted Datasets | Quality & Freshness reports (`data/quality/`, `data/reports/`) | Đang triển khai |
| Pipelines & Corruption Flow | `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`, `src/ingestion/corruption.py` | Clean & Raw Datasets | Baseline, Corrupted & Repaired Metrics (`data/results/`) | Đang triển khai |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --------- | ----------------------------- | ------- |
| Quản lý Hướng dẫn & Contract | Cả nhóm | [`Guide_labs.md`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/Guide_labs.md) |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------- | --------------------------- | ------------------------- | --------------- |
| Khởi tạo Hướng dẫn chính bài lab | [`Guide_labs.md`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/Guide_labs.md) | Tài liệu hướng dẫn chuẩn Day 10 K3 | Kiểm tra file |

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Xây dựng pipeline RAG end-to-end cho dữ liệu bài báo học thuật Crossref, đo lường tác động của lỗi dữ liệu (Data Corruption) lên chất lượng RAG/Agent, chứng minh cơ chế giám sát (Data Observability) và khôi phục (Data Repair) từ bản sao lưu thô (raw snapshot).

### Cách triển khai
- **Pha 1**: Crossref Ingestion $\rightarrow$ Cleaning & Freshness $\rightarrow$ Freeze Test Set $\rightarrow$ Embedding/ChromaDB $\rightarrow$ Data Quality Checks $\rightarrow$ Run Phase 1 Baseline (`script/run_phase1.py`).
- **Pha 2**: Inject Controlled Corruption $\rightarrow$ Measure Impact $\rightarrow$ Repair from Raw Records $\rightarrow$ Compare Baseline vs Corrupted vs Repaired (`script/run_corruption_flow.py`).

---
*Báo cáo sẽ tiếp tục cập nhật đầy đủ số liệu sau khi thực thi các pipeline.*
