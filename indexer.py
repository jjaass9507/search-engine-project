import json
import time
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import jieba
# ★ 修改點：從 utils 匯入函式，而不是在本地定義
from utils import jieba_tokenizer 

# --- 1. 設定區 ---
INPUT_FILE = "crawled_data.json"
OUTPUT_VECTORIZER = "tfidf_vectorizer.joblib"
OUTPUT_MATRIX = "tfidf_matrix.joblib"
OUTPUT_METADATA = "metadata.json"
STOPWORDS_FILE = "stopwords.txt"

# (原本這裡的 def jieba_tokenizer... 請刪除，因為已經移到 utils.py 了)

# --- 3. 載入停用詞 (保持不變) ---
def load_stopwords(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]
    except:
        return []

# --- 4. 索引器主程式 ---
def build_index():
    print("=== 開始建立索引 (使用 utils.jieba_tokenizer) ===")
    
    # ... (讀取資料與準備 corpus 的程式碼保持不變) ...
    # 為了節省篇幅，這裡省略讀檔部分，請保留你原本的邏輯
    # 只要確保前面有 import utils 並且移除了本地的 tokenizer 定義即可
    
    # 假設你已經讀好了 corpus 和 metadata...
    # 如果需要完整程式碼，請參考之前的 indexer.py，只需改最上面 import 和刪除 def
    
    # 讀取檔案邏輯 (簡化版示意，請保留你原本完整的讀取邏輯)
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        crawled_data = json.load(f)
    
    corpus = []
    metadata = []
    for item in crawled_data:
        text = item.get('text', '')
        if text:
            corpus.append(text)
            metadata.append({
                "url": item.get("url", ""),
                "title": item.get("title", "No Title"),
                "text": text
            })

    stopwords = load_stopwords(STOPWORDS_FILE)

    print("正在設定 TF-IDF Vectorizer...")
    
    # ★ 這裡會使用從 utils 匯入的 jieba_tokenizer
    vectorizer = TfidfVectorizer(
        tokenizer=jieba_tokenizer, 
        stop_words=stopwords if stopwords else None,
        max_df=0.95,
        min_df=2,
        max_features=50000,
        token_pattern=None
    )

    print("正在計算 TF-IDF 矩陣...")
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    print("正在儲存模型...")
    joblib.dump(tfidf_matrix, OUTPUT_MATRIX)
    joblib.dump(vectorizer, OUTPUT_VECTORIZER) # 這次存進去的是指向 utils 的參考
    
    with open(OUTPUT_METADATA, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    print("索引重新建立完成！")

if __name__ == "__main__":
    build_index()