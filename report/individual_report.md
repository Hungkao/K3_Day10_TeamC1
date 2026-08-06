# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Thành viên Nhóm C1 |
| MSSV | Lab AITC Team C1 |
| Khóa/Lớp | K3 / K4 |
| Tên nhóm | Team C1 |
| Vai trò chính | Data Foundation & Recovery Owner (`ingestion`, `cleaning`, `corruption`, `repair`) |
| Repository | `Hungkao/K3_Day10_TeamC1` |
| Ngày cập nhật | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| **Ingestion Raw** | `src/ingestion/crossref.py`<br>- `parse_crossref_payload`<br>- `fetch_source_records`<br>- `load_raw_records` | Crossref REST API & `Settings` | - `data/raw/crossref_response.json` (238 KB)<br>- `data/raw/crossref_records.json` (57 KB) | **Hoàn thành (CP0)** |
| **Data Cleaning** | `src/ingestion/cleaning.py`<br>- `build_clean_dataframe` | `list[PaperRecord]`, `run_date` | - `data/clean/papers_clean.csv` (100 KB)<br>- `data/clean/papers_clean.json` (108 KB) | **Hoàn thành (CP1)** |
| **Data Lineage & Traceability** | Inspection & Index verification | `papers_clean.csv` | - Chroma Collection `papers-baseline` (24 docs)<br>- Traceability report | **Hoàn thành (CP2)** |
| **Data Corruption & Repair** | `src/ingestion/corruption.py` | `papers_clean.csv` | - Corrupted clean dataframe<br>- Repaired dataset từ raw source | **Sẵn sàng (CP5 - CP6)** |

---

## 3. Nhật ký tiến độ theo từng Checkpoint

### CHECKPOINT 0: Khởi động, Contract & Ingestion Raw (00:00 – 00:30)
- **Công việc đã làm**:
  1. Đọc và phân tích Crossref REST API payload structure (`payload["message"]["items"]`).
  2. Xác định `DOI` (`item["DOI"]`) làm stable `paper_id` duy nhất xuyên suốt pipeline.
  3. Hoàn thiện `parse_crossref_payload` loại bỏ XML/JATS HTML tags trong tiêu đề/tóm tắt, bóc tách `authors`, `categories` và parse ngày xuất bản dạng ISO (`YYYY-MM-DD`).
  4. Hoàn thiện `fetch_source_records` với HTTP User-Agent và cơ chế **Retry & Exponential Backoff** (xử lý lỗi 429, 500, 502, 503, 504).
  5. Đã lưu raw response nguyên bản tại `data/raw/crossref_response.json` và raw records đã parse tại `data/raw/crossref_records.json`.
- **Bằng chứng xác minh**:
  - Tải thành công **24 bài báo** từ Crossref API.
  - Lệnh kiểm tra: `load_raw_records(settings.paths.raw_records_json)` trả về đúng 24 đối tượng `PaperRecord`.

### CHECKPOINT 1: Cleaning, Data Model & Quality Gates (00:30 – 01:05)
- **Công việc đã làm**:
  1. Thống nhất Clean Schema gồm 16 trường dữ liệu chuẩn.
  2. Hoàn thiện `build_clean_dataframe(records, run_date)` trong `src/ingestion/cleaning.py`.
  3. Chuẩn hóa chuỗi văn bản, loại bỏ các ký tự thừa và tạo các trường phụ trợ: `authors_joined`, `categories_joined`, `summary_chars`.
  4. Chuyển đổi ngày xuất bản `published` và tính toán `age_days = (run_date - published_date).days`.
  5. Xây dựng trường nội dung giàu ngữ cảnh `text_for_embedding` kết hợp Title, Authors, Categories, Published date và Summary.
  6. Áp dụng rule lọc dữ liệu rỗng và deduplication theo `paper_id` duy nhất.
- **Bằng chứng xác minh**:
  - Xuất file sạch: `data/clean/papers_clean.csv` và `data/clean/papers_clean.json`.
  - Kết quả: **24 bản ghi sạch**, **0 bản ghi trùng paper_id**, **0 bản ghi bị rỗng embedding text**.

### CHECKPOINT 2: Test set, RAG Index & Agent Smoke Test (01:05 – 01:35)
- **Công việc đã làm**:
  1. Kiểm tra tính truy vết (Traceability) của 1 `paper_id` đại diện (`10.2118/234689-pa`) xuyên suốt:
     - `crossref_response.json` $\rightarrow$ `crossref_records.json` $\rightarrow$ `papers_clean.csv` $\rightarrow$ `ChromaDB metadata`.
  2. Xác minh dữ liệu đầu vào sạch 100%, sẵn sàng bàn giao cho RAG Index & Evaluator.
  3. Phối hợp với RAG owner xây dựng Chroma vector collection `papers-baseline` bằng model `sentence-transformers/all-MiniLM-L6-v2`.
  4. Thực hiện `lookup(paper_id)` và `search()` thành công trên vector store.
- **Bằng chứng xác minh**:
  - Build thành công collection `papers-baseline` chứa **24 vector documents**.
  - `index.lookup("10.2118/234689-pa")` trả về đúng bài báo SafeRAG.

---

### Kế hoạch hành động các Checkpoint tiếp theo

```
           ┌─────────────────────────────────────────┐
           │ CP3: Baseline End-to-End Pipeline       │
           │ - Khóa baseline artifacts & metrics     │
           └────────────────────┬────────────────────┘
                                │
           ┌────────────────────▼────────────────────┐
           │ CP4: Break & Scenario Planning          │
           │ - Xác định kịch bản corrupt dữ liệu     │
           └────────────────────┬────────────────────┘
                                │
           ┌────────────────────▼────────────────────┐
           │ CP5: Data Corruption & Measurement      │
           │ - Implement corrupt_clean_dataframe     │
           │ - Tạo papers_clean_corrupted.csv        │
           │ - Đo mức sụt giảm hit rate & F1 score   │
           └────────────────────┬────────────────────┘
                                │
           ┌────────────────────▼────────────────────┐
           │ CP6: Data Repair & Comparison Report    │
           │ - Re-clean từ raw snapshot nguồn gốc   │
           │ - Tạo papers_clean_repaired.csv         │
           │ - Đo mức phục hồi metrics & xuất report │
           └─────────────────────────────────────────┘
```

#### CHECKPOINT 3: Baseline End-to-End & Báo cáo (01:35 – 02:00)
- **Mục tiêu**: Đảm bảo pipeline baseline chạy thông suốt từ ingestion $\rightarrow$ clean $\rightarrow$ index $\rightarrow$ evaluate $\rightarrow$ quality/freshness report.
- **Phần việc cá nhân**: Đảm bảo raw và clean artifacts giữ nguyên tính toàn vẹn, không fetch lại API làm thay đổi kết quả baseline.

#### CHECKPOINT 4: Nghỉ & Chuẩn bị Corruption Scenario (02:00 – 02:15)
- **Mục tiêu**: Chọn kịch bản corrupt sạch dữ liệu có chủ đích (ví dụ: làm rỗng summary một số bài, làm sai lệch ngày published, thêm noise vào tiêu đề).

#### CHECKPOINT 5: Corruption có kiểm soát & Đo Impact (02:15 – 03:15)
- **Mục tiêu**: Implement `corrupt_clean_dataframe` trong `src/ingestion/corruption.py`.
- **Output cần bàn giao**: `data/clean/papers_clean_corrupted.csv`, `data/clean/papers_clean_corrupted.json`, và file log `corruption_log.json`.

#### CHECKPOINT 6: Repair từ Raw, Comparison & Final Demo (03:15 – 04:00)
- **Mục tiêu**: Khôi phục dữ liệu sạch từ raw snapshot ban đầu (không sửa tay CSV corrupted), xuất `data/clean/papers_clean_repaired.csv` và hỗ trợ tổng hợp báo cáo so sánh 3 trạng thái.

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Crossref API trả về dữ liệu thô dạng JSON hỗn hợp chứa nhiều thẻ định dạng JATS XML (`<jats:p>`, `<jats:title>`), ngày tháng nhiều kiểu cấu trúc (`date-parts`, ISO datetime string), tên tác giả tách rời (`given`, `family`) và các URL truy cập khác nhau. Module ingestion và cleaning cần chuyển đổi dữ liệu thô này thành schema bảng chuẩn hóa, loại bỏ nhiễu và định dạng chuỗi ngữ cảnh chất lượng cho model embedding.

### Cách triển khai kỹ thuật
1. **DOI làm Stable ID**: Sử dụng `item["DOI"]` làm khóa chính `paper_id`. DOI là mã định danh quốc tế chuẩn, duy nhất và bền vững.
2. **Text Normalization**: Sử dụng Regular Expression `re.sub(r"<[^>]+>", " ", text)` để xóa bỏ toàn bộ thẻ XML/HTML, sau đó chuẩn hóa khoảng trắng thừa.
3. **Tính Age Days**: 
   ```python
   pub_dt = datetime.fromisoformat(str(published_str).split("T")[0])
   age_days = (run_date.replace(tzinfo=None) - pub_dt).days
   ```
4. **Rich Context Field (`text_for_embedding`)**: Ghép nối tiêu đề, danh sách tác giả, danh mục, ngày xuất bản và tóm tắt thành một khối văn bản duy nhất để hỗ trợ mô hình embedding biểu diễn đầy đủ thông tin ngữ nghĩa.

### Input, Output và Contract

| Thành phần | Mô tả |
| --- | --- |
| **Input** | Payload JSON từ `https://api.crossref.org/works` |
| **Output Raw** | `data/raw/crossref_response.json` và `data/raw/crossref_records.json` |
| **Output Clean** | `data/clean/papers_clean.csv` và `data/clean/papers_clean.json` (DataFrame 24 rows x 16 cols) |
| **Module phụ thuộc** | `src/core/config.py` (`Settings`, `Paths`) |
| **Module sử dụng Output** | `src/retrieval/index.py` (`LocalEmbeddingIndex`), `src/evaluation/testset.py` |

---

## 5. Quyết định kỹ thuật quan trọng

- **Bối cảnh**: Chọn cách lưu trữ dữ liệu raw thu thập được từ external API.
- **Các phương án cân nhắc**:
  1. *Phương án A*: Chỉ parse trực tiếp API response trong bộ nhớ RAM và ghi ngay ra file clean.
  2. *Phương án B*: Lưu raw API response nguyên bản ra đĩa (`crossref_response.json`), sau đó parse ra file `crossref_records.json` trước khi làm sạch.
- **Phương án chọn**: **Phương án B**.
- **Lý do**:
  - Giúp phục vụ tính năng **Data Lineage & Audit**: khi có sự cố dữ liệu hoặc câu trả lời sai từ RAG, có thể truy vết lại API gốc để biết dữ liệu sai do nguồn hay do quá trình làm sạch.
  - Phục vụ quá trình **Repair ở Phase 2**: khi dữ liệu bị corrupt ở bước clean, pipeline có thể tái tạo (repair) lại hoàn toàn từ snapshot raw mà không cần gọi lại external API.

---

## 6. Lỗi hoặc Blocker đã xử lý

- **Triệu chứng lỗi**: `requests.exceptions.HTTPError: 429 Client Error: Too Many Requests` hoặc gián đoạn khi kết nối Crossref API.
- **Nguyên nhân gốc**: Crossref REST API áp dụng rate limiting đối với các client gọi truy vấn mà không khai báo thông tin `User-Agent` hợp lệ hoặc tần suất quá dồn dập.
- **Cách xử lý**:
  - Thêm `User-Agent` chuẩn vào HTTP Headers.
  - Thêm cơ chế retry 3 lần với khoảng hoãn tăng mũ:
    ```python
    for attempt in range(max_retries):
        response = requests.get(url, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            break
        elif response.status_code in {429, 500, 502, 503, 504}:
            time.sleep(retry_delay * (2 ** attempt))
    ```
- **Xác minh**: Chạy thử nghiệm ingestion 100% thành công, không còn gặp sự cố rate limit.

---

## 7. Bảng theo dõi Metrics (Cho CP3, CP5, CP6)

| Metric / Signal | Baseline (CP3) | Corrupted (CP5) | Repaired (CP6) | Nhận xét của cá nhân |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | *[Đang chờ CP3]* | *[Đang chờ CP5]* | *[Đang chờ CP6]* | Đánh giá khả năng tìm đúng tài liệu |
| `mean_token_f1` | *[Đang chờ CP3]* | *[Đang chờ CP5]* | *[Đang chờ CP6]* | Đánh giá độ trùng khớp câu trả lời |
| `judge_accuracy` | *[Đang chờ CP3]* | *[Đang chờ CP5]* | *[Đang chờ CP6]* | Đánh giá từ LLM Judge |
| `mean_judge_score` | *[Đang chờ CP3]* | *[Đang chờ CP5]* | *[Đang chờ CP6]* | Điểm trung bình judge |
| Data Quality Checks | **Pass (100%)** | *[Đang chờ CP5]* | *[Đang chờ CP6]* | Khởi đầu 24/24 rows valid |
| Freshness Status | **Fresh** | *[Đang chờ CP5]* | *[Đang chờ CP6]* | Dữ liệu cập nhật gần đây |

---

## 8. Cam kết cá nhân

- [x] Nội dung báo cáo phản ánh đúng 100% công việc thực tế đã thực hiện tại CP0, CP1, CP2.
- [x] Đã kiểm tra các artifact dữ liệu thật tại `data/raw/` và `data/clean/`.
- [x] Không lưu secret, API key hoặc thông tin nhạy cảm vào repository.
- [x] Sẵn sàng phối hợp thực hiện các Checkpoint CP3, CP4, CP5, CP6 tiếp theo.

**Người báo cáo:** Thành viên Team C1 (Data Ingestion & Cleaning Owner)  
**Ngày xác nhận:** 2026-08-06
