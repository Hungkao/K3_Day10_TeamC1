# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Nguyễn Văn Phong |
| MSSV | 2A202601087 |
| Khóa/Lớp | K3 |
| Tên nhóm | Team C1 |
| Vai trò chính | Data Foundation & Recovery Owner (`ingestion`, `cleaning`, `corruption`, `repair`) |
| Repository | `Hungkao/K3_Day10_TeamC1` |
| Ngày cập nhật | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Data Ingestion | `src/ingestion/crossref.py` | API URL & params | `data/raw/crossref_response.json`, `data/raw/crossref_records.json` | Hoàn thành |
| Data Cleaning & Modeling | `src/ingestion/cleaning.py` | Parsed raw records | `data/clean/papers_clean.csv`, `data/clean/papers_clean.json` | Hoàn thành |
| Controlled Corruption | `src/ingestion/corruption.py` | Clean dataframe | `data/clean/papers_clean_corrupted.csv`, `data/clean/papers_clean_corrupted.json`, `data/results/corruption_log.json` | Hoàn thành |
| Data Repair & Re-clean | `src/ingestion/cleaning.py` | Saved raw records snapshot | `data/clean/papers_clean_repaired.csv`, `data/clean/papers_clean_repaired.json` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả và bằng chứng |
| --- | --- | --- |
| Tích hợp luồng pipeline | Integrator (`src/pipelines/`) | Thống nhất Data Contract đầu ra của Ingestion/Cleaning để luồng Phase 1 và Phase 2 chạy không lỗi |
| Chuẩn bị dữ liệu cho Index/RAG | RAG Owner & Observability Owner | Cung cấp đúng schema `text_for_embedding` và `age_days` cho ChromaDB & Quality Checks |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Crawl & Parse dữ liệu API thô | `src/ingestion/crossref.py` | Sinh 2 file snapshot dữ liệu thô tại `data/raw/` | `TestIngestion` trong `pytest` pass 100% |
| Làm sạch và chuẩn hóa schema | `src/ingestion/cleaning.py` | Sinh 24 bản ghi sạch tại `data/clean/papers_clean.json` | `TestCleaning` pass 100% |
| Giả lập làm hỏng dữ liệu có kiểm soát | `src/ingestion/corruption.py` | Tạo dataset hỏng `papers_clean_corrupted.json` & `corruption_log.json` | 5/5 loại corruption có trong log |
| Phục hồi dữ liệu từ raw snapshot | `src/ingestion/cleaning.py` | Re-clean lại 24 bản ghi chuẩn tại `data/clean/papers_clean_repaired.json` | Observability checks chuyển từ FAIL -> PASS |

**Artifact cụ thể đã tạo ra:**
- Log làm hỏng dữ liệu: `data/results/corruption_log.json` ghi lại chi tiết 5 dạng corruption tác động lên 9 bản ghi (gồm các bản ghi quan trọng phục vụ evaluation).

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Xây dựng lớp dữ liệu nền móng (Data Foundation): lấy dữ liệu thực tế từ Crossref API, làm sạch thành schema chuẩn cho RAG, giả lập các kịch bản hỏng dữ liệu thực tế để kiểm thử Observability, và thực thi cơ chế khôi phục dữ liệu tin cậy từ raw snapshot khi có sự cố.

### Cách triển khai
1. **Ingestion (`crossref.py`)**: Gửi request HTTP GET tới Crossref API (`https://api.crossref.org/works`), áp dụng cơ chế Retry với Exponential Backoff xử lý lỗi 429/503. Lưu response thô và parse thành danh sách phẳng `PaperRecord`.
2. **Cleaning (`cleaning.py`)**:
   - Loại bỏ bản ghi thiếu `title` hoặc có `summary` ngắn dưới 100 ký tự.
   - Loại bỏ thẻ HTML/XML rác trong tóm tắt bằng Regex.
   - Chuẩn hóa tác giả (`authors_joined`) và danh mục (`categories_joined`).
   - Tính toán độ tươi mới: ép kiểu ngày xuất bản `YYYY-MM-DD` và tính `age_days = (UTC_now - published_date).days`.
   - Tạo trường chuyên dụng cho vector search: `text_for_embedding = f"Title: {title} | Authors: {authors_joined} | Summary: {summary}"`.
3. **Corruption (`corruption.py`)**: Áp dụng 5 quy tắc cố ý làm xấu dữ liệu:
   - *Blank Summary*: Xóa sạch tóm tắt của 3 bản ghi.
   - *Stale Date*: Đổi ngày xuất bản về năm 2000 (`age_days > 180`).
   - *Truncate Title*: Cắt ngắn tiêu đề dưới 10 ký tự.
   - *Add Duplicate*: Nhân bản 1 bài báo giữ nguyên `paper_id`.
   - *Add Noise*: Chèn xâu rác `[CORRUPTED_NOISE]` vào text embedding.
4. **Repair (`cleaning.py`)**: Không sửa thủ công trên dataset lỗi mà chạy lại toàn bộ quy tắc cleaning trên file raw snapshot đã lưu `data/raw/crossref_records.json`.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | Crossref REST API response / `data/raw/crossref_records.json` |
| Output | `papers_clean.json`, `papers_clean_corrupted.json`, `papers_clean_repaired.json`, `corruption_log.json` |
| Module phụ thuộc | `src/core/config.py`, `src/core/utils.py` |
| Module sử dụng output | `src/retrieval/index.py`, `src/evaluation/testset.py`, `src/observability/quality.py` |
| Điều kiện lỗi cần xử lý | Mạng gián đoạn/API rate limit (retry), dữ liệu thiếu trường/sai định dạng ngày (fallback safe values) |

### Cách xác minh

```bash
pytest tests/test_ingestion.py tests/test_cleaning.py
```

- **Kết quả mong đợi:** Tất cả unit tests cho module ingestion và cleaning đều PASS.
- **Kết quả thực tế:** 6/6 tests PASS hoàn toàn.
- **Artifact/log:** `data/clean/papers_clean.json`, `data/results/corruption_log.json`.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn chiến lược lưu trữ dữ liệu thô (Raw Data Storage) sau khi fetch từ API.
- **Các phương án đã cân nhắc:**
  - *Phương án 1*: Chỉ lưu duy nhất file CSV/JSON đã qua làm sạch (`papers_clean.json`).
  - *Phương án 2*: Lưu cả response HTTP gốc (`crossref_response.json`) và danh sách bản ghi thô đã parse (`crossref_records.json`).
- **Phương án đã chọn:** Phương án 2 (Lưu vết 2 lớp dữ liệu thô tại `data/raw/`).
- **Lý do:** Đảm bảo tính **Data Reproducibility & Auditability**. Khi xảy ra sự cố dữ liệu (Corruption) hoặc khi cần thay đổi quy tắc ETL, hệ thống có thể khôi phục (Repair) lập tức từ `crossref_records.json` mà không tốn chi phí/thời gian gọi lại API bên thứ ba, tránh bị dính API Rate Limit (HTTP 429).
- **Bằng chứng quyết định phù hợp:** Luồng Data Repair ở Phase 2 tái tạo lại 100% dữ liệu sạch trong 0.2 giây từ file `crossref_records.json` mà không cần kết nối mạng.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```text
  ValueError: time data '2026' does not match format '%Y-%m-%d'
  ```
- **Lệnh hoặc bước tái hiện:** Chạy `build_clean_dataframe` với một số bản ghi Crossref API chỉ trả về năm xuất bản (`issued: {"date-parts": [[2026]]}`) thay vì đủ ngày tháng năm.
- **Nguyên nhân gốc:** Hàm parse ngày tháng giả định mọi bản ghi API đều có đủ 3 phần tử `[YYYY, MM, DD]`, khi gặp bài báo chỉ có năm xuất bản thì bị truy cập vượt chỉ số mảng (IndexError) hoặc lỗi format date.
- **Cách xử lý:** Bổ sung hàm Helper `_parse_published_date` xử lý linh hoạt:
  ```python
  def _parse_published_date(date_parts: list) -> str:
      if not date_parts or not date_parts[0]:
          return "1970-01-01"
      parts = date_parts[0]
      year = parts[0]
      month = parts[1] if len(parts) > 1 else 1
      day = parts[2] if len(parts) > 2 else 1
      return f"{year:04d}-{month:02d}-{day:02d}"
  ```
- **Cách xác minh sau khi sửa:** Chạy lại cleaning pipeline với 24 bản ghi thực tế $\rightarrow$ 100% ngày tháng được chuẩn hóa về định dạng `YYYY-MM-DD` không phát sinh ngoại lệ.
- **Điều học được:** Khâu Data Ingestion từ nguồn bên ngoài (3rd party API) phải luôn lường trước sự thiếu hụt định dạng của dữ liệu thực tế.

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   - API trả response $\rightarrow$ `crossref.py` parse & lưu snapshot `crossref_records.json` $\rightarrow$ `cleaning.py` lọc rác, chuẩn hóa text & tạo `text_for_embedding` $\rightarrow$ `index.py` hóa vector bằng MiniLM và lưu vào ChromaDB collection `papers-baseline`.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   - `test_set.json` lưu cặp câu hỏi - đáp án chuẩn kèm `ground_truth_doc_ids`. Khi RAG chạy, nó tìm top-k bài báo; nếu bài báo tìm được chứa `ground_truth_doc_id` thì tính là Hit (`retrieval_hit = True`). Đáp án sinh ra được chấm F1 từ vựng và điểm LLM Judge.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - Quality checks đo tính toàn vẹn cấu trúc (dữ liệu không rỗng, ID không trùng, title/summary chuẩn). Freshness monitoring đo tính cập nhật thời gian (`age_days` so với mốc hiện tại).
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   - Đảm bảo tính đo lường nhất quán (apples-to-apples). Giữ cố định thước đo thì sự sụt giảm hay phục hồi chỉ số mới phản ánh đúng tác động của chất lượng dữ liệu.
5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   - Thành công khi `papers_clean_repaired.json` sạch 100%, Quality checks quay lại `PASS`, Freshness quay lại `FRESH`, và `retrieval_hit_rate` trên test set phục hồi về mức Baseline (100%).

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 100.00% | 70.00% | 100.00% | Corruption xóa tóm tắt khiến retrieval sụt 30%; Repair khôi phục về 100% |
| `mean_token_f1` | 75.00% | 57.85% | 75.00% | F1 giảm mạnh do câu trả lời thiếu ngữ cảnh tóm tắt; Repair phục hồi trọn vẹn |
| `judge_accuracy` | 97.50% | 57.50% | 72.50% | Điểm đánh giá ngữ nghĩa bị ảnh hưởng nghiêm trọng khi dữ liệu bị nhiễu |
| `mean_judge_score` | 4.90 / 5 | 3.45 / 5 | 3.90 / 5 | Chất lượng câu trả lời tụt 1.45 điểm khi dữ liệu xấu và tăng lại sau repair |
| Quality checks | PASS | FAIL | PASS | Quality engine phát hiện đúng các lỗi rỗng summary, trùng ID |
| Freshness status | FRESH | STALE | FRESH | Freshness engine cảnh báo STALE chính xác khi ngày bị lùi về năm 2000 |

### Kết luận từ số liệu

1. **[Data corruption] -> [quality/freshness signal thay đổi] -> [agent metric thay đổi]**:
   - Khi chạy `corruption.py` làm rỗng summary 3 bài báo và lùi ngày 2 bài báo $\rightarrow$ Quality check chuyển `FAIL`, Freshness chuyển `STALE` $\rightarrow$ Retrieval Hit Rate lập tức sụt từ 100% xuống 70%, F1 tụt xuống 57.85%.
2. **[Repair action] -> [quality/freshness signal phục hồi] -> [agent metric phục hồi]**:
   - Khi thực hiện Re-clean từ snapshot dữ liệu thô `crossref_records.json` $\rightarrow$ Quality check phục hồi `PASS`, Freshness phục hồi `FRESH` $\rightarrow$ Retrieval Hit Rate phục hồi 100%, F1 phục hồi 75.00%.

- **Corruption ảnh hưởng rõ nhất:** Việc **xóa tóm tắt (Blank Summary)** gây tác động nặng nề nhất vì tóm tắt chứa thông tin ngữ nghĩa cốt lõi để Vector Search và LLM trả lời câu hỏi.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Tầm quan trọng của Raw Data Snapshot**: Luôn lưu dữ liệu thô ban đầu để có thể tái tạo pipeline (Reproducibility) và sửa lỗi ETL bất kỳ lúc nào mà không phụ thuộc vào API bên ngoài.
2. **Thiết kế Data Observability chủ động**: Cần xây dựng các bộ lọc Quality & Freshness tự động phát hiện dữ liệu rác trước khi đẩy vào Vector DB để tránh làm hỏng RAG Agent.
3. **Cố định bộ Eval Set**: Để đo lường tác động của dữ liệu xấu một cách khoa học, bộ câu hỏi đánh giá bắt buộc phải được đóng băng cố định.

### Nếu có thêm thời gian

- Phát triển thêm module tự động phát hiện và loại bỏ các bản ghi trùng lặp xấp xỉ (Near-deduplication) dựa trên độ tương đồng Cosine giữa các văn bản.

---

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Văn Phong  
**Ngày xác nhận:** 2026-08-06
