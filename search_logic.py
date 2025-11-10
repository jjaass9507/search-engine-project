import joblib
import json
from sklearn.metrics.pairwise import cosine_similarity
import time
import jieba # 雖然 vectorizer 會自動呼叫，但 import 起來以防萬一

# --- 1. 設定區 ---
VECTORIZER_PATH = "tfidf_vectorizer.joblib"
MATRIX_PATH = "tfidf_matrix.joblib"
METADATA_PATH = "metadata.json"
SNIPPET_LENGTH = 100 # 摘要長度 (字)

# --- 2. 載入模型 (在程式啟動時只載入一次) ---
print("正在載入搜尋模型...")
try:
    vectorizer = joblib.load(VECTORIZER_PATH)
    tfidf_matrix = joblib.load(MATRIX_PATH)
    
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print(f"模型載入成功。共 {len(metadata)} 筆文件。")

except FileNotFoundError:
    print("="*30)
    print("錯誤：找不到索引檔案！")
    print("請先執行 crawler.py 和 indexer.py。")
    print("="*30)
    # 這裡我們先設為 None，讓程式可以 import，但 search 會失敗
    vectorizer, tfidf_matrix, metadata = None, None, None
except Exception as e:
    print(f"載入模型時發生未預期錯誤: {e}")
    vectorizer, tfidf_matrix, metadata = None, None, None


# --- 3. 核心搜尋函式 ---
def perform_search(query_string, top_k=10):
    """
    執行搜尋並回傳 top_k 個結果
    """
    # 修正後的檢查：明確檢查 None
    if vectorizer is None or tfidf_matrix is None or metadata is None:
        return {"error": "搜尋引擎尚未初始化。"}, 0.0

    print(f"\n收到查詢: '{query_string}'")
    
    # 1. 記錄開始時間
    start_time = time.time()

    # 2. 將查詢字串轉換為 TF-IDF 向量
    #    TfidfVectorizer 會自動使用我們在 indexer.py 中設定的
    #    斷詞器 (tokenizer) 和停用詞 (stopwords)
    try:
        query_vector = vectorizer.transform([query_string])
    except Exception as e:
        print(f"查詢轉換失敗: {e}")
        return {"error": f"查詢處理失敗: {e}"}, 0.0

    # 3. 計算餘弦相似度 (Cosine Similarity)
    #    計算「查詢向量」和「所有文件向量」的相似度
    #    結果會是 (1, N) 的矩陣，N 是文件總數
    similarities = cosine_similarity(query_vector, tfidf_matrix)

    # 4. 取得分數並排序
    #    similarities[0] 是一個包含 N 個分數的 array
    #    我們使用 .argsort() 找出分數最高的前 K 個的「索引 (index)」
    #    [::-1] 是將排序反轉 (從高到低)
    scores = similarities[0]
    top_indices = scores.argsort()[-top_k:][::-1]

    # 5. 整理並回傳結果
    results = []
    for rank, idx in enumerate(top_indices):
        # 從 scores 取得分數
        score = scores[idx]
        
        # 如果分數太低 (例如 0)，就不顯示
        if score < 0.01: # 你可以調整這個閾值
            continue

        # 從 metadata 取得原始資料
        item = metadata[idx]
        
        # 產生摘要 (snippet)
        full_text = item.get('text', '')
        snippet = full_text[:SNIPPET_LENGTH].replace("\n", " ") + "..."

        results.append({
            "rank": rank + 1,
            "title": item.get('title', 'No Title'),
            "url": item.get('url', ''),
            "snippet": snippet,
            "score": float(score) # 轉換為 python float
        })

    # 6. 記錄結束時間
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000 # 轉換為毫秒

    print(f"查詢完成，找到 {len(results)} 筆結果，花費 {elapsed_time:.2f} 毫秒。")
    
    # 回傳結果列表 和 執行時間
    return results, elapsed_time


# --- 4. 終端機測試區塊 ---
if __name__ == "__main__":
    # 這個區塊只會在
    # python search_logic.py
    # 執行時才會被觸發，
    # 在 app.py 中 import 它時不會觸發
    
    # 修正後的檢查：明確檢查 None
    if vectorizer is None or tfidf_matrix is None or metadata is None:
        print("無法執行測試，模型載入失敗。")
    else:
        print("\n--- 搜尋引擎終端機測試 ---")
        print("輸入 'exit' 離開。")
        while True:
            query = input("請輸入查詢關鍵字: ")
            if query.lower() == 'exit':
                break
            
            results, time_taken = perform_search(query)
            
            if isinstance(results, dict) and "error" in results:
                print(f"錯誤: {results['error']}")
            elif not results:
                print("查無結果。")
            else:
                print(f"(花費 {time_taken:.2f} 毫秒)")
                for res in results:
                    print(f"  Rank {res['rank']} (Score: {res['score']:.4f})")
                    print(f"  Title: {res['title']}")
                    print(f"  URL: {res['url']}")
                    print(f"  Snippet: {res['snippet']}\n")