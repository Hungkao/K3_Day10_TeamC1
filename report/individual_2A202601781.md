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
| Vector Embedding Backend | `src/retrieval/embeddings.py`<br>`MiniLMEmbeddings` | Text string (`text_for_embedding`) | Dense vector list (384 dims) | Hoàn thành |
| Vector Store & Index Manager | `src/retrieval/index.py`<br>`LocalEmbeddingIndex` | Clean/Corrupted/Repaired DataFrames | Persistent ChromaDB collections (`papers-baseline`, `papers-corrupted`, `papers-repaired`) & Search results | Hoàn thành |
| LLM Provider Abstraction | `src/retrieval/llm.py`<br>`build_llm` | Provider name (`gemini`/`openrouter`/`openai`) & API Keys | Unified LLM Client instance | Hoàn thành |
| QA & RAG Search Engine | `src/retrieval/qa.py`<br>`answer_question` | Natural language question, `Settings`, `LocalEmbeddingIndex` | Structured `AnswerResult` (Answer, Retrieved IDs, Contexts) | Hoàn thành |
| Agentic Retrieval Integration | `src/retrieval/agent.py`<br>`run_agent_demo` | Natural language query | Agent response & Tool call log | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả và bằng chứng |
| :--- | :--- | :--- |
| Tích hợp RAG Evaluator | Role 4 (Eval & Observability) | Hỗ trợ hàm `answer_question` để evaluator chạy 40 câu hỏi test set |
| Đảm bảo Zero Baseline Mutation | Role 1 & Role 2 | Đã cập nhật `_derive_collection_name` trong `index.py` để khi chạy corrupted/repaired data thì collection `papers-baseline` không bao giờ bị ghi đè |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Triển khai Mô hình Embedding Local | `src/retrieval/embeddings.py` | Embedding 384 chiều dùng `all-MiniLM-L6-v2` chạy mượt trên CPU | `pytest tests/test_embeddings.py` pass 100% |
| Quản lý Vector Store ChromaDB 3 Trạng thái | `src/retrieval/index.py` | 3 Collections riêng biệt: `papers-baseline`, `papers-corrupted`, `papers-repaired` | `pytest tests/test_index.py` pass 100% |
| Xây dựng RAG QA Engine với Groundedness Check | `src/retrieval/qa.py` | Hàm `answer_question` trả về `AnswerResult` chính xác | `pytest tests/test_qa.py` pass 100% |
| Đa dạng hóa LLM Providers | `src/retrieval/llm.py` | Hỗ trợ Gemini, OpenRouter, OpenAI, Anthropic, Ollama | `pytest tests/test_llm.py` pass 100% |

**Artifact cụ thể đã tạo ra:**
- Thư mục Vector Store ChromaDB tại `data/chroma/` chứa 3 collections độc lập và file embeddings `data/embeddings/papers_embeddings.json`.

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Xây dựng thành phần cốt lõi của RAG System: biến văn bản bài báo thành Vector biểu diễn ngữ nghĩa, lưu trữ vào cơ sở dữ liệu Vector để tra cứu (Similarity Search) với tốc độ cao, kết hợp linh hoạt với nhiều nhà cung cấp LLM (Gemini, OpenRouter, OpenAI) để trả lời câu hỏi chính xác dựa trên ngữ cảnh được trích xuất.

### Cách triển khai
1. **Embedding (`embeddings.py`)**: Sử dụng thư viện `sentence-transformers` nạp mô hình `sentence-transformers/all-MiniLM-L6-v2`. Thực hiện mã hóa chuỗi văn bản `text_for_embedding` thành Vector 384 chiều.
2. **Vector Store Index (`index.py`)**: Đóng gói lớp `LocalEmbeddingIndex` sử dụng `chromadb.PersistentClient`. Hỗ trợ:
   - Tự động phân tách 3 collections: `papers-baseline`, `papers-corrupted`, `papers-repaired` dựa trên đường dẫn file embedding.
   - Tìm kiếm lai (Lookup chính xác theo tiêu đề + Search tương đồng Cosine vector).
3. **LLM Abstraction (`llm.py`)**: Xây dựng lớp bọc `UnifiedLLM` chuẩn hóa giao diện gọi API của các LLM Provider khác nhau (`gemini-2.5-flash`, `openrouter`, `openai`).
4. **QA Engine (`qa.py`)**:
   - Nhận câu hỏi $\rightarrow$ Trích xuất tiêu đề bằng Regex để lookup bài báo chính xác nếu có.
   - Thực hiện Vector Search để lấy Top-k ngữ cảnh liên quan nhất.
   - Cơ chế Kiểm tra Căn cứ (Groundedness Check): Nếu điểm similarity quá thấp ($< 0.20$), trả về *"I don't know from the indexed corpus"* thay vì đoán mò.

### Input, output và contract

| Thành phần | Mô tả |
| :--- | :--- |
| Input | Câu hỏi ngôn ngữ tự nhiên, Cleaned/Corrupted DataFrame, `Settings`. |
| Output | `SearchResult` objects, `AnswerResult` (chứa câu trả lời, `retrieved_doc_ids`, `retrieved_contexts`), ChromaDB collections. |
| Module phụ thuộc | `src/core/config.py`, `src/core/utils.py`, `sentence-transformers`, `chromadb`. |
| Module sử dụng output | `src/evaluation/metrics.py`, `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`. |
| Điều kiện lỗi cần xử lý | Mất kết nối HuggingFace download model (offline cache fallback), lỗi hết API key LLM. |

### Cách xác minh

```bash
pytest tests/test_index.py tests/test_qa.py tests/test_llm.py
```

- **Kết quả mong đợi:** Tất cả các test cases kiểm tra Vector Search, RAG Answer Extraction và LLM Builder đều PASS.
- **Kết quả thực tế:** 8/8 tests PASS 100%.
- **Artifact/log:** `data/embeddings/papers_embeddings.json`, `data/chroma/`.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn mô hình Embedding cho hệ thống RAG trong môi trường lab học tập.
- **Các phương án đã cân nhắc:**
  - *Phương án 1*: Dùng Cloud Embedding API (như OpenAI `text-embedding-3-small` hoặc Google Embedding API).
  - *Phương án 2*: Dùng Local Open-source Embedding Model (`sentence-transformers/all-MiniLM-L6-v2`).
- **Phương án đã chọn:** Phương án 2 (Local Model `all-MiniLM-L6-v2`).
- **Lý do:**
  - *Tính độc lập & Chi phí*: Chạy hoàn toàn 100% offline trên CPU cá nhân, không tốn tiền API, không lo bị nghẽn mạng hay dính Rate Limit (HTTP 429).
  - *Tính nhất quán (Reproducibility)*: Mô hình 384 chiều tạo ra vector cố định 100% cho mọi thành viên trong nhóm, giúp kết quả đánh giá RAG giữa các máy hoàn toàn trùng khớp.
- **Bằng chứng quyết định phù hợp:** Tốc độ tạo vector cực nhanh ($< 1$ giây cho 24 bài báo) và Retrieval Hit Rate đạt mức tuyệt đối 100% ở Baseline.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```text
  chromadb.errors.UniqueConstraintError: Collection papers-baseline already exists.
  ```
- **Lệnh hoặc bước tái hiện:** Chạy lại script `run_phase1.py` nhiều lần mà không xóa cache ChromaDB cũ.
- **Nguyên nhân gốc:** Hàm `LocalEmbeddingIndex.build()` cố gắng gọi `client.create_collection(name="papers-baseline")` khi collection này đã tồn tại trong database SQLite từ lần chạy trước.
- **Cách xử lý:** Bổ sung logic tự động làm sạch collection cũ trước khi build lại:
  ```python
  try:
      client.delete_collection(name=collection_name)
  except Exception:
      pass
  collection = client.create_collection(name=collection_name)
  ```
- **Cách xác minh sau khi sửa:** Chạy lại `python script/run_phase1.py` 5 lần liên tiếp $\rightarrow$ 100% các lần chạy đều tự xóa collection cũ và build lại mượt mà không có lỗi.
- **Điều học được:** Với các hệ thống lưu trữ trạng thái (Stateful Storage như Vector DB), hàm Build bắt buộc phải đạt tính chất Idempotent (chạy nhiều lần cho ra cùng 1 kết quả sạch).

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   - API trả về JSON $\rightarrow$ Cleaning lọc rác và tạo `text_for_embedding` $\rightarrow$ `MiniLMEmbeddings` mã hóa văn bản thành Vector 384 chiều $\rightarrow$ `LocalEmbeddingIndex` nạp véc-tơ và metadata vào ChromaDB persistent collection.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   - `test_set.json` chứa danh sách câu hỏi và `ground_truth_doc_ids`. Khi RAG chạy `answer_question`, nó tìm top-4 bài báo gần nhất. Nếu top-4 này chứa `ground_truth_doc_id` thì tính là `retrieval_hit = True`. Đáp án được chấm điểm F1 và LLM Judge.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - Quality checks kiểm tra tính hợp lệ về mặt cấu trúc (không null, không duplicate, không rỗng). Freshness monitoring kiểm tra tuổi đời dữ liệu (`age_days <= 180`).
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   - Để giữ cố định thước đo. Chỉ khi câu hỏi và đáp án chuẩn không đổi thì sự sụt giảm hay tăng điểm mới phản ánh chính xác chất lượng của dữ liệu đầu vào.
5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   - Thành công khi `papers_clean_repaired.json` được khôi phục, Quality check báo `PASS`, Freshness báo `FRESH`, và `retrieval_hit_rate` trên test set phục hồi về 100%.

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| :--- | ---: | ---: | ---: | :--- |
| `retrieval_hit_rate` | 100.00% | 70.00% | 100.00% | Vector Search trên dữ liệu hỏng bị rớt 30% do thiếu summary; Repair đưa về 100% |
| `mean_token_f1` | 75.00% | 57.85% | 75.00% | F1 giảm mạnh khi context bị mất; Repair giúp trích xuất lại đáp án chuẩn |
| `judge_accuracy` | 97.50% | 57.50% | 72.50% | Điểm ngữ nghĩa bị sụt giảm nặng do dữ liệu bị chèn nhiễu |
| `mean_judge_score` | 4.90 / 5 | 3.45 / 5 | 3.90 / 5 | Điểm trung bình từ LLM Judge bị giảm 1.45 điểm ở trạng thái hỏng |
| Quality checks | PASS | FAIL | PASS | Quality engine phát hiện chính xác các lỗi thiếu tóm tắt và trùng ID |
| Freshness status | FRESH | STALE | FRESH | Freshness engine báo STALE chính xác khi bị lùi ngày |

### Kết luận từ số liệu

1. **[Data corruption] -> [quality/freshness signal thay đổi] -> [agent metric thay đổi]**:
   - Khi dữ liệu bị hỏng (xóa summary, lùi ngày) $\rightarrow$ Quality check chuyển `FAIL`, Freshness chuyển `STALE` $\rightarrow$ Retrieval Hit Rate sụt từ 100% xuống 70%, F1 tụt xuống 57.85%.
2. **[Repair action] -> [quality/freshness signal phục hồi] -> [agent metric phục hồi]**:
   - Khi Re-clean dữ liệu từ snapshot thô `crossref_records.json` $\rightarrow$ Quality check phục hồi `PASS`, Freshness phục hồi `FRESH` $\rightarrow$ Retrieval Hit Rate phục hồi 100%.

- **Corruption ảnh hưởng rõ nhất:** **Blank Summary** ảnh hưởng nặng nhất đến Vector Index vì xóa đi không gian ngữ nghĩa 384 chiều của văn bản.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Về Data Pipeline**: Vector Store là bộ phận phản ánh nhạy bén nhất chất lượng dữ liệu đầu vào.
2. **Về Data Quality/Observability**: Cần có các chốt chặn kiểm tra vector embedding rỗng hoặc bất thường trước khi lưu vào ChromaDB.
3. **Về ảnh hưởng của Data đến RAG Agent**: RAG Agent phụ thuộc hoàn toàn vào ngữ cảnh tìm được từ Vector DB; context hỏng sẽ dẫn đến câu trả lời hỏng.

### Nếu có thêm thời gian

- Thử nghiệm kết hợp phương pháp tìm kiếm lai **Hybrid Search (BM25 Sparse + Vector Dense)** để tăng độ chính xác tìm kiếm với các từ khóa chuyên ngành.

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
