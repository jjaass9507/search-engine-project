# 資訊檢索 (IR) 期末專案 - 迷你搜尋引擎
# (Information Retrieval Term Project - Mini Search Engine)

這是一個為「資訊檢索與生成式AI (Information Retrieval and Generative Artificial Intelligence)」課程所打造的小型網頁搜尋引擎。

本專案實作了小型搜尋引擎的完整四大核心流程：
1.  **(A) Web Spider:** 爬蟲程式
2.  **(B) Indexing:** 索引建立 (使用 TF-IDF)
3.  **(C) Search & Ranking:** 搜尋與排序 (使用 Cosine Similarity)
4.  **(D) Web Interface:** 網頁介面 (使用 Flask)

**Demo:**
[請在這裡放一張你網站首頁的截圖，例如 `search_demo.png`]
---

## 專案特色 (Features)

* **網頁爬蟲 (`crawler.py`):**
    * 使用 `requests` 及 `BeautifulSoup4` 爬取網頁。
    * 遵循 `robots.txt` 規範及 2 秒爬取延遲 (`CRAWL_DELAY`)。
    * 爬取**[請填入你的主題，例如：AI 新聞]**相關主題的網頁，最多 1,000 頁。
    * 將爬取結果 (URL, title, text) 儲存為 `crawled_data.json`。
* **索引建立 (`indexer.py`):**
    * 使用 `scikit-learn` 的 `TfidfVectorizer` 進行文字預處理。
    * 包含**英文停用詞 (Stopwords)** 移除、`max_df` (0.98)、`min_df` (2) 參數調整。
    * (若為中文) 整合 `jieba` 進行中文斷詞。
    * 將 TF-IDF 矩陣及 Vectorizer 物件序列化 (serialize) 儲存為 `.joblib` 檔。
* **搜尋與排序 (`search_logic.py`):**
    * 接收使用者查詢 (Query)。
    * 使用儲存的 Vectorizer 將 Query 轉換為 TF-IDF 向量。
    * 計算 Query 向量與所有文件向量的**餘弦相似度 (Cosine Similarity)**。
    * 回傳 Top-K (預設 10) 相關文件。
* **網頁介面 (`app.py`):**
    * 使用 `Flask` 打造的簡易網頁伺服器。
    * 包含「首頁」、「搜尋結果頁」及「關於本站」三個頁面。
    * (加分項) 顯示查詢花費時間 (ms)。
    * (加分項) 在「關於本站」頁面顯示目前索引的文件總數。

---

## 技術棧 (Tech Stack)

* **Python 3.x**
* **Flask:** 網頁後端框架
* **scikit-learn:** 用於 TF-IDF 向量化及餘弦相似度計算
* **requests:** HTTP 請求 (爬蟲)
* **BeautifulSoup4 (bs4):** HTML 解析 (爬蟲)
* **joblib:** 序列化/反序列化 Python 物件 (儲存索引)
* **jieba:** (選用) 中文斷詞

---

## 如何在本機執行 (How to Run)

**1. 環境設定**

   ```bash
   # 1. 複製此專案
   git clone [你 GitHub Repo 的 URL]
   cd ir_project
   
   # 2. 建立並啟動虛擬環境
   python -m venv venv
   source venv/bin/activate  # (macOS/Linux)
   .\venv\Scripts\activate   # (Windows)
   
   # 3. 安裝所有依賴套件
   pip install -r requirements.txt
2. 執行搜尋引擎管線 (Pipeline)

你需要依序執行 3 個步驟來啟動搜尋引擎。

步驟一：爬取資料 (會花費約 30-40 分鐘)

(可選) 進入 crawler.py 修改 SEED_URLS 為你想爬的種子網站。

Bash

python crawler.py
執行完畢後，你將得到 crawled_data.json 檔案。

步驟二：建立索引

(可選) 進入 indexer.py 調整 TfidfVectorizer 的參數 (例如中文/英文設定)。

Bash

python indexer.py
執行完畢後，你將得到 tfidf_matrix.joblib, tfidf_vectorizer.joblib, metadata.json 三個索引檔案。

步驟三：啟動網頁伺服器

Bash

python app.py
伺服器啟動後，你將看到 search_logic.py 載入模型的日誌。

3. 開始搜尋！

打開你的瀏覽器，前往 http://127.0.0.1:5000 即可開始使用。

檔案結構
ir_project/
│
├── .gitignore          # 告訴 Git 忽略哪些檔案 (重要!)
├── README.md           # 專案說明 (就是本檔案)
├── requirements.txt    # 專案依賴的 Python 套件
│
├── crawler.py          # (A) 網頁爬蟲
├── indexer.py          # (B) 索引建立器
├── search_logic.py     # (C) 搜尋核心邏輯
├── app.py              # (D) Flask 網頁伺服器
│
├── templates/          # Flask 的 HTML 模板
│   ├── index.html      # 首頁
│   ├── results.html    # 搜尋結果頁
│   └── about.html      # 關於頁面
│
├── (爬取後產生的檔案 - 不會上傳到 GitHub)
│   ├── crawled_data.json
│
├── (索引後產生的檔案 - 不會上傳到 GitHub)
│   ├── metadata.json
│   ├── tfidf_matrix.joblib
│   └── tfidf_vectorizer.joblib
│
└── (虛擬環境 - 不會上傳到 GitHub)
    └── venv/