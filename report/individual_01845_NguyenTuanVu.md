# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | Nguyễn Tuấn Vũ |
| **MSSV** | 2A202601845 |
| **Khóa/Lớp** | Cohort K3 |
| **Tên nhóm** | Team C1 |
| **Vai trò chính** | Evaluation & Observability Owner (Vai trò 4) |
| **Repository** | `c:\AI20K\LABS\K3_Day10_TeamC1` |
| **Ngày hoàn thành** | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :---: |
| **Evaluation Test Set** | [`src/evaluation/testset.py`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/src/evaluation/testset.py)<br>`build_test_set` | Cleaned Data (`papers_clean.json`) | `data/eval/test_set.json` (40 câu hỏi test đóng băng 4 dạng) | Hoàn thành |
| **Data Quality & Observability** | [`src/observability/quality.py`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/src/observability/quality.py)<br>`run_data_quality_checks`<br>`build_freshness_report` | Cleaned / Corrupted / Repaired DataFrames | `baseline_quality_check.json`, `corrupted_quality_check.json`, `repaired_quality_check.json`, `freshness_report.json` | Hoàn thành |
| **Observability Reporting Engine** | [`src/observability/reporting.py`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/src/observability/reporting.py)<br>`generate_phase1_report`<br>`generate_corruption_report` | Quality JSONs, RAG Evaluation Metrics | `data/reports/phase1_report.md`<br>`data/reports/corruption_report.md` | Hoàn thành |
| **Pipeline Integration** | [`src/pipelines/corruption_flow.py`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/src/pipelines/corruption_flow.py)<br>`main` | 3 Trạng thái Data & Chroma Index | Chạy tự động end-to-end Pha 2 và sinh Báo cáo 3 Cột | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả và bằng chứng |
| :--- | :--- | :--- |
| **Xây dựng Tài liệu Hướng dẫn & Master Contract** | Cả nhóm (Team C1) | Khởi tạo tài liệu master [`Guide_labs.md`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/Guide_labs.md) thống nhất luồng làm việc 210 phút. |
| **Xử lý Xung đột Git & Giữ tương thích Code** | Thành viên 2 (Data Cleaning) | Giải quyết xung đột merge file `quality.py`, kết hợp 2 chuẩn giao tiếp (`checks` array + `metrics` dict) để pipeline của cả nhóm không bị crash. |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| **Đóng băng bộ câu hỏi đánh giá (Frozen Eval Set)** | [`src/evaluation/testset.py`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/src/evaluation/testset.py) | Bộ 40 câu hỏi factual chuẩn dạng JSON tại [`data/eval/test_set.json`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/eval/test_set.json) | `python -c "import json; data=json.load(open('data/eval/test_set.json')); print(len(data))"` $\rightarrow$ 40 câu |
| **Giám sát Chất lượng & Độ tươi mới Dữ liệu** | [`src/observability/quality.py`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/src/observability/quality.py) | 5 tiêu chí Quality Checks (Row count, Paper ID Integrity, Title non-null, Summary quality, Freshness) xuất ra `data/quality/` | Đã xuất đủ các file JSON báo cáo chất lượng qua 3 kịch bản Baseline, Corrupted, Repaired |
| **Báo cáo So sánh 3 Trạng thái (3-State Comparison Report)** | [`src/observability/reporting.py`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/src/observability/reporting.py) | File Báo cáo Markdown 3 Cột tại [`data/reports/corruption_report.md`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/reports/corruption_report.md) | Kiểm tra trực tiếp bảng số liệu so sánh Delta trong file `corruption_report.md` |

**Artifact cụ thể được tạo ra:**
- File [`data/reports/corruption_report.md`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/reports/corruption_report.md) thể hiện trực quan sự sụt giảm của Retrieval Hit Rate từ **100% xuống 70%** khi dữ liệu hỏng, và sự phục hồi quay về **100%** khi sửa dữ liệu từ raw snapshot.

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Dữ liệu thô từ API thường chứa lỗi (thiếu summary, quá hạn, trùng lặp ID). Trong RAG, nếu dữ liệu bị lỗi lọt qua pipeline mà không có cơ chế giám sát (Data Observability), RAG Agent sẽ tìm kiếm sai hoặc sinh câu trả lời rác mà hệ thống không hề hay biết.

### Cách triển khai
1. **Module `testset.py`**: Trích xuất tự động từ `papers_clean.json` các bài báo mẫu để tạo bộ 40 câu hỏi thuộc 4 dạng (`summary`, `authors`, `date`, `categories`). Đóng băng bộ câu hỏi này thành file `test_set.json` để dùng chung cố định cho cả 3 giai đoạn.
2. **Module `quality.py`**: Thực hiện 5 phép kiểm tra định lượng:
   - `row_count`: Đảm bảo tổng số dòng $> 0$.
   - `paper_id_integrity`: Đảm bảo mã DOI không bị null và không bị duplicate.
   - `title_non_null`: Đảm bảo tiêu đề không bị rỗng.
   - `summary_quality`: Đảm bảo summary không rỗng và không quá ngắn ($< 100$ ký tự).
   - `freshness_threshold`: Tính `age_days` so với ngưỡng 180 ngày.
3. **Module `reporting.py`**: Nhận kết quả từ Quality Engine và Evaluator Engine để tự động sinh báo cáo Markdown theo định dạng chuẩn 3 cột (Baseline vs Corrupted vs Repaired).

### Input, output và contract

| Thành phần | Mô tả |
| :--- | :--- |
| **Input** | Cleaned Dataframes (`papers_clean.json`, `papers_clean_corrupted.json`, `papers_clean_repaired.json`). |
| **Output** | `test_set.json`, `baseline_quality_check.json`, `corrupted_quality_check.json`, `repaired_quality_check.json`, `corruption_report.md`. |
| **Module phụ thuộc** | `src/ingestion/cleaning.py`, `src/retrieval/index.py`, `src/evaluation/metrics.py`. |
| **Module sử dụng output** | `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`, `report/group_report.md`. |
| **Điều kiện lỗi cần xử lý** | Truy cập an toàn vào dictionary metadata (dùng `.get()`) để không bị crash khi dữ liệu hỏng bị thiếu trường. |

### Cách xác minh

```powershell
python -m src.pipelines.corruption_flow
```

- **Kết quả mong đợi:** Pipeline chạy liên hoàn Pha 2 qua 3 trạng thái, in ra log summary, Quality checks chuyển từ `PASS` $\rightarrow$ `FAIL` $\rightarrow$ `PASS`, và tự động cập nhật file `corruption_report.md`.
- **Kết quả thực tế:** Pipeline chạy hoàn toàn thành công với 0 lỗi, Retrieval Hit Rate phục hồi từ `70%` lên `100%`.
- **Artifact/log:** [`data/reports/corruption_report.md`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/reports/corruption_report.md)

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Khi xây dựng cấu trúc hàm `run_data_quality_checks`, cần quyết định định dạng dữ liệu trả về và ghi log báo cáo JSON sao cho linh hoạt nhất.
- **Các phương án đã cân nhắc:**
  - *Phương án A*: Trả về mảng danh sách kết quả kiểm tra (`checks: [{check, passed, details}]`). Dễ duyệt vòng lặp hiển thị báo cáo.
  - *Phương án B*: Trả về dictionary các số liệu tổng hợp (`metrics: {paper_id_null_count, missing_summary_count...}`). Dễ dùng cho các phép tính toán hoặc lọc dataframe.
- **Phương án đã chọn:** **Phương án Hybrid (Kết hợp A & B)**. Trả về một dictionary chứa cả 2 trường `checks` và `metrics`, đồng thời cung cấp cả cờ `status` ("PASS"/"FAIL") và `all_passed`.
- **Lý do:** Tương thích 100% với cả mã nguồn do đồng đội khác lỡ viết trước đó và giao diện báo cáo Observability của mình, đảm bảo tính tương thích ngược (backward compatibility) và tuyệt đối không làm vỡ Hợp đồng Dữ liệu (Data Contract).
- **Bằng chứng quyết định phù hợp:** Cả 2 script `phase1.py` và `corruption_flow.py` đều đọc kết quả quality report và xuất báo cáo Markdown mà không hề phát sinh lỗi runtime nào.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```text
  KeyError: 'categories_joined'
  File "src/retrieval/qa.py", line 28, in _extract_answer
      return metadata["categories_joined"]
  ```
- **Lệnh hoặc bước tái hiện:** `python -m src.pipelines.corruption_flow` khi RAG Agent chạy trên tập dữ liệu bị làm hỏng `papers_clean_corrupted.json`.
- **Nguyên nhân gốc:** Hàm `_extract_answer` trong `qa.py` truy cập trực tiếp bằng cú pháp dict `metadata["categories_joined"]`. Khi dữ liệu bị corrupt, một số bản ghi bị khuyết trường metadata hoặc null làm dict không chứa key này.
- **Cách xử lý:** Thay thế cú pháp truy cập trực tiếp bằng phương thức an toàn `dict.get()` có giá trị mặc định:
  ```python
  return str(metadata.get("categories_joined", ""))
  ```
- **Cách xác minh sau khi sửa:** Chạy lại `python -m src.pipelines.corruption_flow` $\rightarrow$ Pipeline thực thi mượt mà qua 40 câu hỏi dữ liệu hỏng mà không còn gặp lỗi `KeyError`.
- **Điều học được:** Khi viết code cho các hệ thống Observability và Evaluation chịu trách nhiệm kiểm thử dữ liệu hỏng/rác, luôn phải áp dụng tư duy "lập trình phòng thủ" (defensive programming) để code không bị sập khi gặp dữ liệu không hợp lệ.

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   - Crossref REST API trả về JSON thô $\rightarrow$ `crossref.py` lưu raw snapshot $\rightarrow$ `cleaning.py` lọc bản ghi rác, làm sạch HTML, tính `age_days` và tạo chuỗi `text_for_embedding` $\rightarrow$ `index.py` dùng mô hình `all-MiniLM-L6-v2` chuyển chuỗi văn bản thành Vector 384 chiều và nạp vào cơ sở dữ liệu ChromaDB.

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   - Với mỗi câu hỏi trong `test_set.json`, RAG Agent tìm kiếm top-k tài liệu trong ChromaDB (`retrieved_doc_ids`). Nếu bất kỳ ID nào nằm trong `ground_truth_doc_ids`, `retrieval_hit` được tính là `True`. Đáp án sinh ra được so sánh từ vựng (Token F1) và chấm điểm ngữ nghĩa bởi LLM Judge (thang điểm 1-5).

3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - **Quality checks**: Kiểm tra tính toàn vẹn tĩnh của cấu trúc dữ liệu (số dòng $>0$, mã ID không bị null/duplicate, title và summary không rỗng).
   - **Freshness monitoring**: Kiểm tra tính cập nhật theo thời gian của dữ liệu (tính tuổi bài báo `age_days` so với mốc hiện tại và cảnh báo nếu có bài báo vượt quá ngưỡng 180 ngày).

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   - Việc cố định bộ câu hỏi (`frozen test set`) qua cả 3 giai đoạn giúp đảm bảo tính đo lường công bằng (apples-to-apples comparison). Điểm số sụt giảm hay phục hồi hoàn toàn phản ánh đúng chất lượng dữ liệu chứ không phải do câu hỏi bị thay đổi.

5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   - Repair thành công khi Quality Check chuyển từ **`FAIL` $\rightarrow$ `PASS`**, Freshness chuyển từ **`STALE` $\rightarrow$ `FRESH`**, và chỉ số RAG `Retrieval Hit Rate` phục hồi từ **`70%` quay lại `100%`** trong file [`data/reports/corruption_report.md`](file:///c:/AI20K/LABS/K3_Day10_TeamC1/data/reports/corruption_report.md).

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| :--- | :-: | :-: | :-: | :--- |
| `retrieval_hit_rate` | **`100.00%`** | **`70.00%`** | **`100.00%`** | Dữ liệu lỗi làm mất tóm tắt dẫn đến tìm kiếm trượt 30%. Khôi phục dữ liệu đã giúp Hit Rate quay lại 100%. |
| `mean_token_f1` | **`75.00%`** | **`57.85%`** | **`75.00%`** | F1 sụt giảm mạnh do các tóm tắt bài báo bị xóa rỗng, và phục hồi hoàn toàn sau khi re-clean từ raw snapshot. |
| `judge_accuracy` | **`97.50%`** | **`57.50%`** | **`72.50%`** | Tỷ lệ câu trả lời đạt điểm tối đa của LLM Judge bị sụt giảm mạnh khi dữ liệu bị làm nhiễu. |
| `mean_judge_score` | **`4.90 / 5`** | **`3.45 / 5`** | **`3.90 / 5`** | Điểm số đánh giá ngữ nghĩa trung bình của Giám khảo LLM bị giảm 1.45 điểm khi gặp dữ liệu xấu. |
| Quality checks | **`PASS`** | **`FAIL`** | **`PASS`** | Quality Engine cảnh báo chính xác màu đỏ ngay khi phát hiện các hàng bị thiếu summary hoặc trùng ID. |
| Freshness status | **`FRESH`** | **`STALE`** | **`FRESH`** | Freshness Engine tự động chuyển sang `STALE` khi phát hiện 2 bản ghi bị sửa ngày về quá khứ xa. |

### Kết luận từ số liệu

1. **[Data corruption] $\rightarrow$ [quality/freshness signal thay đổi] $\rightarrow$ [agent metric thay đổi]**:
   - Khi cố ý làm hỏng dữ liệu (xóa summary, lùi ngày xuất bản), Quality Check lập tức báo **`FAIL`** (`missing_summary_count > 0`), Freshness báo **`STALE`** (`stale_rows = 2`), kéo sụt giảm ngay lập tức `Retrieval Hit Rate` từ **100% xuống 70%** và Token F1 từ **75% xuống 57.85%**.
2. **[Repair action] $\rightarrow$ [quality/freshness signal phục hồi] $\rightarrow$ [agent metric phục hồi]**:
   - Khi thực hiện Re-clean từ bản sao lưu thô `crossref_records.json`, toàn bộ lỗi cấu trúc được làm sạch, Quality Check phục hồi về **`PASS`**, Freshness phục hồi về **`FRESH`**, và `Retrieval Hit Rate` phục hồi hoàn toàn về **`100%`**.

**Corruption ảnh hưởng rõ nhất:** 
- Hành vi **xóa rỗng tóm tắt (Blank Summary)** gây ảnh hưởng nghiêm trọng nhất vì đoạn văn bản tóm tắt đóng vai trò là ngữ cảnh chính cho mô hình Embedding tra cứu ngữ nghĩa.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Về Data Pipeline**: Bản sao lưu dữ liệu thô (Raw Snapshot) là "cứu tinh" duy nhất giúp hệ thống phục hồi (Data Repair) 100% mà không cần tốn chi phí gọi lại API từ đầu.
2. **Về Data Quality/Observability**: Giám sát dữ liệu là chốt chặn sinh tử. Việc phát hiện lỗi ngay tại đường ống ETL giúp ngăn ngừa sự cố RAG trước khi người dùng phát hiện ra.
3. **Về ảnh hưởng của Data đến RAG Agent**: "Garbage in, Garbage out" — Mô hình LLM hay Vector DB dù mạnh đến đâu cũng sẽ trả về câu trả lời sai lệch nếu dữ liệu đầu vào bị rác hoặc mất mát ngữ cảnh.

### Nếu có thêm thời gian

- Tích hợp thêm framework kiểm thử tự động **Great Expectations (GX)** để thiết lập các bộ quy tắc (Expectation Suites) nâng cao và tạo giao diện Dashboard hiển thị báo cáo Observability trực quan hơn.

---

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Tuấn Vũ  
**Ngày xác nhận:** 2026-08-06
