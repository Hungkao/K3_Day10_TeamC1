# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | Nguyễn Hữu Khánh Tùng |
| **MSSV** | 2A202601781 |
| **Khóa/Lớp** | K3 |
| **Tên nhóm** | Team C1 (K3_Day10_TeamC1) |
| **Vai trò chính** | **Vai trò 3: RAG & Agent Owner** (Phụ trách Vector DB Indexing, ChromaDB, SentenceTransformers MiniLM, Search & Lookup, RAG Agent Integration) |
| **Repository** | https://github.com/Hungkao/K3_Day10_TeamC1 |
| **Ngày hoàn thành** | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu (Ownership)

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| **Vector DB Indexing (Baseline)** | `src/retrieval/index.py`<br>`LocalEmbeddingIndex.build()` | `data/clean/papers_clean.csv` | Collection `papers-baseline`<br>`data/embeddings/papers_embeddings.json` | Hoàn thành |
| **Vector DB Indexing (Corrupted)** | `src/retrieval/index.py`<br>`LocalEmbeddingIndex.build()` | `data/clean/papers_clean_corrupted.csv` | Collection `papers-corrupted`<br>`data/embeddings/papers_embeddings_corrupted.json` | Hoàn thành |
| **Vector DB Indexing (Repaired)** | `src/retrieval/index.py`<br>`LocalEmbeddingIndex.build()` | `data/clean/papers_clean_repaired.csv` | Collection `papers-repaired`<br>`data/embeddings/papers_embeddings_repaired.json` | Hoàn thành |
| **QA Logic & Groundedness Filter** | `src/retrieval/qa.py`<br>`answer_question()` | User Question, LocalEmbeddingIndex | `AnswerResult` (Answer, Doc IDs, Similarity Score) | Hoàn thành |
| **Agent Tool & Retrieval Integration** | `src/retrieval/agent.py`<br>`build_agent()` | Query, Prompt, Index Tools | Structured Agent Answer | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| **Phân tách & Bảo vệ Baseline** | Member 2 (Data ETL Owner) | Đảm bảo pipeline tạo riêng collection/manifest cho corrupted & repaired mà không làm ghi đè hay mutate `papers-baseline`. |
| **Hỗ trợ Benchmark RAG** | Member 4 (Evaluator Owner) | Cung cấp interface tra cứu đồng nhất cho 3 trạng thái index để Member 4 chạy đánh giá trên `test_set.json`. |
| **Fix Chroma PersistentClient Lock** | Cả nhóm (Team C1) | Xử lý lỗi `Access is denied (os error 5)` trên Windows bằng cơ chế `_CHROMA_CLIENT_CACHE` và cập nhật đường dẫn linh hoạt `settings.paths.chroma_dir`. |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| **Xây dựng Index Baseline (CP2)** | `src/retrieval/index.py`<br>`data/embeddings/papers_embeddings.json` | 24 tài liệu được nhúng (384-dim MiniLM) vào Collection `papers-baseline`. | `LocalEmbeddingIndex.load()`, `collection.count() == 24` |
| **Thực thi QA & Smoke Test (CP3)** | `src/retrieval/qa.py`<br>`src/retrieval/agent.py` | Tra cứu ngữ nghĩa & trích xuất câu trả lời chính xác cho query baseline. | `answer_question()`, Hit Rate = 100% |
| **Tạo Corrupted Index (CP5)** | `data/embeddings/papers_embeddings_corrupted.json` | 23 tài liệu bẩn được đánh index vào Collection `papers-corrupted`. | `LocalEmbeddingIndex.search()`, Score rớt từ 0.62 xuống 0.47 |
| **Tạo Repaired Index (CP6)** | `data/embeddings/papers_embeddings_repaired.json` | 24 tài liệu sạch được khôi phục vào Collection `papers-repaired`. | Top result khôi phục đúng bài SafeRAG gốc (`10.2118/234689-pa`) |

### Output cụ thể do Vai trò 3 phụ trách:
3 Chroma Collection độc lập tồn tại song song trong database SQLite (`papers-baseline`, `papers-corrupted`, `papers-repaired`) và 3 file Embedding Manifest tương ứng (`papers_embeddings.json`, `papers_embeddings_corrupted.json`, `papers_embeddings_repaired.json`).

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Xây dựng thành phần Vector Database và RAG Retrieval cho hệ thống tra cứu bài báo khoa học. Đảm bảo khả năng tra cứu ngữ nghĩa chính xác (Semantic Search), lọc theo tiêu đề (Exact Lookup), tích hợp vào Agentic RAG, đồng thời hỗ trợ so sánh đối chiếu độc lập giữa 3 trạng thái dữ liệu (Baseline, Corrupted, Repaired) mà không bị ghi đè dữ liệu.

### Cách triển khai
1. **Model Embedding**: Sử dụng `sentence-transformers/all-MiniLM-L6-v2` để mã hóa văn bản hợp nhất (`Title + Authors + Published + Summary`) thành vector 384 chiều.
2. **Vector Store**: Sử dụng `ChromaDB` với Cosine Similarity (`hnsw:space = cosine`).
3. **Cơ chế Caching Client**: Xây dựng `_CHROMA_CLIENT_CACHE` trong `src/retrieval/index.py` để chia sẻ duy nhất 1 instance `chromadb.PersistentClient` theo đường dẫn `persist_path`, ngăn chặn xung đột khóa file SQLite trên môi trường Windows.
4. **Đường dẫn linh hoạt**: Thay thế đường dẫn tuyệt đối cứng bằng `settings.paths.chroma_dir` khi load index từ JSON manifest, giúp hệ thống chạy được trên mọi máy tính trong nhóm.

### Input, output và contract

| Thành phần | Mô tả |
| :--- | :--- |
| **Input** | `DataFrame` làm sạch chứa các trường `paper_id`, `title`, `summary`, `authors_joined`, `text_for_embedding`. |
| **Output** | Object `LocalEmbeddingIndex`, file JSON Manifest lưu danh sách tài liệu & metadata, và Chroma Vector Collection. |
| **Module phụ thuộc** | `src/core/config.py` (`Settings`, `Paths`), `sentence_transformers`, `chromadb`. |
| **Module sử dụng output** | `src/retrieval/qa.py`, `src/retrieval/agent.py`, `src/eval/evaluator.py`, `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`. |
| **Điều kiện lỗi cần xử lý** | Khóa file SQLite khi mở nhiều client cùng lúc, trường bị khuyết/NaN trong dữ liệu bẩn, đường dẫn tuyền đối bị lệch giữa các máy. |

### Cách xác minh

```bash
python -c "from core.config import load_settings; from retrieval.index import LocalEmbeddingIndex; s = load_settings(); idx = LocalEmbeddingIndex.load(s); print(idx.collection.count(), idx.search('safety report generation large language model', top_k=1)[0].score)"
```

- **Kết quả mong đợi:** In ra số lượng `24` và kết quả tìm kiếm top 1 có score khoảng `0.6235`.
- **Kết quả thực tế:** In ra đúng `24` và score `0.6235` với Paper ID `10.2118/234689-pa`.
- **Artifact/log:** `data/embeddings/papers_embeddings.json`.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Khi nạp và lưu trữ Embeddings Manifest giữa các môi trường làm việc của thành viên trong nhóm, file `papers_embeddings.json` ban đầu chứa đường dẫn tuyệt đối (`persist_path: "C:\\Users\\Admin\\Desktop\\..."`), gây ra lỗi không tìm thấy database khi đồng bộ về máy cá nhân.
- **Các phương án đã cân nhắc:**
  1. *Phương án 1*: Yêu cầu mỗi người tự sửa thủ công file JSON manifest sau mỗi lần `git pull`.
  2. *Phương án 2*: Sửa hàm `LocalEmbeddingIndex.load()` trong `src/retrieval/index.py` để luôn nạp `persist_path` từ `settings.paths.chroma_dir` (được định nghĩa linh hoạt theo root dự án hiện tại).
- **Phương án đã chọn:** Phương án 2.
- **Lý do:** Đảm bảo tính **Reproducibility** và khả năng làm việc nhóm mượt mà. Không phụ thuộc vào đường dẫn tuyệt đối trên máy của từng người.
- **Bằng chứng quyết định phù hợp:** Code chạy thành công 100% trên tất cả các máy trong nhóm sau khi pull mã nguồn mới mà không cần bất kỳ thao tác cấu hình lại đường dẫn thủ công nào.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```text
  chromadb.errors.InternalError: Access is denied. (os error 5)
  ```
- **Lệnh hoặc bước tái hiện:** Thực thi script khởi tạo `LocalEmbeddingIndex.load()` và `LocalEmbeddingIndex.build()` liên tiếp trong cùng một tiến trình Python trên Windows.
- **Nguyên nhân gốc:** ChromaDB trên Windows sử dụng Rust bindings kết nối SQLite. Mỗi lần gọi `chromadb.PersistentClient(path=...)`, một connection mới được tạo ra và khóa file `chroma.sqlite3`. Khi gọi lại trong cùng process, Windows ngăn không cho tiến trình mở thêm lock song song, dẫn đến lỗi OS Error 5.
- **Cách xử lý:** Thêm dictionary `_CHROMA_CLIENT_CACHE` trong `src/retrieval/index.py` để cache client instance. Nếu `persist_path` đã tồn tại trong cache, sử dụng lại instance cũ thay vì khởi tạo mới.
- **Cách xác minh sau khi sửa:** Chạy lại script thử nghiệm cả 3 collection (`papers-baseline`, `papers-corrupted`, `papers-repaired`) trong 1 lần thực thi duy nhất, script chạy mượt mà với Exit Code 0.
- **Bài học kỹ thuật:** Xử lý I/O và database connection trên Windows cần đặc biệt lưu ý đến cơ chế File Lock và ưu tiên reuse client instance.

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   * Raw JSON thu thập từ Crossref API (`raw/crossref_response.json`) được trích xuất thành danh sách bản ghi (`raw/crossref_records.json`).
   * Pipeline ETL làm sạch dữ liệu, kiểm tra schema, tạo cột ghép `text_for_embedding` và lưu thành CSV (`data/clean/papers_clean.csv`).
   * `LocalEmbeddingIndex.build()` đọc CSV, dùng model `all-MiniLM-L6-v2` chuyển đổi cột văn bản thành vector nhúng 384 chiều và lưu trữ vào ChromaDB (`data/chroma/`).

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   * File `data/eval/test_set.json` chứa 40 câu hỏi kiểm thử kèm danh sách `ground_truth_doc_ids` (ID bài báo chuẩn chứa câu trả lời).
   * Khi đo `retrieval_hit_rate`, hệ thống cho RAG search `top_k=4` tài liệu và kiểm tra xem `ground_truth_doc_ids` có xuất hiện trong danh sách trả về hay không.
   * `judge_accuracy` dùng LLM Judge (Gemini) để chấm điểm câu trả lời sinh ra so với ground truth theo thang điểm từ 1 đến 5.

3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   * **Quality checks**: Kiểm tra tính vẹn toàn cấu trúc của dữ liệu (không trùng lặp `paper_id`, không rỗng tiêu đề/tóm tắt, tóm tắt có độ dài thích hợp `> 100` ký tự).
   * **Freshness monitoring**: Kiểm tra mốc thời gian xuất bản của bài báo (`published` date) so với ngưỡng ngày quy định (180 ngày) để đảm bảo dữ liệu không bị lạc hậu.

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   * Để đảm bảo tính công bằng và nhất quán tuyệt đối của thực nghiệm (Benchmark Consistency).
   * Giúp đo lường chính xác mức độ suy giảm hiệu năng do nhiễu dữ liệu gây ra (Corrupted) và mức độ phục hồi của hệ thống sau khi được làm sạch lại (Repaired).

5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   * **Artifacts**: File `repaired_quality_check.json` báo trạng thái `"PASS"`, file metrics `repaired_metrics.json` được khởi tạo.
   * **Metrics**: `retrieval_hit_rate` phục hồi từ **0.70 lên 1.00 (100%)**, `judge_accuracy` phục hồi từ **0.575 lên 0.725**, và `mean_judge_score` tăng từ **3.45 lên 3.90**.

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| :--- | ---: | ---: | ---: | :--- |
| `retrieval_hit_rate` | **1.0000** | **0.7000** | **1.0000** | Nhiễu dữ liệu làm rớt 30% khả năng tra cứu. Khi repair, Hit Rate phục hồi hoàn toàn về 100%. |
| `mean_token_f1` | **0.7500** | **0.5785** | **0.7500** | Token F1 phục hồi 100% về mức baseline ban đầu sau khi làm sạch dữ liệu. |
| `judge_accuracy` | **1.0000** | **0.5750** | **0.7250** | Phục hồi mạnh mẽ từ 57.5% lên 72.5%. |
| `mean_judge_score` | **5.0000** | **3.4500** | **3.9000** | Điểm số đánh giá chất lượng câu trả lời của LLM Judge phục hồi rõ rệt. |
| **Quality checks** | **PASS** | **FAIL** | **PASS** | Corrupted vi phạm trùng lặp ID & thiếu tóm tắt; Repaired đạt 100% tiêu chuẩn vẹn toàn. |
| **Freshness status** | **PASS** | **FAIL** | **PASS** | Corrupted bị tiêm dữ liệu cũ (>180 ngày); Repaired loại bỏ hoàn toàn bài báo cũ. |

### Kết luận từ số liệu

1. **Chuỗi nguyên nhân – bằng chứng 1 (Corruption)**:
   `[Injected Gibberish & Duplicate IDs]` → `[Quality Check FAIL: 2 Duplicate IDs, 5 Missing Summaries]` → `[Hit Rate giảm từ 1.00 xuống 0.70 & Judge Accuracy giảm từ 1.00 xuống 0.575]`.
2. **Chuỗi nguyên nhân – bằng chứng 2 (Repair)**:
   `[Re-ingest & Re-clean from Raw Source]` → `[Quality Check PASS: 0 Duplicates, 0 Missing Summaries]` → `[Hit Rate phục hồi về 1.00 & Token F1 phục hồi về 0.75]`.

*   **Corruption nào ảnh hưởng rõ nhất và vì sao?**: Xóa tóm tắt (`missing_summary`) và chèn từ vô nghĩa (`gibberish`) ảnh hưởng nghiêm trọng nhất vì làm mất thông tin ngữ nghĩa trong không gian vector của MiniLM, dẫn đến câu hỏi tìm kiếm trả về các tài liệu không liên quan.
*   **Kết quả khác với kỳ vọng ban đầu**: `judge_accuracy` của Repaired (0.725) chưa về lại mức 1.0 như Baseline ban đầu do một số bài báo ở luồng repair có độ dài tóm tắt ngắn hơn nhẹ so với bản gốc, tuy nhiên `retrieval_hit_rate` đã khôi phục hoàn hảo 100%.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. **Về Data Pipeline**: Dữ liệu đầu vào quyết định trực tiếp chất lượng RAG ("Garbage in, Garbage out"). Phải thiết kế pipeline làm sạch tự động có khả năng tái lập (reproducible).
2. **Về Data Quality & Observability**: Việc xây dựng bộ Quality Checks và Freshness Checks giúp phát hiện sớm sự suy giảm chất lượng dữ liệu trước khi nó ảnh hưởng đến người dùng cuối.
3. **Về RAG Agent**: RAG Agent hoạt động phụ thuộc lớn vào độ chính xác của Vector Index. Khi Vector Index bị nhiễu, ngay cả LLM mạnh cũng không thể tạo ra câu trả lời đúng.

### Nếu có thêm thời gian
Tôi sẽ triển khai thêm cơ chế **Hybrid Search (kết hợp BM25 Keyword Search + Dense Vector Search với Reranker)** trong `src/retrieval/index.py` để tăng cường khả năng tra cứu chính xác cả theo từ khóa chuyên ngành lẫn ngữ nghĩa.

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
