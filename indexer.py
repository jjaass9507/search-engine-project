import json
import jieba  # 如果你處理中文，就需要
import time
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib # 用來儲存/載入模型

# --- 1. 設定區 ---
INPUT_FILE = "crawled_data.json"
OUTPUT_VECTORIZER = "tfidf_vectorizer.joblib"
OUTPUT_MATRIX = "tfidf_matrix.joblib"
OUTPUT_METADATA = "metadata.json" # 儲存 URL 和標題，供搜尋結果顯示

# --- 2. 中文斷詞函式 (如果你爬的是英文，可以跳過) ---
def jieba_tokenizer(text):
    """
    使用 jieba 進行中文斷詞，並過濾掉單個字的 token
    """
    # seg_list = jieba.cut(text, cut_all=False) # 精確模式
    seg_list = jieba.cut_for_search(text) # 搜尋引擎模式
    
    # 過濾掉單個字 (除非它是英文字母或數字，例如 'A' 或 '5')
    # 並過濾掉純粹的標點符號或空白
    tokens = []
    for word in seg_list:
        word = word.strip()
        if word and (len(word) > 1 or word.isalnum()):
            tokens.append(word)
    
    return tokens

# --- 3. 載入停用詞 (可選，但建議) ---
def load_stopwords(file_path="stopwords.txt"):
    """
    從檔案載入停用詞列表。
    你需要自己去網路上下載一份中文停用詞表 (例如：
    https://github.com/goto456/stopwords/blob/master/cn_stopwords.txt
    或
    https://github.com/goto456/stopwords/blob/master/en_stopwords.txt
    )
    並儲存為 'stopwords.txt'
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            stopwords = [line.strip() for line in f.readlines()]
        print(f"成功載入 {len(stopwords)} 個停用詞。")
        return stopwords
    except FileNotFoundError:
        print("警告：未找到 'stopwords.txt'，將不使用停用詞。")
        return [] # 回傳空列表

# --- 4. 索引器主程式 ---
def build_index():
    print("開始建立索引...")
    
    # 1. 載入爬取的資料
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            crawled_data = json.load(f)
    except FileNotFoundError:
        print(f"錯誤：找不到 {INPUT_FILE}。請先執行 crawler.py！")
        return
    except json.JSONDecodeError:
        print(f"錯誤：{INPUT_FILE} 檔案內容不是有效的 JSON。")
        return

    if not crawled_data:
        print("錯誤：資料檔案為空，無法建立索引。")
        return

    print(f"成功載入 {len(crawled_data)} 筆爬蟲資料。")

    # 2. 準備文件內容 (corpus) 和 metadata
    # corpus 是 TfidfVectorizer 需要的「文件內文列表」
    corpus = []
    # metadata 儲存對應的 URL 和 title，用於前端顯示
    metadata = []

    for item in crawled_data:
        # 確保 text 欄位存在且有內容
        if 'text' in item and item['text']:
            corpus.append(item['text'])
            metadata.append({
                "url": item.get("url", ""),
                "title": item.get("title", "No Title"),
                "text": item['text']  # <-- 請加上這一行
            })
        else:
            print(f"警告：跳過一筆資料，缺少 'text' 欄位。 URL: {item.get('url')}")

    if not corpus:
        print("錯誤：沒有可供索引的有效文字內容。")
        return
        
    print(f"準備好 {len(corpus)} 份文件進行索引。")

    # 3. 載入停用詞
    stopwords = load_stopwords() # 試著載入 'stopwords.txt'

    # 4. 設定 TF-IDF Vectorizer
    print("正在設定 TF-IDF Vectorizer...")
    
    # ** 關鍵設定：中文 vs 英文 **
    # 如果是中文:
    # vectorizer = TfidfVectorizer(
    #     tokenizer=jieba_tokenizer,  # 使用 jieba 斷詞
    #     stop_words=stopwords if stopwords else None, # 使用停用詞
    #     max_df=0.8,                 # 忽略在 80% 以上文件中都出現的詞 (太常見)
    #     min_df=5,                   # 忽略在 5 份以下文件中出現的詞 (太罕見)
    #     max_features=20000          # 最終矩陣只保留最重要的 20000 個詞
    # )
    
    # 如果是英文 (請取消註解下面這段，並註解掉上面中文的 vectorizer):
    vectorizer = TfidfVectorizer(
        stop_words='english',     # 使用內建的英文停用詞
        max_df=0.98,
        min_df=2,
        max_features=20000
    )

    # 5. 執行 TF-IDF 計算
    print("正在計算 TF-IDF 矩陣... (這可能需要幾分鐘)")
    start_time = time.time()
    
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    end_time = time.time()
    print(f"TF-IDF 矩陣計算完成！")
    print(f"矩陣維度: {tfidf_matrix.shape}") # (文件數量, 詞彙數量)
    print(f"花費時間: {end_time - start_time:.2f} 秒")

    # 6. 儲存結果
    print("正在儲存索引檔案...")
    
    # 儲存 TF-IDF 矩陣
    joblib.dump(tfidf_matrix, OUTPUT_MATRIX)
    print(f"TF-IDF 矩陣已儲存至 {OUTPUT_MATRIX}")

    # 儲存 Vectorizer 物件 (非常重要，搜尋時需要用它來轉換 query)
    joblib.dump(vectorizer, OUTPUT_VECTORIZER)
    print(f"Vectorizer 物件已儲存至 {OUTPUT_VECTORIZER}")

    # 儲存 metadata
    with open(OUTPUT_METADATA, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    print(f"Metadata 已儲存至 {OUTPUT_METADATA}")

    print("\n索引建立完成！")

# --- 5. 執行索引器 ---
if __name__ == "__main__":
    # 為了讓 jieba 載入自訂詞典或初始化 (如果需要的話)
    # 這裡可以放一個 dummy 斷詞，確保載入完成
    if 'jieba' in globals():
        jieba.cut("初始化jieba") 
        
    build_index()