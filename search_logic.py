import joblib
import json
from sklearn.metrics.pairwise import cosine_similarity
import time
# ★ 修改點：從 utils 匯入
from utils import jieba_tokenizer 

# --- 1. 設定區 ---
VECTORIZER_PATH = "tfidf_vectorizer.joblib"
MATRIX_PATH = "tfidf_matrix.joblib"
METADATA_PATH = "metadata.json"
SNIPPET_LENGTH = 150

# (原本這裡的 def jieba_tokenizer... 請刪除)

# --- 2. 載入模型 ---
print("正在載入搜尋模型...")
try:
    # 現在載入時，joblib 會去 utils.py 找 jieba_tokenizer，而我們已經 import 了，所以會成功
    vectorizer = joblib.load(VECTORIZER_PATH)
    tfidf_matrix = joblib.load(MATRIX_PATH)
    
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print(f"模型載入成功。共 {len(metadata)} 筆文件。")

except Exception as e:
    print(f"載入模型失敗: {e}")
    vectorizer, tfidf_matrix, metadata = None, None, None

# --- 3. 搜尋函式 (保持不變) ---
def perform_search(query_string, top_k=5):
    # ... (原本的搜尋邏輯完全不用動) ...
    # 為了完整性，這裡列出關鍵部分
    if vectorizer is None:
        return {"error": "搜尋引擎未初始化"}, 0.0

    print(f"\n執行搜尋: '{query_string}'")
    start_time = time.time()
    
    try:
        query_vector = vectorizer.transform([query_string])
        similarities = cosine_similarity(query_vector, tfidf_matrix)
        scores = similarities[0]
        top_indices = scores.argsort()[-top_k:][::-1]
        
        results = []
        for rank, idx in enumerate(top_indices):
            score = scores[idx]
            if score < 0.01: continue
            
            item = metadata[idx]
            snippet = item.get('text', '')[:SNIPPET_LENGTH].replace("\n", " ") + "..."
            
            results.append({
                "rank": rank + 1,
                "title": item.get('title', 'No Title'),
                "url": item.get('url', '#'),
                "snippet": snippet,
                "score": float(score)
            })
            
        return results, (time.time() - start_time) * 1000

    except Exception as e:
        return {"error": str(e)}, 0.0