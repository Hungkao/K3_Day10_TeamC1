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
| Configuration System | `src/core/config.py` | Environment variables, `.env` | Class `Settings`, `PathSettings` | Hoàn thành |
| Utility Functions | `src/core/utils.py` | Text, JSON payloads | Safe string format, JSON I/O, Slug helpers | Hoàn thành |
| Baseline Pipeline | `src/pipelines/phase1.py` | Raw data, Cleaned data, Chroma Index, Evaluator | Baseline metrics, Phase 1 Markdown report | Hoàn thành |
| Corruption & Repair Flow | `src/pipelines/corruption_flow.py` | Baseline data, Corrupted data, Raw lineage | Corrupted & Repaired metrics, 3-State comparison report | Hoàn thành |
| Entrypoint Scripts | `script/run_phase1.py`, `script/run_corruption_flow.py` | CLI execution | End-to-end execution across 3 states | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Debug & Safe Type Handling | Module `src/evaluation/metrics.py` (Vũ) | Sửa lỗi `TypeError` ép kiểu `str` cho `_token_f1` khi dữ liệu rỗng. |
| Metadata Extraction Safety | Module `src/retrieval/qa.py` (Tùng) | Thêm `metadata.get()` phòng ngừa `KeyError` khi tra cứu dữ liệu lỗi. |
| Chroma Re-initialization Fix | Module `src/retrieval/index.py` (Tùng) | Sửa lỗi `HNSW segment reader` khi rebuild collection trong cùng tiến trình. |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Xây dựng hệ thống cấu hình chuẩn | `src/core/config.py` | Load tự động cài đặt, đường dẫn và API Key | `load_settings()` |
| Tích hợp Baseline Pipeline | `src/pipelines/phase1.py` | Luồng 7 bước Baseline | `python script/run_phase1.py` |
| Tích hợp Corruption & Repair Flow | `src/pipelines/corruption_flow.py` | Luồng 10 bước Pha 2 | `python script/run_corruption_flow.py` |
| Tạo Báo cáo so sánh 3 trạng thái | `data/reports/corruption_report.md` | Bảng đối chiếu 3 trạng thái | File Markdown sinh tự động |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Với vai trò Lead Integrator, tôi chịu trách nhiệm kết nối các thành phần riêng lẻ do 3 thành viên khác phát triển (Ingestion, Retrieval, Evaluation, Observability) thành một **Pipeline chạy end-to-end hoàn chỉnh**, đảm bảo tính tái lập (reproducibility), cách ly 3 môi trường (Baseline, Corrupted, Repaired) và không làm hỏng dữ liệu gốc.

### Cách triển khai
1. **Hệ thống Cấu hình Cặp đường dẫn (`src/core/config.py`)**: Thiết lập toàn bộ đường dẫn lưu trữ (`data/raw`, `data/clean`, `data/chroma`, `data/eval`, `data/reports`) độc lập theo vị trí tương đối của dự án `Path(__file__)`.
2. **Orchestration Pha 1 (`src/pipelines/phase1.py`)**: Nối 7 bước từ Fetch Raw $\rightarrow$ Clean $\rightarrow$ Index $\rightarrow$ Test Set $\rightarrow$ Evaluation $\rightarrow$ Quality/Freshness $\rightarrow$ Report.
3. **Orchestration Pha 2 (`src/pipelines/corruption_flow.py`)**: Nối 10 bước mô phỏng lỗi dữ liệu, rebuild index riêng (`papers-corrupted`), đánh giá suy giảm, tự động khôi phục từ `raw_records.json`, rebuild index (`papers-repaired`), đánh giá lại và xuất báo cáo đối chiếu 3 trạng thái.

### Input, output và contract

| Thành phần | Mô tả |
| ------------------------------ | ------------------------------------------- |
| Input | `data/raw/crossref_records.json`, `data/clean/papers_clean.csv`, `data/eval/test_set.json` |
| Output | `data/reports/phase1_report.md`, `data/reports/corruption_report.md`, metrics JSON files |
| Module phụ thuộc | `ingestion.cleaning`, `retrieval.index`, `evaluation.metrics`, `observability.reporting` |
| Module sử dụng output | CLI script `script/run_phase1.py` & `script/run_corruption_flow.py` |
| Điều kiện lỗi cần xử lý | Trường hợp dữ liệu rỗng (blank summary), rỗng metadata, lỗi HNSW reader của ChromaDB |

### Cách xác minh

```bash
.\.venv\Scripts\python.exe script/run_phase1.py
.\.venv\Scripts\python.exe script/run_corruption_flow.py
```

- **Kết quả mong đợi:** Cả 2 script chạy thành công từ đầu đến cuối không văng lỗi, xuất báo cáo Markdown tại `data/reports/`.
- **Kết quả thực tế:** Script đã chạy thành công 100%, sinh ra file `phase1_report.md` và `corruption_report.md` với đầy đủ con số thực nghiệm.
- **Artifact/log:** `data/reports/corruption_report.md`, `data/results/baseline_metrics.json`.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Khi đánh giá 3 trạng thái dữ liệu (Baseline, Corrupted, Repaired), cần lưu trữ Vector Index để truy vấn.
- **Các phương án đã cân nhắc:** 
  1. *Phương án A:* Ghi đè vào duy nhất 1 Collection Chroma (`papers-baseline`).
  2. *Phương án B:* Cách ly thành 3 Collection Chroma riêng biệt (`papers-baseline`, `papers-corrupted`, `papers-repaired`).
- **Phương án đã chọn:** Phương án B — Cách ly tuyệt đối 3 Collection và 3 bộ file embedding JSON.
- **Lý do:** Phương án B đảm bảo nguyên tắc bảo toàn dữ liệu chuẩn (DoD), giúp so sánh khách quan và tránh tình trạng dữ liệu lỗi ghi đè gây sai lệch mốc Baseline.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** `TypeError: expected string or bytes-like object, got 'float'` xảy ra trong hàm `_token_f1` khi chạy đánh giá dữ liệu rỗng.
- **Lệnh hoặc bước tái hiện:** `python script/run_phase1.py`
- **Nguyên nhân gốc:** Một số trường dữ liệu trong DataFrame bị NaN được pandas đọc dưới dạng kiểu `float`. Khi truyền biến `float` vào hàm `normalize_whitespace` vốn sử dụng `re.sub()`, Python ném lỗi `TypeError`.
- **Cách xử lý:** Cập nhật hàm `normalize_whitespace` trong `src/core/utils.py` và `_token_f1` trong `src/evaluation/metrics.py` tự động kiểm tra và chuyển tất cả biến `None` hoặc `float` NaN thành chuỗi rỗng `""`.
- **Cách xác minh sau khi sửa:** Chạy lại `script/run_phase1.py`, pipeline chạy thông suốt $100\%$ không bị ngắt quãng.
- **Điều học được:** Khi xây dựng data pipeline xử lý dữ liệu thực tế (Real-world data), luôn phải bọc ép kiểu an toàn (Defensive programming) cho mọi dữ liệu đầu vào.

---

## 7. Hiểu biết về luồng end-to-end

1. **Luồng dữ liệu:** Dữ liệu thô từ Crossref API được fetch và lưu dạng JSON nguyên bản (`raw_records.json`) $\rightarrow$ qua `cleaning.py` được chuẩn hóa tiêu đề, ngày tháng, tính toán `age_days` và tạo cột hợp nhất `text_for_embedding` $\rightarrow$ đưa qua `MiniLMEmbeddings` biến đổi thành vector 384 chiều và lưu vào DB Chroma (`papers-baseline`).
2. **Evaluation Set & Ground Truth:** Bộ đề thi `test_set.json` chứa 40 câu hỏi được tạo cố định từ cleaned dataset. Trường `ground_truth_doc_ids` chứa ID bài báo chính xác dùng để đo tỷ lệ tìm thấy (`retrieval_hit_rate`).
3. **Quality checks vs Freshness monitoring:** Quality checks kiểm tra tính toàn vẹn kỹ thuật của dữ liệu (null values, trùng lặp ID, độ dài chuỗi), còn Freshness monitoring kiểm tra tính mới của tri thức (tuổi bài báo `age_days` có vượt ngưỡng 180 ngày không).
4. **Tại sao dùng chung 1 test set:** Việc dùng cố định một test set cho cả 3 trạng thái đảm bảo tính khách quan và khoa học (A/B testing), giúp đo đạc chính xác mức độ suy giảm khi dữ liệu bị lỗi và mức độ phục hồi sau khi sửa.
5. **Đánh giá Repair thành công:** Repair được xem là thành công khi `Data Quality` quay về `PASS`, `Freshness` quay về `FRESH`, và `Retrieval Hit Rate` phục hồi từ `70.00%` trở lại `100.00%`.

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` | 100.00% | 70.00% | 100.00% | Dữ liệu lỗi làm mất bài báo khiến Hit Rate giảm 30%, khi repair dữ liệu phục hồi hoàn toàn 100%. |
| `mean_token_f1` | 75.00% | 57.85% | 75.00% | Lỗi làm rỗng summary khiến Token F1 giảm mạnh, khi khôi phục lại summary điểm F1 trở về mốc mốc chuẩn. |
| `LLM Judge Accuracy` | 100.00% | 57.50% | 72.50% | Điểm LLM Judge phản ánh trực tiếp chất lượng thông tin cung cấp cho mô hình. |
| Quality checks | PASS | FAIL | PASS | Quality checks phát hiện chính xác các lỗi blank summary, duplicate ID và title bị cắt xén. |
| Freshness status | FRESH | STALE | FRESH | Freshness phát hiện lỗi giả lập làm cũ ngày xuất bản về năm 2015. |

### Kết luận từ số liệu

1. **Chuỗi nguyên nhân 1:** [Làm rỗng summary & gán ngày cũ] $\rightarrow$ [Quality báo FAIL, Freshness báo STALE] $\rightarrow$ [Hit Rate giảm xuống 70%, LLM Judge Score giảm xuống 3.45].
2. **Chuỗi nguyên nhân 2:** [Khôi phục dữ liệu từ Raw Lineage] $\rightarrow$ [Quality quay về PASS, Freshness quay về FRESH] $\rightarrow$ [Hit Rate phục hồi 100%, F1 phục hồi 75%].

* **Corruption ảnh hưởng rõ nhất:** Hành vi làm rỗng `summary` và xóa các bản ghi mới nhất làm giảm chất lượng RAG nghiêm trọng nhất vì làm mất hẳn ngữ cảnh mà LLM cần để trả lời.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. **Thiết kế Data Pipeline:** Cần phân chia module rõ ràng, quản lý cấu hình bằng đối tượng Settings tập trung và luôn duy trì luồng dữ liệu nguyên vẹn (Lineage).
2. **Data Observability:** Kiểm thử dữ liệu (Data Quality Gates & Freshness Monitoring) là tuyến phòng thủ bắt buộc để phát hiện sớm lỗi dữ liệu trước khi đưa vào RAG Agent.
3. **Tác động của Data Quality đến RAG:** Chất lượng câu trả lời của LLM phụ thuộc trực tiếp vào tính chính xác và đầy đủ của dữ liệu đầu vào ("Garbage in, garbage out").

### Nếu có thêm thời gian
Tôi sẽ cài đặt thêm công cụ **Ragas Evaluation** chi tiết (Faithfulness, Answer Relevance, Context Precision) và phát triển giao diện Dashboard Streamlit trực quan để theo dõi Data Observability theo thời gian thực.

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
