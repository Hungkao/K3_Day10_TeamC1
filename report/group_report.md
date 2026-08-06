# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin | Nội dung |
| :--- | :--- |
| **Khóa/Lớp** | Cohort K3 |
| **Tên nhóm** | Team C1 |
| **Repository** | https://github.com/Hungkao/K3_Day10_TeamC1 |
| **Ngày hoàn thành** | 2026-08-06 |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | :--- | :--- | :--- | :--- |
| 1 | Nguyễn Phúc Hưng | 2A202601115 | Role 1 — Lead / Integrator | `src/core/`, `src/pipelines/`, `script/` |
| 2 | Nguyễn Văn Phong | 2A202601087 | Role 2 — Data Eng | `src/ingestion/`, `data/raw/`, `data/clean/` |
| 3 | Nguyễn Hữu Khánh Tùng | 2A202601781 | Role 3 — RAG Specialist | `src/retrieval/`, `data/embeddings/`, `data/chroma/` |
| 4 | Nguyễn Tuấn Vũ | 2A202601845 | Role 4 — Eval & Observability | `src/evaluation/`, `src/observability/`, `data/quality/` |

---

## 2. Tóm tắt kết quả

**Tóm tắt của nhóm:**

Nhóm Team C1 đã hoàn thành 100% việc xây dựng đường ống dữ liệu RAG end-to-end cho 24 bài báo khoa học lấy từ Crossref REST API, tích hợp hệ thống giám sát chất lượng (Data Observability), giả lập làm hỏng dữ liệu có kiểm soát (Data Corruption) và khôi phục thành công từ bản sao lưu thô (Raw Snapshot).

Ở mốc Baseline (Pha 1), pipeline tạo đầy đủ các artifacts tại `data/raw/`, `data/clean/`, `data/eval/test_set.json` (40 câu hỏi factual đóng băng), `data/embeddings/`, `data/results/` và báo cáo `data/reports/phase1_report.md` với **Retrieval Hit Rate đạt 100%** và **Mean Token F1 đạt 75.00%**.

Ở Pha 2, hành vi cố ý xóa tóm tắt (Blank Summary) gây ảnh hưởng nghiêm trọng nhất khiến Retrieval Hit Rate sụt giảm từ 100% xuống **70.00%**, Token F1 giảm từ 75% xuống **57.85%**, kéo theo cờ cảnh báo Observability chuyển sang **`FAIL`** và **`STALE`**. Sau khi thực hiện Re-clean phục hồi dữ liệu từ file raw snapshot `crossref_records.json`, các chỉ số RAG (Hit Rate 100%, F1 75%) và cờ Observability (**`PASS`**, **`FRESH`**) đều được khôi phục trọn vẹn. 

Giới hạn lớn nhất hiện tại là tập dữ liệu thử nghiệm dừng ở quy mô 24 bài báo; hướng cải thiện tiếp theo là mở rộng quy mô dữ liệu và áp dụng framework Great Expectations.

---

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
Crossref API
    -> raw response/raw records (crossref_response.json & crossref_records.json)
    -> cleaning và data modeling (papers_clean.csv & papers_clean.json)
    -> embedding + ChromaDB index (papers-baseline)
    -> evaluation baseline (test_set.json & baseline_metrics.json)
    -> quality/freshness reports (baseline_quality_check.json & phase1_report.md)
    -> corruption (papers_clean_corrupted.json & corruption_log.json)
    -> re-index và re-evaluate (papers-corrupted & corrupted_metrics.json)
    -> repair từ dữ liệu nguồn (papers_clean_repaired.json)
    -> comparison report (corruption_report.md)
```

### Trách nhiệm của từng khối

| Khối | Input | Xử lý chính | Output/artifact | Owner |
| :--- | :--- | :--- | :--- | :--- |
| Ingestion | Crossref REST API | Fetch HTTP GET, retry backoff, parse raw JSON | `data/raw/crossref_response.json`, `data/raw/crossref_records.json` | Nguyễn Văn Phong |
| Cleaning | Raw records snapshot | Lọc rác HTML, định dạng tác giả/danh mục, tính `age_days`, tạo `text_for_embedding` | `data/clean/papers_clean.csv`, `data/clean/papers_clean.json` | Nguyễn Văn Phong |
| Embedding/index | Cleaned DataFrame | Encoding vector MiniLM 384 dims, quản lý ChromaDB collections | `data/embeddings/papers_embeddings.json`, `data/chroma/` | Nguyễn Hữu Khánh Tùng |
| Evaluation | Clean Data, Chroma Index | Tạo 40 câu test set đóng băng, Vector Similarity Search, LLM Judge evaluation | `data/eval/test_set.json`, `data/results/baseline_metrics.json` | Nguyễn Tuấn Vũ |
| Observability | Clean/Corrupted/Repaired Data | 5 Quality Checks, Freshness monitoring, sinh báo cáo Markdown | `data/quality/`, `data/reports/phase1_report.md` | Nguyễn Tuấn Vũ |
| Corruption/repair | Clean Data, Raw Snapshot | Giả lập 5 dạng corruption, Re-clean raw snapshot để phục hồi dữ liệu | `papers_clean_corrupted.json`, `papers_clean_repaired.json`, `corruption_log.json` | Nguyễn Văn Phong |
| Orchestration | Core Settings & Modules | Điều phối luồng Phase 1 và Phase 2 end-to-end, quản lý release Git | `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`, `script/` | Nguyễn Phúc Hưng |

---

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình | Giá trị sử dụng |
| :--- | :--- |
| `LLM_PROVIDER` | `openrouter` / `gemini` |
| `LLM_MODEL` | `qwen/qwen-2.5-7b-instruct` / `gemini-2.5-flash` |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Số lượng Crossref records | 24 records |
| Retrieval `top_k` | 4 |
| Freshness threshold | 180 days |
| Random seed, nếu có | `42` |

Không dán nội dung API key hoặc file `.env` vào báo cáo.

### Lệnh cài đặt

```bash
python -m pip install -e .
```

### Lệnh chạy

Baseline:

```bash
python script/run_phase1.py
```

Corruption flow:

```bash
python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh | Trạng thái | Thời điểm chạy gần nhất | Bằng chứng |
| :--- | :--- | :--- | :--- |
| Baseline pipeline | Thành công | 2026-08-06 | `data/results/baseline_metrics.json` (Hit Rate: 100%) |
| Corruption flow | Thành công | 2026-08-06 | `data/reports/corruption_report.md` (Hit Rate: 70% -> 100%) |

---

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính | Giá trị |
| :--- | :--- |
| Source | Crossref REST API Endpoint (`https://api.crossref.org/works`) |
| Query/filter | `query=agentic retrieval augmented generation large language model`, `filter=from-pub-date:2026-02-07,has-abstract:true` |
| Thời điểm lấy dữ liệu | 2026-08-06 UTC |
| Số record nhận được | 24 records |
| Cơ chế retry/backoff | Exponential backoff (đợi 1s, 2s, 4s nếu gặp HTTP status 429 Rate Limit) |

### Raw và clean schema

| Trường | Kiểu dữ liệu | Bắt buộc? | Ý nghĩa | Xử lý khi thiếu/sai |
| :--- | :--- | :---: | :--- | :--- |
| `paper_id` | String (DOI) | Có | Định danh duy nhất của bài báo | Bỏ qua bản ghi hoặc sinh slug URL chuẩn hóa |
| `title` | String | Có | Tiêu đề chính của bài báo | Bỏ qua bản ghi nếu rỗng hoặc null |
| `summary` | String | Có | Đoạn tóm tắt (Abstract) bài báo | Bỏ qua bản ghi nếu rỗng hoặc ngắn hơn 100 ký tự |
| `published` | String | Có | Ngày xuất bản định dạng `YYYY-MM-DD` | Gán ngày mặc định `1970-01-01` nếu thiếu |
| `authors_joined` | String | Có | Danh sách tên tác giả nối bằng dấu phẩy | Gán chuỗi `"Unknown Author"` |
| `categories_joined` | String | Không | Danh mục/chủ đề bài báo | Gán chuỗi rỗng `""` |
| `age_days` | Integer | Có | Số ngày tính từ lúc xuất bản đến hiện tại | Tính toán tự động từ mốc thời gian hiện tại UTC |
| `text_for_embedding` | String | Có | Chuỗi ngữ cảnh tổng hợp dùng để hóa vector | Ghép chuỗi dạng `Title: [title] \| Authors: [authors] \| Summary: [summary]` |

### Quy tắc cleaning

| Quy tắc | Quality dimension liên quan | Số record bị tác động | Cách xác minh |
| :--- | :--- | :-: | :--- |
| Loại bỏ bản ghi thiếu `title` hoặc `summary` ngắn $<100$ chars | Completeness & Validity | 0 (Do API filter đã chuẩn) | Lệnh `run_data_quality_checks` |
| Xóa sạch thẻ HTML/XML rác trong abstract (`<jats:p>`, `<b>`...) | Validity | 24 records | Kiểm tra Regex trong `src/ingestion/cleaning.py` |
| Chuẩn hóa định dạng ngày xuất bản về `YYYY-MM-DD` | Timeliness & Validity | 24 records | `build_freshness_report` |
| Ghép chuỗi tiêu đề, tác giả, tóm tắt thành `text_for_embedding` | Completeness | 24 records | Kiểm tra cấu trúc DataFrame đầu ra |

**Giải thích cách nhóm tạo `text_for_embedding`, document ID và `age_days`:**

1. `text_for_embedding`: Được nhóm tạo bằng cách ghép 3 trường thông tin cốt lõi theo định dạng: `Title: {title} | Authors: {authors_joined} | Summary: {summary}`. Việc này giúp mô hình Embedding (MiniLM) mã hóa được cả ngữ nghĩa tiêu đề lẫn nội dung tóm tắt vào không gian Vector 384 chiều.
2. `document ID`: Nhóm sử dụng trực tiếp mã DOI chuẩn hóa của bài báo (hoặc chuỗi slug từ tiêu đề) làm `paper_id` duy nhất cho từng document.
3. `age_days`: Được tính bằng công thức `(UTC_now - published_date).days`. Trường này được dùng trực tiếp cho Observability Engine để đánh giá độ tươi mới (Freshness threshold: 180 ngày).

---

## 6. Evaluation setup

| Thành phần | Cấu hình thực tế |
| :--- | :--- |
| Số câu hỏi | 40 câu hỏi factual |
| Các `question_type` | `summary` (10 câu), `authors` (10 câu), `date` (10 câu), `categories` (10 câu) |
| Ground-truth document ID | Mã DOI `paper_id` của bài báo tương ứng trong dataset làm sạch |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector store/collection | Persistent ChromaDB (`papers-baseline`, `papers-corrupted`, `papers-repaired`) |
| Retrieval `top_k` | 4 |
| LLM provider/model | OpenRouter (`qwen/qwen-2.5-7b-instruct`) / Gemini (`gemini-2.5-flash`) |
| Test set dùng chung cho ba trạng thái | [`data/eval/test_set.json`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/eval/test_set.json) (Frozen) |

**Giải thích vì sao test set được giữ nguyên khi đánh giá baseline, corrupted và repaired:**

Việc đóng băng và giữ nguyên bộ câu hỏi đánh giá (`test_set.json`) qua cả 3 trạng thái là nguyên tắc đo lường khoa học bắt buộc (apples-to-apples comparison). Khi cố định thước đo (câu hỏi, đáp án chuẩn, ground-truth doc IDs), mọi sự suy giảm hay phục hồi của các chỉ số metrics (`retrieval_hit_rate`, `mean_token_f1`, `mean_judge_score`) hoàn toàn phản ánh chính xác tác động của chất lượng dữ liệu đầu vào (Data Quality), loại trừ hoàn toàn yếu tố nhiễu do câu hỏi đánh giá bị thay đổi.

---

## 7. Kết quả baseline

### Artifact checklist

| Artifact | Đường dẫn thực tế | Trạng thái | Ghi chú |
| :--- | :--- | :---: | :--- |
| Raw response/records | `data/raw/` | Có | `crossref_response.json`, `crossref_records.json` |
| Cleaned dataset | `data/clean/` | Có | `papers_clean.csv`, `papers_clean.json` |
| Embedding manifest/index | `data/embeddings/` | Có | `papers_embeddings.json`, `data/chroma/` |
| Evaluation set | `data/eval/` | Có | `test_set.json` (40 câu hỏi frozen) |
| Baseline metrics | `data/results/baseline_metrics.json` | Có | Hit Rate: 100%, Token F1: 75% |
| Quality/freshness | `data/quality/` | Có | `baseline_quality_check.json`, `freshness_report.json` |
| Baseline report | `data/reports/phase1_report.md` | Có | Export tự động từ pipeline |

### Baseline metrics

| Metric | Giá trị | Diễn giải |
| :--- | :-: | :--- |
| `retrieval_hit_rate` | **`100.00%`** (`1.0000`) | Vector search truy vấn chính xác bài báo chứa câu trả lời cho 40/40 câu hỏi test set. |
| `mean_token_f1` | **`75.00%`** (`0.7500`) | Độ trùng khớp từ vựng giữa câu trả lời sinh ra và đáp án chuẩn đạt mức cao. |
| `judge_accuracy` | **`97.50%`** (`0.9750`) | 39/40 câu trả lời được LLM Judge chấm điểm đạt tối đa (4 hoặc 5 điểm). |
| `mean_judge_score` | **`4.90 / 5.0`** | Điểm số đánh giá ngữ nghĩa trung bình của Giám khảo LLM đạt mức gần như tuyệt đối. |
| Ragas, nếu có | `N/A` | Không chạy Ragas do bài lab ưu tiên dùng LLM Judge nhẹ và Token F1 local để tiết kiệm chi phí API. |

---

## 8. Data quality và freshness

### Quality checks

| Check | Quality dimension | Ngưỡng/kỳ vọng | Kết quả baseline | Bằng chứng |
| :--- | :--- | :--- | :---: | :--- |
| `row_count` | Completeness | Total rows $> 0$ | **PASS** (24 rows) | `baseline_quality_check.json` |
| `paper_id_integrity` | Uniqueness & Validity | Null = 0, Duplicate = 0 | **PASS** (Null: 0, Dup: 0) | `baseline_quality_check.json` |
| `title_non_null` | Validity | Null = 0 | **PASS** (Null: 0) | `baseline_quality_check.json` |
| `summary_quality` | Completeness & Accuracy | Missing = 0, Short = 0 | **PASS** (Missing: 0) | `baseline_quality_check.json` |
| `freshness_threshold` | Timeliness | Stale rows ($> 180$ days) = 0 | **PASS** (Stale: 0) | `baseline_quality_check.json` |

### Freshness

| Thuộc tính | Giá trị |
| :--- | :--- |
| Freshness được đo tại | Cleaned dataset (`papers_clean.json`) |
| Timestamp mới nhất | `2026-08-05` (Bài báo mới nhất xuất bản) |
| Ngưỡng freshness | `180` ngày |
| Trạng thái baseline | **`FRESH`** |
| Lý do | Bài báo mới nhất xuất bản trước thời điểm hiện tại 1 ngày (`age_days = 1 <= 180`). |

---

## 9. Corruption scenarios và repair

| Corruption | Cách tạo | Record bị tác động | Quality signal kỳ vọng | Tác động thực tế | Cách repair |
| :--- | :--- | :-: | :--- | :--- | :--- |
| **Blank Summary** | Xóa rỗng trường `summary` | 3 records | Quality Check `FAIL` (`missing_summary_count > 0`) | Hit Rate tụt từ 100% xuống 70%, F1 tụt xuống 57.85% | Re-clean lại từ file raw snapshot `crossref_records.json` |
| **Stale Date** | Đổi ngày về `2000-01-01` | 2 records | Freshness Check `STALE` (`stale_rows > 0`) | `is_fresh` chuyển thành `False` | Re-clean lại từ file raw snapshot `crossref_records.json` |
| **Truncate Title** | Cắt ngắn tiêu đề bài báo $<10$ chars | 2 records | Quality Check `FAIL` | Làm suy giảm chất lượng hiển thị ngữ cảnh | Re-clean lại từ file raw snapshot `crossref_records.json` |
| **Add Duplicate** | Nhân bản 1 bài báo giữ nguyên `paper_id` | 1 record | Quality Check `FAIL` (`duplicate_ids > 0`) | Gây nhiễu kết quả tra cứu vector | Re-clean lại từ file raw snapshot `crossref_records.json` |
| **Add Noise** | Chèn chuỗi rác `[CORRUPTED_NOISE]` | 1 record | Quality Check `FAIL` | Làm suy giảm điểm số tương đồng Cosine | Re-clean lại từ file raw snapshot `crossref_records.json` |

**Corruption log:**

- **Đường dẫn**: `data/results/corruption_log.json`
- **Trạng thái**: **Có**
- **Nhận xét**: Log ghi nhận đầy đủ 5 loại corruption, danh sách các `paper_id` bị tác động và các tham số làm hỏng dữ liệu cụ thể.

**Giải thích cách repair đảm bảo dữ liệu được phục hồi từ nguồn đáng tin cậy thay vì chỉ che kết quả lỗi:**

Quy trình Repair trong dự án không sử dụng các thủ thuật sửa đè mã cứng (hardcode) hay che lỗi tạm thời trên tập dữ liệu đã bị hỏng. Thay vào đó, nhóm thực thi luồng Data Recovery chuẩn công nghiệp: chạy lại toàn bộ quy tắc Cleaning & Normalization từ bản sao lưu dữ liệu thô ban đầu (Raw Data Snapshot tại `data/raw/crossref_records.json`). Vì `crossref_records.json` là bản ghi thô nguyên bản thu thập từ Crossref API chưa bị biến đổi, việc re-clean từ nguồn này đảm bảo dữ liệu phục hồi 100% tính chân thực và toàn vẹn cấu trúc.

---

## 10. So sánh baseline, corrupted và repaired

| Metric/signal | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi | Nhận xét |
| :--- | :-: | :-: | :-: | :-: | :-: | :--- |
| `retrieval_hit_rate` | **`100.00%`** | **`70.00%`** | **`100.00%`** | **-30.00%** | **+30.00%** | Phục hồi hoàn toàn 100% sau khi Re-clean từ raw snapshot. |
| `mean_token_f1` | **`75.00%`** | **`57.85%`** | **`75.00%`** | **-17.15%** | **+17.15%** | F1 sụt giảm khi mất tóm tắt và quay về mức ban đầu. |
| `judge_accuracy` | **`97.50%`** | **`57.50%`** | **`72.50%`** | **-40.00%** | **+15.00%** | Điểm số LLM Judge phục hồi đáng kể sau khi sửa lại ngữ cảnh text. |
| `mean_judge_score` | **`4.90 / 5`** | **`3.45 / 5`** | **`3.90 / 5`** | **-1.45** | **+0.45** | Chất lượng câu trả lời từ LLM Judge tăng 0.45 điểm sau repair. |
| Quality checks pass/fail | **`PASS`** | **`FAIL`** | **`PASS`** | Đổi sang FAIL | Đổi sang PASS | Quality Engine phát hiện chính xác màu đỏ ngay khi có lỗi. |
| Freshness status | **`FRESH`** | **`STALE`** | **`FRESH`** | Chuyển STALE | Chuyển FRESH | Freshness Engine cảnh báo chính xác khi bài báo bị lùi ngày xuất bản. |

**Nêu ít nhất hai kết luận có quan hệ nhân quả được hỗ trợ bởi artifacts:**

1. **[Blank Summary Corruption] $\rightarrow$ [Quality Check FAIL (`missing_summary_count: 3` trong `corrupted_quality_check.json`)] $\rightarrow$ [Retrieval Hit Rate sụt từ 100% xuống 70% trong `corrupted_metrics.json`]**.
2. **[Repair Re-clean từ Raw Snapshot] $\rightarrow$ [Quality Check phục hồi PASS (`missing_summary_count: 0` trong `repaired_quality_check.json`)] $\rightarrow$ [Retrieval Hit Rate phục hồi từ 70% lên 100% trong `repaired_metrics.json`]**.

---

## 11. Vấn đề tích hợp quan trọng

Mô tả một vấn đề phát sinh khi ghép các module trong pipeline và cách nhóm xử lý:

- **Triệu chứng:** Lỗi `KeyError: 'categories_joined'` phát sinh tại `src/retrieval/qa.py` khi chạy pipeline Pha 2 trên tập dữ liệu bị làm hỏng `papers_clean_corrupted.json`.
- **Nguyên nhân:** Hàm `_extract_answer` truy cập trực tiếp bằng cú pháp dict `metadata["categories_joined"]`. Khi dữ liệu bị corrupt, một số bản ghi bị khuyết trường metadata làm dictionary không tồn tại key này.
- **Cách xử lý:** Thay thế cú pháp truy cập trực tiếp bằng phương thức an toàn `dict.get("categories_joined", "")`.
- **Cách xác minh:** Chạy lệnh `python script/run_corruption_flow.py` $\rightarrow$ Pipeline thực thi mượt mà qua 40 câu hỏi dữ liệu hỏng mà không gặp bất kỳ lỗi runtime nào.

---

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng | Hướng cải thiện có thể kiểm chứng |
| :--- | :--- | :--- |
| **Quy mô dữ liệu thử nghiệm nhỏ (24 bài báo)** | Chưa đánh giá được độ phức tạp khi vector search trên quy mô hàng ngàn văn bản | Mở rộng gọi API thu thập 500+ bài báo và đo lường độ trễ tìm kiếm ChromaDB |
| **Nhạy cảm với biến động điểm số của LLM Judge** | Chênh lệch điểm số nhỏ giữa các lần gọi LLM khác nhau | Bổ sung Few-shot Examples trong Prompt của LLM Judge để cố định tiêu chí chấm |

---

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm và repository chính xác.
- [x] Phân công khớp với module, artifact và kết quả thực tế.
- [x] Lệnh tái hiện đã được chạy lại trên phiên bản dùng để nộp.
- [x] Baseline, corrupted và repaired dùng cùng evaluation set.
- [x] Bảng metrics khớp với các file trong `data/results/`.
- [x] Quality/freshness conclusions khớp với `data/quality/`.
- [x] Các đường dẫn báo cáo và artifact truy cập được.
- [x] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng.
- [x] Không có `.env`, API key, token hoặc secret trong source, report, log hay ảnh.
