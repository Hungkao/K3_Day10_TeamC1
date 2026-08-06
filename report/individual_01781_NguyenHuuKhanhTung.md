# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | Nguyễn Hữu Khánh Tùng |
| **MSSV** | 2A202601781 |
| **Khóa/Lớp** | Cohort K3 |
| **Tên nhóm** | Team C1 |
| **Vai trò chính** | RAG & Agent Owner (Vai trò 3) |
| **Repository** | `d:\AITHUCCHIEN\LABS\LAB10\K3_Day10_TeamC1` |
| **Ngày hoàn thành** | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :---: |
| **Vector DB Indexing (Baseline)** | [`src/retrieval/index.py`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/src/retrieval/index.py)<br>`LocalEmbeddingIndex.build` | Cleaned Data (`papers_clean.csv`) | Collection `papers-baseline`<br>`data/embeddings/papers_embeddings.json` | Hoàn thành |
| **Vector DB Indexing (Corrupted)** | [`src/retrieval/index.py`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/src/retrieval/index.py)<br>`LocalEmbeddingIndex.build` | Corrupted Data (`papers_clean_corrupted.csv`) | Collection `papers-corrupted`<br>`data/embeddings/papers_embeddings_corrupted.json` | Hoàn thành |
| **Vector DB Indexing (Repaired)** | [`src/retrieval/index.py`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/src/retrieval/index.py)<br>`LocalEmbeddingIndex.build` | Repaired Data (`papers_clean_repaired.csv`) | Collection `papers-repaired`<br>`data/embeddings/papers_embeddings_repaired.json` | Hoàn thành |
| **QA Logic & Groundedness Filter** | [`src/retrieval/qa.py`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/src/retrieval/qa.py)<br>`answer_question`<br>`_extract_answer` | User Question, LocalEmbeddingIndex | `AnswerResult` (Answer, Doc IDs, Similarity Score) | Hoàn thành |
| **Agent Tool & Retrieval Integration** | [`src/retrieval/agent.py`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/src/retrieval/agent.py)<br>`build_agent` | Query, Prompt, Index Tools | Structured Agent Answer | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả và bằng chứng |
| :--- | :--- | :--- |
| **Phân tách & Bảo vệ Baseline Collection** | Thành viên 2 (Data ETL Owner) | Đảm bảo pipeline tạo riêng collection và manifest cho corrupted & repaired mà không làm ghi đè hay mutate `papers-baseline`. |
| **Hỗ trợ Interface Tra cứu Benchmark** | Thành viên 4 (Evaluation Owner) | Cung cấp interface tra cứu đồng nhất cho 3 trạng thái index để Thành viên 4 chạy đánh giá bộ `test_set.json`. |
| **Xử lý Khóa File ChromaDB trên Windows** | Cả nhóm (Team C1) | Khắc phục triệt để lỗi `Access is denied (os error 5)` bằng cơ chế `_CHROMA_CLIENT_CACHE` và cập nhật đường dẫn linh hoạt `settings.paths.chroma_dir`. |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| **Xây dựng Index Baseline (CP2)** | [`src/retrieval/index.py`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/src/retrieval/index.py) | 24 tài liệu được mã hóa vector nhúng (384-dim MiniLM) vào Collection `papers-baseline` | `python -c "from core.config import load_settings; from retrieval.index import LocalEmbeddingIndex; s=load_settings(); idx=LocalEmbeddingIndex.load(s); print(idx.collection.count())"` $\rightarrow$ 24 tài liệu |
| **Thực thi QA & Smoke Test (CP3)** | [`src/retrieval/qa.py`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/src/retrieval/qa.py) | Tra cứu ngữ nghĩa & trích xuất câu trả lời chính xác cho query baseline | Run QA smoke test script $\rightarrow$ Hit Rate = 100%, Score > 0.60 |
| **Tạo Corrupted Index (CP5)** | [`data/embeddings/papers_embeddings_corrupted.json`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/data/embeddings/papers_embeddings_corrupted.json) | 23 tài liệu bị làm hỏng được đánh index vào Collection `papers-corrupted` | Run baseline query $\rightarrow$ Top result rớt bài gốc, Score rớt từ 0.6235 xuống 0.4726 |
| **Tạo Repaired Index (CP6)** | [`data/embeddings/papers_embeddings_repaired.json`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/data/embeddings/papers_embeddings_repaired.json) | 24 tài liệu sạch được khôi phục vào Collection `papers-repaired` | Run baseline query $\rightarrow$ Khôi phục chính xác bài SafeRAG gốc với Similarity Score = 0.6235 |

**Artifact cụ thể được tạo ra:**
- 3 Chroma Collection độc lập tồn tại song song trong database SQLite (`papers-baseline`, `papers-corrupted`, `papers-repaired`) và 3 file Embeddings Manifest tương ứng tại [`data/embeddings/papers_embeddings.json`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/data/embeddings/papers_embeddings.json), [`data/embeddings/papers_embeddings_corrupted.json`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/data/embeddings/papers_embeddings_corrupted.json), và [`data/embeddings/papers_embeddings_repaired.json`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/data/embeddings/papers_embeddings_repaired.json).

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Xây dựng thành phần Vector Database và RAG Retrieval cho hệ thống tra cứu bài báo khoa học. Đảm bảo khả năng tra cứu ngữ nghĩa chính xác (Semantic Search), lọc theo tiêu đề (Exact Lookup), tích hợp mượt mà vào Agentic RAG, đồng thời hỗ trợ so sánh đối chiếu độc lập giữa 3 trạng thái dữ liệu (Baseline, Corrupted, Repaired) mà không bị xung đột hay ghi đè dữ liệu.

### Cách triển khai
1. **Model Embedding & ChromaDB Vector Store**: Sử dụng `sentence-transformers/all-MiniLM-L6-v2` để mã hóa văn bản hợp nhất (`Title + Authors + Published + Summary`) thành vector 384 chiều. Lưu trữ vào ChromaDB với không gian độ đo Cosine (`hnsw:space = cosine`).
2. **Cơ chế Client Caching (`_CHROMA_CLIENT_CACHE`)**: Xây dựng dictionary cache cho instance `chromadb.PersistentClient` theo `persist_path` trong `src/retrieval/index.py`. Điều này giúp tái sử dụng duy nhất một kết nối database trên Windows, loại bỏ triệt để lỗi OS File Locking khi mở nhiều client song song.
3. **Đường dẫn Linh hoạt (Cross-Platform Manifest Loading)**: Khi nạp index từ file JSON manifest, hàm `LocalEmbeddingIndex.load()` chủ động ưu tiên đọc `settings.paths.chroma_dir` hiện tại của môi trường thay vì đường dẫn tuyệt đối lưu trong JSON, giúp code chạy mượt mà trên mọi máy tính trong nhóm.

### Input, output và contract

| Thành phần | Mô tả |
| :--- | :--- |
| **Input** | Cleaned DataFrames (`papers_clean.csv`, `papers_clean_corrupted.csv`, `papers_clean_repaired.csv`). |
| **Output** | Object `LocalEmbeddingIndex`, file JSON Manifest lưu danh sách tài liệu & metadata, và Chroma Vector Collection. |
| **Module phụ thuộc** | `src/core/config.py` (`Settings`, `Paths`), `sentence_transformers`, `chromadb`. |
| **Module sử dụng output** | `src/retrieval/qa.py`, `src/retrieval/agent.py`, `src/evaluation/evaluator.py`, `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`. |
| **Điều kiện lỗi cần xử lý** | Xung đột khóa file SQLite trên Windows, trường bị khuyết/NaN trong dữ liệu hỏng, đường dẫn tuyệt đối bị lệch giữa các máy. |

### Cách xác minh

```powershell
python -c "from core.config import load_settings; from retrieval.index import LocalEmbeddingIndex; s = load_settings(); idx = LocalEmbeddingIndex.load(s); print(idx.collection.count(), idx.search('safety report generation large language model', top_k=1)[0].score)"
```

- **Kết quả mong đợi:** In ra số lượng `24` tài liệu và kết quả tìm kiếm top 1 có score đạt mức `0.6235` ứng với bài báo SafeRAG (`10.2118/234689-pa`).
- **Kết quả thực tế:** In ra đúng `24` và score `0.6235` chính xác tuyệt đối.
- **Artifact/log:** [`data/embeddings/papers_embeddings.json`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/data/embeddings/papers_embeddings.json)

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Khi nạp và lưu trữ Embeddings Manifest giữa các môi trường làm việc của thành viên trong nhóm, file `papers_embeddings.json` ban đầu lưu trữ đường dẫn tuyệt đối (`persist_path: "C:\\Users\\Admin\\Desktop\\..."`), gây ra lỗi không tìm thấy database khi các thành viên khác `git pull` mã nguồn về máy cá nhân.
- **Các phương án đã cân nhắc:**
  - *Phương án A*: Yêu cầu từng thành viên tự sửa thủ công file JSON manifest trên máy cá nhân sau mỗi lần pull code.
  - *Phương án B*: Sửa hàm `LocalEmbeddingIndex.load()` trong `src/retrieval/index.py` để luôn đọc `persist_path` linh hoạt từ `settings.paths.chroma_dir` theo thư mục làm việc hiện tại của dự án.
- **Phương án đã chọn:** **Phương án B**.
- **Lý do:** Đảm bảo tính **Tái lập (Reproducibility)** và khả năng làm việc nhóm mượt mà. Loại bỏ hoàn toàn sự phụ thuộc vào cấu trúc thư mục tuyệt đối trên máy của từng cá nhân.
- **Bằng chứng quyết định phù hợp:** Mã nguồn chạy thành công 100% trên tất cả các máy tính trong nhóm sau khi đồng bộ mà không cần bất kỳ thao tác cấu hình lại đường dẫn thủ công nào.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```text
  chromadb.errors.InternalError: Access is denied. (os error 5)
  ```
- **Lệnh hoặc bước tái hiện:** Thực thi script khởi tạo `LocalEmbeddingIndex.load()` và `LocalEmbeddingIndex.build()` liên tiếp trong cùng một tiến trình Python trên môi trường Windows.
- **Nguyên nhân gốc:** ChromaDB trên Windows sử dụng Rust bindings kết nối SQLite. Mỗi lần khởi tạo `chromadb.PersistentClient(path=...)`, một connection mới được tạo ra và khóa file `chroma.sqlite3`. Khi mở lại client trong cùng process, hệ thống file trên Windows ngăn không cho mở thêm lock song song, dẫn đến lỗi OS Error 5.
- **Cách xử lý:** Bổ sung cơ chế caching `_CHROMA_CLIENT_CACHE` dạng dictionary trong `src/retrieval/index.py`:
  ```python
  _CHROMA_CLIENT_CACHE: dict[str, chromadb.PersistentClient] = {}

  def _get_chroma_client(persist_path: str) -> chromadb.PersistentClient:
      abs_path = os.path.abspath(persist_path)
      if abs_path not in _CHROMA_CLIENT_CACHE:
          _CHROMA_CLIENT_CACHE[abs_path] = chromadb.PersistentClient(path=abs_path)
      return _CHROMA_CLIENT_CACHE[abs_path]
  ```
- **Cách xác minh sau khi sửa:** Chạy lại script thử nghiệm cả 3 collection (`papers-baseline`, `papers-corrupted`, `papers-repaired`) trong 1 lần thực thi duy nhất $\rightarrow$ Script thực thi mượt mà với Exit Code 0.
- **Điều học được:** Xử lý I/O và database connection trên hệ điều hành Windows cần đặc biệt lưu ý đến cơ chế File Locking và luôn ưu tiên tái sử dụng (reuse) client instance.

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
   - Repair thành công khi Quality Check chuyển từ **`FAIL` $\rightarrow$ `PASS`**, Freshness chuyển từ **`STALE` $\rightarrow$ `FRESH`**, và chỉ số RAG `Retrieval Hit Rate` phục hồi từ **`70%` quay lại `100%`** trong file [`data/reports/corruption_report.md`](file:///d:/AITHUCCHIEN/LABS/LAB10/K3_Day10_TeamC1/data/reports/corruption_report.md).

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| :--- | :-: | :-: | :-: | :--- |
| `retrieval_hit_rate` | **`100.00%`** | **`70.00%`** | **`100.00%`** | Dữ liệu lỗi làm rớt 30% khả năng tra cứu. Khi repair, Hit Rate phục hồi hoàn toàn về 100%. |
| `mean_token_f1` | **`75.00%`** | **`57.85%`** | **`75.00%`** | Token F1 phục hồi 100% về mức baseline ban đầu sau khi làm sạch lại dữ liệu. |
| `judge_accuracy` | **`100.00%`** | **`57.50%`** | **`72.50%`** | Tỷ lệ câu trả lời đạt điểm tối đa của LLM Judge phục hồi mạnh mẽ từ 57.5% lên 72.5%. |
| `mean_judge_score` | **`5.00 / 5`** | **`3.45 / 5`** | **`3.90 / 5`** | Điểm số đánh giá ngữ nghĩa trung bình của Giám khảo LLM tăng từ 3.45 lên 3.90. |
| Quality checks | **`PASS`** | **`FAIL`** | **`PASS`** | Corrupted vi phạm trùng lặp ID & rỗng summary; Repaired đạt 100% tiêu chuẩn vẹn toàn. |
| Freshness status | **`FRESH`** | **`STALE`** | **`FRESH`** | Freshness Engine cảnh báo `STALE` khi phát hiện bài báo cũ; Repaired loại bỏ hoàn toàn dữ liệu cũ. |

### Kết luận từ số liệu

1. **[Data corruption] $\rightarrow$ [quality/freshness signal thay đổi] $\rightarrow$ [agent metric thay đổi]**:
   - Khi cố ý làm hỏng dữ liệu (xóa rỗng summary, lùi ngày xuất bản), Quality Check báo **`FAIL`** (`missing_summary_count = 5`), Freshness báo **`STALE`** (`stale_rows = 2`), kéo sụt giảm ngay lập tức `Retrieval Hit Rate` từ **100% xuống 70%** và Token F1 từ **75% xuống 57.85%**.
2. **[Repair action] $\rightarrow$ [quality/freshness signal phục hồi] $\rightarrow$ [agent metric phục hồi]**:
   - Khi thực hiện Re-clean từ bản sao lưu thô `crossref_records.json`, toàn bộ lỗi cấu trúc được làm sạch, Quality Check phục hồi về **`PASS`**, Freshness phục hồi về **`FRESH`**, và `Retrieval Hit Rate` phục hồi hoàn toàn về **`100%`**.

**Corruption ảnh hưởng rõ nhất:** 
- Hành vi **xóa rỗng tóm tắt (Blank Summary)** gây ảnh hưởng nghiêm trọng nhất vì tóm tắt đóng vai trò là văn cảnh chính cho mô hình Embedding tra cứu ngữ nghĩa.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Về Data Pipeline**: Dữ liệu đầu vào quyết định trực tiếp chất lượng RAG ("Garbage in, Garbage out"). Cần thiết kế pipeline làm sạch dữ liệu tự động có khả năng tái lập (reproducible).
2. **Về Data Quality/Observability**: Giám sát dữ liệu là chốt chặn sinh tử. Việc phát hiện sớm lỗi dữ liệu giúp ngăn ngừa sự cố RAG trước khi ảnh hưởng tới người dùng cuối.
3. **Về ảnh hưởng của Data đến RAG Agent**: RAG Agent hoạt động phụ thuộc lớn vào độ chính xác của Vector Index. Khi Vector Index bị nhiễu, ngay cả LLM mạnh cũng không thể tạo ra câu trả lời đúng.

### Nếu có thêm thời gian

- Triển khai thêm cơ chế **Hybrid Search (kết hợp BM25 Keyword Search + Dense Vector Search với Reranker)** trong `src/retrieval/index.py` để tăng cường khả năng tra cứu chính xác cả theo từ khóa chuyên ngành lẫn ngữ nghĩa.

---

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Hữu Khánh Tùng  
**Ngày xác nhận:** 2026-08-06
