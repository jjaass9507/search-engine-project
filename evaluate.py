import search_logic
import statistics

def evaluate_search_engine():
    # 1. 確保模型已載入
    if search_logic.vectorizer is None:
        print("錯誤：搜尋模型未載入，請先執行 crawler.py 和 indexer.py。")
        return

    print("="*50)
    print("搜尋引擎評估工具 (Precision@5)")
    print("="*50)
    print("說明：")
    print("本程式會依序執行測試查詢，請您針對每個結果判定是否相關。")
    print("輸入 'y' 或 '1' 代表相關 (Relevant)")
    print("輸入 'n' 或 '0' 代表不相關 (Not Relevant)")
    print("-" * 50)

    # --- 設定測試查詢 ---
    # 請在這裡填入 5-10 個你想測試的關鍵字
    # 建議包含：單詞、你的主題專有名詞、稍微模糊的詞
    test_queries = [
        "artificial intelligence",
        "machine learning",
        "neural networks",
        "deep learning",
        "GPT" 
    ]
    
    precision_scores = []

    for q_idx, query in enumerate(test_queries):
        print(f"\n[{q_idx+1}/{len(test_queries)}] 正在測試查詢: '{query}'...")
        
        # 執行搜尋，取前 5 筆 (Top-5)
        results, _ = search_logic.perform_search(query, top_k=5)
        
        if not results:
            print("  -> 查無結果，跳過此查詢。")
            continue

        relevant_count = 0
        
        print(f"  找到 {len(results)} 筆結果，請開始評分：")
        
        for i, res in enumerate(results):
            print(f"\n  Result #{i+1}:")
            print(f"    Title: {res['title']}")
            print(f"    URL:   {res['url']}")
            print(f"    Snippet: {res['snippet']}")
            
            # 人工標註迴圈
            while True:
                user_input = input("    這筆結果相關嗎？ (y/n): ").strip().lower()
                if user_input in ['y', 'yes', '1']:
                    relevant_count += 1
                    break
                elif user_input in ['n', 'no', '0']:
                    break
                else:
                    print("    請輸入 y 或 n。")
        
        # 計算該查詢的 Precision@5
        # 公式: 相關文件數 / 檢索到的文件數 (通常是5，但如果結果少於5則以實際數量為準)
        p_at_5 = relevant_count / len(results)
        precision_scores.append(p_at_5)
        print(f"  -> 此查詢的 Precision@{len(results)} = {p_at_5:.2f}")

    # --- 最終報告 ---
    if precision_scores:
        avg_precision = statistics.mean(precision_scores)
        print("\n" + "="*50)
        print("評估完成！")
        print("="*50)
        print(f"測試查詢數量: {len(test_queries)}")
        print(f"平均 Precision@5 (MAP): {avg_precision:.4f}")
        print("="*50)
        
        # 這裡的輸出可以直接複製貼上到你的報告中
    else:
        print("\n沒有完成任何有效的評估。")

if __name__ == "__main__":
    evaluate_search_engine()