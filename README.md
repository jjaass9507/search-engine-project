# 資訊檢索 (IR) 期末專案 - 迷你搜尋引擎
# (Information Retrieval Term Project - Mini Search Engine)

這是一個為「資訊檢索與生成式AI (Information Retrieval and Generative Artificial Intelligence)」課程所打造的小型網頁搜尋引擎。

本專案不僅實作了基礎的搜尋引擎流程，還包含了**搜尋品質評估 (Precision@5)** 以及 **片語搜尋 (Bigrams)** 等進階功能。

**Demo:**
*(建議上傳一張網頁截圖取代此行)*

---

## 🚀 專案特色 (Features)

### 核心功能
1.  **(A) 網頁爬蟲 (`crawler.py`):**
    * 使用 `requests` + `BeautifulSoup4`。
    * **禮貌爬取**：遵循 `robots.txt` 規範及 2 秒延遲 (`CRAWL_DELAY`)。
    * 目標爬取 1,000 頁特定主題 (如 AI/Tech) 網頁。
2.  **(B) 索引建立 (`indexer.py`):**
    * 使用 `scikit-learn` 的 `TfidfVectorizer`。
    * **進階文字處理**：包含英文停用詞移除、動態 `max_df`/`min_df` 閾值調整。
    * 將模型序列化儲存為 `.joblib` 檔，確保搜尋效率。
3.  **(C) 搜尋與排序 (`search_logic.py`):**
    * 使用 **餘弦相似度 (Cosine Similarity)** 進行排序。
    * 支援顯示搜尋結果摘要 (Snippet) 與相關性分數。
4.  **(D) 網頁介面 (`app.py`):**
    * 基於 **Flask** 的輕量級 Web App。
    * 包含首頁、結果頁、關於頁面。

### 🏆 加分功能 (Bonus Features)
* **搜尋品質評估工具 (`evaluate.py`):**
    * 實作 **Precision@5** 評估指標。
    * 提供互動式介面，讓使用者手動標註搜尋結果相關性，並計算平均準確率 (MAP)。
* **支援片語搜尋 (Phrase Search Support):**
    * 在索引階段啟用 `ngram_range=(1, 2)`。
    * 除了單字 (Unigrams) 外，也能索引雙字片語 (Bigrams)，提升搜尋 "Artificial Intelligence" 等專有名詞的精確度。
* **搜尋效能顯示:**
    * 在搜尋結果頁即時顯示查詢耗時 (毫秒)。

---

## 🛠 技術棧 (Tech Stack)

* **Language:** Python 3.x
* **Web Framework:** Flask
* **IR / ML Libraries:** scikit-learn, numpy, scipy
* **Crawling:** requests, beautifulsoup4
* **Utilities:** joblib (模型儲存), jieba (中文斷詞支援 - 選用)

---

## 💻 如何執行 (How to Run)

### 1. 環境設定

```bash
# 1. 下載專案
git clone [你的 GitHub Repo URL]
cd ir_project

# 2. 建立並啟動虛擬環境
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安裝依賴
pip install -r requirements.txt
2. 執行管線 (Pipeline)
請依序執行以下步驟來啟動系統：

步驟一：資料爬取

Bash

python crawler.py
產出：crawled_data.json

步驟二：建立索引

Bash

python indexer.py
產出：tfidf_matrix.joblib, tfidf_vectorizer.joblib, metadata.json

步驟三：啟動搜尋引擎

Bash

python app.py
前往瀏覽器打開 http://127.0.0.1:5000 開始搜尋！

3. 執行評估 (Bonus)
如果你想測試搜尋引擎的準確度：

Bash

python evaluate.py
程式會自動執行預設的 5-10 個查詢。

請依照提示輸入 y (相關) 或 n (不相關)。

最後將顯示 平均 Precision@5 分數。

📂 檔案結構
Plaintext

ir_project/
│
├── .gitignore           # Git 忽略設定
├── README.md            # 專案文件
├── requirements.txt     # 套件依賴清單
│
├── crawler.py           # (A) 爬蟲程式
├── indexer.py           # (B) 索引程式 (含 Bigram 設定)
├── search_logic.py      # (C) 搜尋邏輯核心
├── app.py               # (D) Flask 網頁主程式
├── evaluate.py          # (Bonus) Precision@5 評估工具
│
├── templates/           # 網頁模板
│   ├── index.html       # 搜尋首頁
│   ├── results.html     # 結果頁 (含時間顯示)
│   └── about.html       # 關於頁面
│
└── (自動生成檔案 - 不上傳 GitHub)
    ├── crawled_data.json
    ├── metadata.json
    ├── *.joblib
    └── venv/
