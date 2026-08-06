# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| ------------------ | -------------------------- |
| Họ và tên | Nguyễn Phúc Hưng |
| MSSV | 2A202601115 |
| Khóa/Lớp | K3 - Team C1 |
| Tên nhóm | Team C1 |
| Vai trò chính | Role 1 — Pipeline Orchestration, Integration & Release Lead |
| Repository | https://github.com/Hungkao/K3_Day10_TeamC1 |
| Ngày hoàn thành | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Configuration & Core Utils | `src/core/config.py`, `src/core/utils.py` | Environment variables, `.env` file | Settings instance & paths config | Hoàn thành |
| Raw Data Ingestion Integration | `src/ingestion/crossref.py` | Crossref REST API parameters | Raw response & records JSON files | Hoàn thành |
| Phase 1 Baseline Pipeline | `src/pipelines/phase1.py` | Settings & Clean dataset | Baseline artifacts (`data/results/`, `data/reports/phase1_report.md`) | Hoàn thành |
| Phase 2 Corruption Pipeline | `src/pipelines/corruption_flow.py` | Baseline settings & Raw snapshot | Corruption report (`data/reports/corruption_report.md`) | Hoàn thành |
| Automation Scripts & Release | `script/run_phase1.py`, `script/run_corruption_flow.py` | Command line arguments | Executable workflow entry points | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả và bằng chứng |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Đánh giá RAG Evaluation | Role 3 (RAG/Agent Specialist) | Phối hợp tích hợp module evaluation trong pipeline end-to-end |
| Observability Reporting | Role 4 (Eval & Observability) | Đảm bảo pipeline gọi đúng hàm sinh markdown report tự động |
| Quản lý Repository & Merge Lead | Cả nhóm (Team C1) | Quản lý branching strategy, merge code và resolve xung đột Git |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Xây dựng hệ thống Cấu hình trung tâm | `src/core/config.py` | Nạp biến môi trường an toàn, quản lý toàn bộ đĩa đệm đường dẫn `Paths` | Run test settings pass 100% |
| Tích hợp Baseline Orchestration Pipeline | `src/pipelines/phase1.py` | Chạy liên hoàn 7 bước từ API -> Cleaning -> Vector DB -> Eval -> Observability | `python script/run_phase1.py` |
| Tích hợp Phase 2 Corruption & Repair Flow | `src/pipelines/corruption_flow.py` | Điều phối luồng 3 trạng thái (Baseline, Corrupted, Repaired) | `python script/run_corruption_flow.py` |
| Quản lý Release & Git Integration | GitHub Repository | Nhánh `main` sạch sẽ, đồng bộ 100% không còn xung đột | Git commit history trên GitHub |

**Artifact cụ thể đã tạo ra:**
- Workflow điều phối tự động: `src/pipelines/phase1.py` và `src/pipelines/corruption_flow.py` chạy thành công end-to-end không bị gián đoạn.

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Kết nối các module riêng lẻ của 4 thành viên (Ingestion, Cleaning, Vector Search, Evaluation, Observability) thành một đường ống dữ liệu (Data Pipeline) chạy tự động liên hoàn từ đầu đến cuối, đảm bảo tính tái tạo kết quả (Reproducibility) và không bị rò rỉ API key.

### Cách triển khai
1. **Core Settings (`src/core/config.py`)**: Đóng gói toàn bộ thông số mô hình (LLM, Embedding, Top-k, Freshness threshold) và đường dẫn file đĩa (`Paths`) vào một dataclass tập trung. Đảm bảo nạp an toàn API key từ `.env` hoặc biến môi trường mà không hardcode trong mã nguồn.
2. **Phase 1 Pipeline (`src/pipelines/phase1.py`)**: Orchestrate 7 bước:
   - Load/fetch raw records $\rightarrow$ Clean dataset $\rightarrow$ Build Chroma index `papers-baseline` $\rightarrow$ Load frozen test set $\rightarrow$ Evaluate RAG $\rightarrow$ Run quality & freshness checks $\rightarrow$ Export `phase1_report.md`.
3. **Phase 2 Pipeline (`src/pipelines/corruption_flow.py`)**: Orchestrate luồng so sánh 3 trạng thái:
   - Build corrupted dataset $\rightarrow$ Re-index `papers-corrupted` $\rightarrow$ Evaluate RAG $\rightarrow$ Run corrupted observability checks.
   - Re-clean từ snapshot thô `crossref_records.json` $\rightarrow$ Re-index `papers-repaired` $\rightarrow$ Evaluate RAG $\rightarrow$ Run repaired observability checks.
   - Gọi `generate_corruption_report` xuất báo cáo so sánh 3 cột tại `corruption_report.md`.

### Input, output và contract

| Thành phần | Mô tả |
| ------------------------------ | ------------------------------------------- |
| Input | Raw Crossref records, Clean DataFrame, Frozen Test Set JSON |
| Output | Metrics JSONs (`baseline`, `corrupted`, `repaired`), Reports Markdown (`phase1_report.md`, `corruption_report.md`) |
| Module phụ thuộc | Tất cả các module trong `src/ingestion/`, `src/retrieval/`, `src/evaluation/`, `src/observability/` |
| Module sử dụng output | `script/run_phase1.py`, `script/run_corruption_flow.py`, Báo cáo nhóm `group_report.md` |
| Điều kiện lỗi cần xử lý | Xung đột phiên bản ChromaDB index, lỗi hết token LLM, mất kết nối API |

### Cách xác minh

```bash
python script/run_phase1.py
python script/run_corruption_flow.py
```

- **Kết quả mong đợi:** Cả 2 script chạy mượt mà từ đầu đến cuối, in log từng bước rõ ràng và sinh đầy đủ các file kết quả tại `data/results/`, `data/quality/` và `data/reports/`.
- **Kết quả thực tế:** Chạy thành công 100%, Retrieval Hit Rate đạt 100% ở Baseline, giảm xuống 70% ở Corrupted và phục hồi về 100% ở Repaired.
- **Artifact/log:** `data/reports/phase1_report.md` và `data/reports/corruption_report.md`.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn phương pháp quản lý và truy cập các đường dẫn đĩa (File System Paths) giữa các module trong toàn bộ dự án.
- **Các phương án đã cân nhắc:**
  - *Phương án 1*: Để từng module tự hardcode đường dẫn file tương đối (ví dụ `../data/clean/papers_clean.json`).
  - *Phương án 2*: Tập trung toàn bộ đường dẫn vào dataclass `Paths` trong `src/core/config.py` và truyền đối tượng `Settings` vào tất cả các hàm.
- **Phương án đã chọn:** Phương án 2 (Centralized Config & Paths Dataclass).
- **Lý do:** Giúp loại bỏ hoàn toàn lỗi gõ sai đường dẫn, đảm bảo tính nhất quán trên các hệ điều hành khác nhau (Windows / Linux / macOS), dễ dàng thay đổi thư mục lưu trữ khi cần mà không phải sửa code ở nhiều nơi.
- **Bằng chứng quyết định phù hợp:** Toàn bộ pipeline chạy trên môi trường Windows PowerShell của nhóm không gặp bất kỳ lỗi `FileNotFoundError` nào liên quan đến đường dẫn.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```text
  chromadb.errors.NotFoundError: Error getting collection: Collection [papers-baseline] does not exist.
  ```
- **Lệnh hoặc bước tái hiện:** Chạy script `run_phase1.py` sau khi xóa thư mục `data/chroma/` để làm sạch cache.
- **Nguyên nhân gốc:** Hàm khởi tạo `LocalEmbeddingIndex` cố gắng gọi `client.get_collection()` trước khi collection được tạo hoặc khi cache ChromaDB SQLite bị xóa nhưng client persistent chưa kịp sync.
- **Cách xử lý:** Bổ sung cơ chế tự động xóa/tạo mới collection an toàn trong `LocalEmbeddingIndex.build()`:
  ```python
  try:
      client.delete_collection(name=collection_name)
  except Exception:
      pass
  collection = client.create_collection(name=collection_name)
  ```
- **Cách xác minh sau khi sửa:** Xóa thư mục `data/chroma/` và chạy lại `python script/run_phase1.py` $\rightarrow$ Collection được tự động khởi tạo lại sạch sẽ mà không gặp lỗi.
- **Điều học được:** Khi làm việc với cơ sở dữ liệu Vector lưu trữ local, luôn cần thiết kế cơ chế khoanh vùng ngoại lệ và tự khởi tạo an toàn (Idempotent initialization).

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   - API trả về response $\rightarrow$ Ingestion lưu raw snapshot $\rightarrow$ Cleaning làm sạch HTML/XML và ghép `text_for_embedding` $\rightarrow$ Embedding model `all-MiniLM-L6-v2` tạo vector 384 chiều $\rightarrow$ Lưu vào ChromaDB persistent store.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   - Bộ 40 câu hỏi đóng băng chứa `ground_truth_doc_ids`. Khi RAG chạy, nó tìm top-k bài báo; nếu bài báo tìm được chứa ID chuẩn thì `retrieval_hit = True`. Đáp án được chấm điểm ngữ nghĩa bởi LLM Judge (1-5 điểm) và F1 từ vựng.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - Quality checks kiểm tra tính đầy đủ/toàn vẹn cấu trúc (dữ liệu rỗng, trùng mã ID, tiêu đề thiếu). Freshness monitoring đo tuổi dữ liệu (`age_days`) so với mốc hiện tại để đảm bảo tính cập nhật.
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   - Để đảm bảo tính khách quan và đo lường công bằng. Cùng một thước đo mới chứng minh được dữ liệu xấu làm suy giảm RAG và dữ liệu sửa giúp phục hồi RAG.
5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   - Repair thành công khi Quality Check báo `PASS`, Freshness báo `FRESH`, và Retrieval Hit Rate phục hồi về 100% trong `corruption_report.md`.

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` | 100.00% | 70.00% | 100.00% | Dữ liệu bị rỗng summary khiến retrieval sụt 30%; Repair khôi phục về 100% |
| `mean_token_f1` | 75.00% | 57.85% | 75.00% | F1 giảm mạnh khi thiếu ngữ cảnh tóm tắt; Repair đưa chỉ số về ban đầu |
| `judge_accuracy` | 97.50% | 57.50% | 72.50% | Tỷ lệ câu trả lời hoàn hảo của LLM Judge bị giảm khi gặp dữ liệu nhiễu |
| `mean_judge_score` | 4.90 / 5 | 3.45 / 5 | 3.90 / 5 | Điểm số chất lượng câu trả lời bị tụt 1.45 điểm khi dữ liệu lỗi |
| Quality checks | PASS | FAIL | PASS | Quality Engine phát hiện chính xác lỗi rỗng summary và trùng ID |
| Freshness status | FRESH | STALE | FRESH | Freshness Engine tự động cảnh báo STALE khi ngày bị lùi về quá khứ |

### Kết luận từ số liệu

1. **[Data corruption] -> [quality/freshness signal thay đổi] -> [agent metric thay đổi]**:
   - Khi làm hỏng dữ liệu $\rightarrow$ Quality check chuyển `FAIL`, Freshness chuyển `STALE` $\rightarrow$ Retrieval Hit Rate sụt từ 100% xuống 70%, F1 tụt xuống 57.85%.
2. **[Repair action] -> [quality/freshness signal phục hồi] -> [agent metric phục hồi]**:
   - Khi Re-clean dữ liệu từ raw snapshot $\rightarrow$ Quality check quay về `PASS`, Freshness quay về `FRESH` $\rightarrow$ Retrieval Hit Rate phục hồi 100%.

- **Corruption ảnh hưởng rõ nhất:** Việc **xóa tóm tắt (Blank Summary)** gây suy giảm nặng nhất vì tóm tắt là ngữ cảnh chính cho vector search.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Về Data Pipeline**: Thiết kế pipeline dạng modular và có orchestration script giúp dự án dễ bảo trì và mở rộng.
2. **Về Data Quality/Observability**: Tích hợp kiểm tra chất lượng dữ liệu ngay trong pipeline giúp phát hiện sớm sự cố.
3. **Về ảnh hưởng của Data đến RAG Agent**: Chất lượng dữ liệu đầu vào quyết định 90% hiệu năng của RAG Agent.

### Nếu có thêm thời gian

- Xây dựng giao diện Web Dashboard (dùng Streamlit/Gradio) để hiển thị báo cáo Observability và cho phép chọn kịch bản corruption trực quan.

---

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Phúc Hưng  
**Ngày xác nhận:** 2026-08-06
