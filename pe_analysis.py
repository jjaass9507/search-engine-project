import json
import time
import query_rewrite
import ai_explain

# 嘗試匯入搜尋模組 (相容改名前後的檔名)
try:
    import search_logic as search
except ImportError:
    try:
        import search_logic as search
    except ImportError:
        search = None
        print("Warning: Could not import 'search' or 'search_logic'. Real search testing will fail.")

# --- 實驗設定 ---
TEST_QUESTIONS = [
    "什麼是生成式 AI？",
    "How to optimize a neural network?"
]

def print_separator(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def run_query_rewrite_experiment():
    print_separator("TASK 1: Query Understanding (Prompt A vs. B)")
    
    for q in TEST_QUESTIONS:
        print(f"\n[User Question]: {q}")
        print("-" * 40)
        
        # --- Version A (Basic) ---
        print(">> Version A (Basic Prompt):")
        start_time = time.time()
        res_a = query_rewrite.rewrite_query(q, version='A')
        duration_a = time.time() - start_time
        print(f"   Output: {json.dumps(res_a, ensure_ascii=False)}")
        print(f"   Time: {duration_a:.4f}s")
        
        print("-" * 20)
        
        # --- Version B (Advanced) ---
        print(">> Version B (Advanced Prompt - Structured & Cross-Lingual):")
        start_time = time.time()
        res_b = query_rewrite.rewrite_query(q, version='B')
        duration_b = time.time() - start_time
        print(f"   Output: {json.dumps(res_b, ensure_ascii=False)}")
        print(f"   Time: {duration_b:.4f}s")
        
        # --- 簡易分析 ---
        is_json_a = isinstance(res_a, list) and len(res_a) > 0
        is_json_b = isinstance(res_b, list) and len(res_b) > 0
        
        print(f"\n   [Analysis]:")
        print(f"   - Format check (A): {'Pass' if is_json_a else 'Fail'}")
        print(f"   - Format check (B): {'Pass' if is_json_b else 'Fail'}")
        
        # 檢查是否包含中英雙語 (簡單啟發式檢查：是否有 ASCII 和 非 ASCII 字元)
        has_ascii_b = any(c.isascii() for w in res_b for c in w)
        has_non_ascii_b = any(not c.isascii() for w in res_b for c in w)
        print(f"   - Cross-lingual check (B): {'Pass' if has_ascii_b and has_non_ascii_b else 'Partial'}")

def run_result_explanation_experiment():
    print_separator("TASK 2: Result Explanation (Prompt A vs. B) using REAL Search Data")
    
    if search is None:
        print("[Error] Search module not found. Skipping Task 2.")
        return

    question = "請解釋生成式 AI 的定義與風險。"
    print(f"\n[User Question]: {question}")
    
    # 1. 取得搜尋關鍵字 (使用 Version B 以獲得最佳搜尋效果)
    print("   [Step 1] Generating search keywords (using Query Rewrite Ver. B)...")
    queries = query_rewrite.rewrite_query(question, version='B')
    search_query = " ".join(queries)
    print(f"   Search Query: {search_query}")

    # 2. 執行搜尋 (使用實際爬取的資料)
    print("   [Step 2] Searching database...")
    # 呼叫 search 模組進行搜尋
    # 注意：需確保已執行過 indexer.py 且有 .joblib 檔案
    results, _ = search.perform_search(search_query)
    
    if not results or (isinstance(results, dict) and "error" in results):
        print(f"   [Error] No results found or Search Engine not initialized.")
        print(f"   Details: {results}")
        return

    # 取前 3 筆結果作為 Context
    context_results = results[:3]
    print(f"   [Step 3] Found {len(results)} results. Using top {len(context_results)} for explanation:")
    for i, res in enumerate(context_results):
        print(f"      Source {i+1}: {res.get('title', 'No Title')}")

    # --- Version A (Basic) ---
    print("\n" + "-" * 40)
    print(">> Version A (Basic Prompt):")
    res_a = ai_explain.explain_results(question, context_results, version='A')
    print(f"\n{res_a.strip()}")
    
    # --- Version B (Advanced) ---
    print("\n" + "-" * 40)
    print(">> Version B (Advanced Prompt - Anti-Hallucination & Citation):")
    res_b = ai_explain.explain_results(question, context_results, version='B')
    print(f"\n{res_b.strip()}")
    
    # --- 簡易分析 ---
    print("\n" + "-" * 40)
    print("   [Analysis]:")
    print(f"   - Citations [Source X] in A: {'Yes' if '[Source' in res_a else 'No'}")
    print(f"   - Citations [Source X] in B: {'Yes' if '[Source' in res_b else 'No'} (Expect: Yes)")
    
    # 檢查語言是否為繁體中文 (簡單檢查常見繁體字)
    traditional_chars = ["為", "這", "個", "會", "說", "與", "對", "學"] 
    is_traditional_b = any(char in res_b for char in traditional_chars)
    print(f"   - Traditional Chinese check (B): {'Pass' if is_traditional_b else 'Check Manually'}")

def main():
    print("Starting Prompt Engineering Analysis...")
    print("注意：請確保 GEMINI_API_KEY 環境變數已設定，且已執行過 crawler.py 與 indexer.py。")
    
    try:
        run_query_rewrite_experiment()
        run_result_explanation_experiment()
    except Exception as e:
        print(f"\n[Error] 執行分析時發生錯誤: {e}")
        print("請檢查 API Key 設定、網路連線或搜尋引擎索引狀態。")

if __name__ == "__main__":
    main()