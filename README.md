資訊檢索與生成式 AI 期末專案 - 智慧型搜尋引擎
(IR & GenAI Term Project - Intelligent Search Engine)
這是一個結合 傳統資訊檢索 (TF-IDF) 與 生成式 AI (Google Gemma Model) 的混合式搜尋引擎。

本專案不僅實作了從爬蟲到索引的完整流程，更引入了 LLM 驅動的查詢改寫 (Query Rewriting) 與 搜尋結果摘要解釋 (Result Explanation)，並內建了 Prompt Engineering A/B 測試 機制來分析不同提示詞對生成品質的影響。

🚀 專案特色 (Features)
🧠 1. 生成式 AI 整合 (GenAI Integration)
本系統使用 Google GenAI SDK (google-genai) 串接 Gemma-3-4b-it 模型，增強搜尋體驗：

智慧查詢改寫 (Query Rewrite):

將使用者的自然語言問題（如「深度學習是什麼？」）自動轉換為 4-5 組適合搜尋引擎的 SEO 關鍵字 (中英對照)。

解決使用者關鍵字輸入不精確的問題，提升檢索召回率。

AI 結果解釋 (AI Explanation):

RAG (Retrieval-Augmented Generation) 架構：AI 閱讀前幾名搜尋結果 (Snippet) 後，生成一段簡潔的繁體中文回答，並標註來源出處 (Citations)。

包含 防幻覺 (Anti-Hallucination) 機制，確保回答基於實際搜尋結果。

🔬 2. 提示工程實驗室 (Prompt Engineering Lab)
系統內建 A/B 測試框架，同時執行並比較兩種不同策略的效果：

Version A (Basic): 基礎的直覺式提示詞。

Version B (Advanced): 經過優化的提示詞，包含角色設定 (Persona)、結構化輸出 (JSON)、思考鏈 (CoT) 及多語言要求。

網頁介面比較: 搜尋結果頁面會並列顯示 A/B 兩版的改寫結果與 AI 解釋，方便評估提示工程的效益。

🛠 3. 核心搜尋引擎基礎
(A) 網頁爬蟲 (crawler.py): 遵循 robots.txt 與禮貌延遲，針對 Tech/AI 主題網站進行爬取。

(B) 索引建立 (indexer.py): 使用 jieba 斷詞與 TfidfVectorizer，支援 Bigram (片語搜尋) 與停用詞過濾。

(C) 搜尋排序 (search_logic.py): 基於餘弦相似度 (Cosine Similarity) 進行相關性排序。

(D) 網頁介面 (app.py): 基於 Flask 開發，即時顯示查詢耗時與 AI 生成過程。

📊 4. 評估與分析
Prompt 分析工具 (pe_analysis.py): 獨立腳本，用於自動化測試 Query Rewrite 與 Explanation 的格式正確性、語言一致性與引用準確度。

檢索品質評估 (evaluate.py): 傳統 IR 指標 (Precision@5) 的互動式評測工具。

🛠 技術棧 (Tech Stack)
Core: Python 3.x

GenAI / LLM:

SDK: google-genai

Model: gemma-3-4b-it (via Google Gemini API)

Web Framework: Flask, Jinja2

IR / ML: scikit-learn, numpy, jieba

Crawler: requests, beautifulsoup4

Deployment: gunicorn (Optional)

💻 如何執行 (How to Run)
1. 環境設定
Bash

# 1. 下載專案
git clone [你的 GitHub Repo URL]
cd ir_project

# 2. 建立並啟動虛擬環境 (建議)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安裝依賴
pip install -r requirements.txt
2. 設定 API Key (重要！)
本專案需要 Google Gemini API Key 才能啟用 AI 功能。請至 Google AI Studio 申請 Key。

Windows (PowerShell):

PowerShell

$env:GEMINI_API_KEY="你的_API_KEY_貼在這裡"
macOS / Linux:

Bash

export GEMINI_API_KEY="你的_API_KEY_貼在這裡"
3. 執行管線 (Pipeline)
請依序執行以下步驟：

步驟一：資料爬取

Bash

python crawler.py
# 產出：crawled_data.json
步驟二：建立索引

Bash

python indexer.py
# 產出：tfidf_matrix.joblib, tfidf_vectorizer.joblib, metadata.json
步驟三：啟動搜尋引擎 Web App

Bash

python app.py
前往瀏覽器打開 http://127.0.0.1:5000 開始體驗 AI 搜尋！

🧪 執行實驗與分析
1. 執行提示工程分析 (Prompt Engineering Analysis)
如果你想查看 Prompt A (基礎版) 與 Prompt B (進階版) 在後端的實際表現差異（格式檢查、時間消耗、多語言能力）：

Bash

python pe_analysis.py
2. 執行檢索品質評估 (IR Evaluation)
手動標註搜尋結果相關性，計算 Precision@5 分數：

Bash

python evaluate.py
📂 檔案結構
Plaintext

ir_project/
│
├── .gitignore           # Git 忽略設定
├── README.md            # 專案文件
├── requirements.txt     # 套件依賴清單
│
├── crawler.py           # 爬蟲程式 (TechCrunch, Wired, iThome...)
├── indexer.py           # 索引程式 (TF-IDF + Jieba)
├── search_logic.py      # 搜尋核心邏輯
├── utils.py             # 共用工具 (包含 jieba tokenizer)
│
├── app.py               # Flask Web App (整合 GenAI A/B 測試)
├── query_rewrite.py     # [GenAI] 查詢改寫模組 (呼叫 Gemma)
├── ai_explain.py        # [GenAI] 結果解釋模組 (呼叫 Gemma)
│
├── pe_analysis.py       # [Analysis] Prompt Engineering 分析腳本
├── evaluate.py          # [Analysis] Precision@5 評估工具
│
├── templates/           # 網頁模板
│   ├── index.html       # 搜尋首頁
│   ├── results.html     # 結果頁 (顯示 A/B 版比較與搜尋結果)
│   └── about.html       # 關於頁面
│
└── (自動生成檔案)
    ├── crawled_data.json
    ├── metadata.json
    └── *.joblib
