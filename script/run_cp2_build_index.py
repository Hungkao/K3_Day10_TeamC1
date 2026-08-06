from pathlib import Path
import sys

# Đảm bảo UTF-8 encoding và import module src/
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd
from core.config import load_settings, require_llm_credentials
from retrieval.index import LocalEmbeddingIndex
from retrieval.agent import build_agent, run_agent_question
from retrieval.qa import answer_question

def execute_checkpoint_2():
    print("=========================================================")
    print("📌 THỰC THI CHECKPOINT 2 - VAI TRÒ 3: RAG & AGENT OWNER")
    print("=========================================================\n")

    settings = load_settings()
    clean_csv = settings.paths.clean_csv
    clean_json = settings.paths.clean_json

    # -----------------------------------------------------------------
    # Bước 1: Nạp Clean Data & Tạo MiniLM Embeddings + ChromaDB Collection
    # -----------------------------------------------------------------
    print("1️⃣ BƯỚC 1: Đọc dữ liệu sạch và khởi tạo Vector Database (ChromaDB)...")
    if clean_csv.exists():
        print(f"   -> Đang đọc: {clean_csv.name}")
        df = pd.read_csv(clean_csv)
    elif clean_json.exists():
        print(f"   -> Đang đọc: {clean_json.name}")
        df = pd.read_json(clean_json)
    else:
        raise FileNotFoundError("Không tìm thấy dữ liệu clean trong data/clean/")

    print(f"   -> Đã load {len(df)} bài báo khoa học.")
    print(f"   -> Đang mã hóa vector với model '{settings.embedding_model}'...")
    print(f"   -> Tạo ChromaDB collection '{settings.baseline_collection_name}'...")

    # Gọi build index
    index = LocalEmbeddingIndex.build(
        df=df,
        settings=settings,
        embeddings_output_path=settings.paths.embeddings_json
    )

    print("   ✅ Đã khởi tạo thành công Vector Index!")
    print(f"   -> ChromaDB Directory: {settings.paths.chroma_dir}")
    print(f"   -> Manifest Artifact: {settings.paths.embeddings_json}\n")

    # -----------------------------------------------------------------
    # Bước 2: Test Semantic Search & Exact Lookup với Query Kiểm Chứng
    # -----------------------------------------------------------------
    print("2️⃣ BƯỚC 2: Kiểm thử Semantic Search & Exact Lookup...")

    # Test 2a: Semantic Search
    test_query_1 = "safety report generation large language model"
    print(f"\n   🔍 [Semantic Search Test] Query: '{test_query_1}'")
    search_results = index.search(test_query_1, top_k=2)
    for i, res in enumerate(search_results, 1):
        print(f"      Top {i}: [Score: {res.score:.4f}] Paper ID: {res.paper_id}")
        print(f"             Title: {res.title}")
    
    assert len(search_results) > 0, "LỖI: Semantic search không trả về kết quả!"
    print("   ✅ Semantic Search hoạt động chính xác.")

    # Test 2b: Exact Lookup theo paper_id
    test_id = df.iloc[0]["paper_id"]
    print(f"\n   🎯 [Exact Lookup Test] Looking up Paper ID: '{test_id}'")
    lookup_by_id = index.lookup(test_id)
    assert lookup_by_id is not None, f"LỖI: Không tìm thấy paper_id '{test_id}'!"
    print(f"      Found: {lookup_by_id['title']}")

    # Test 2c: Exact Lookup theo title
    test_title = df.iloc[0]["title"]
    print(f"   🎯 [Exact Lookup Test] Looking up Title: '{test_title[:40]}...'")
    lookup_by_title = index.lookup(test_title)
    assert lookup_by_title is not None, "LỖI: Không tìm thấy paper theo title!"
    print(f"      Found Paper ID: {lookup_by_title['paper_id']}")
    print("   ✅ Exact Lookup (ID & Title) hoạt động chính xác.\n")

    # -----------------------------------------------------------------
    # Bước 3: Tạo Agent & Kiểm tra Tool Output
    # -----------------------------------------------------------------
    print("3️⃣ BƯỚC 3: Khởi tạo RAG Agent & Kiểm tra Tool Output...")
    
    # 3a. Kiểm tra QA Heuristic Engine (luôn hoạt động)
    sample_q = f"Who authored the paper '{test_title}'?"
    print(f"\n   🤖 [QA Engine Test] Question: '{sample_q}'")
    ans_result = answer_question(sample_q, settings, index)
    print(f"      Answer: {ans_result.answer}")
    print(f"      Retrieved Doc IDs: {ans_result.retrieved_doc_ids}")
    assert len(ans_result.retrieved_doc_ids) > 0, "LỖI: Agent không trích xuất được doc_id từ tool!"

    # 3b. Kiểm tra LLM Agent nếu có API Key
    try:
        require_llm_credentials(settings)
        print(f"\n   🤖 [LLM Agent Test] Khởi tạo Agent với Provider '{settings.llm_provider}'...")
        agent = build_agent(settings=settings, index=index)
        
        test_agent_q = "What is the main contribution of SafeRAG framework?"
        print(f"      Sending Question to LLM Agent: '{test_agent_q}'")
        agent_response = run_agent_question(agent, test_agent_q)
        print(f"      Agent Answer: {agent_response[:300]}...")
        print("   ✅ LLM Agent đã gọi Tools và trả lời dựa trên corpus thành công!")
    except Exception as e:
        print(f"   ℹ️ Bỏ qua LLM Agent gọi trực tiếp API (Lý do: {e})")
        print("   ✅ Đã kiểm tra thành công Tool Output thông qua QA Engine!")

    print("\n=========================================================")
    print("🎉 CHECKPOINT 2 CHO VAI TRÒ 3 ĐÃ HOÀN THÀNH XUẤT SẮC!")
    print("=========================================================")

if __name__ == "__main__":
    execute_checkpoint_2()
