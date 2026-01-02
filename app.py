from flask import Flask, render_template, request
import search_logic as search
import query_rewrite
import ai_explain
import json
import time

app = Flask(__name__)

# --- 讀取統計資料 ---
def get_stats():
    try:
        with open(search.METADATA_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        return {"total_pages": len(metadata)}
    except:
        return {"total_pages": 0}

stats = get_stats()

# --- 首頁 ---
@app.route('/')
def index():
    return render_template('index.html')

# --- 搜尋結果頁 (雙版本比較模式) ---
@app.route('/search')
def search_route():
    user_question = request.args.get('q', '')
    
    # 初始化變數
    results = []
    
    # 分別儲存 A/B 版的結果
    genai_queries_a = []
    genai_queries_b = []
    explanation_a = ""
    explanation_b = ""
    
    time_taken = 0.0
    error_msg = None
    
    if user_question:
        try:
            print(f"收到使用者查詢: {user_question}")
            
            # --- 階段 1: GenAI 查詢改寫 (Query Rewrite) ---
            # 同時執行 A 版與 B 版
            print("正在執行 Query Rewrite (A & B)...")
            genai_queries_a = query_rewrite.rewrite_query(user_question, version='A')
            genai_queries_b = query_rewrite.rewrite_query(user_question, version='B')
            
            # --- 階段 2: 執行搜尋 (Search) ---
            # 策略：為了讓比較基準一致 (Explanation 比較的是同一組文章)，
            # 我們使用效果較好的 B 版關鍵字來進行實際搜尋。
            # (或者你也可以把 A 和 B 的關鍵字合併起來搜尋)
            search_query = " ".join(genai_queries_b)
            
            results, time_taken = search.perform_search(search_query)
            
            if isinstance(results, dict) and "error" in results:
                error_msg = results["error"]
                results = []
            
            # --- 階段 3: GenAI 結果解釋 (Explanation) ---
            if results:
                print("正在執行 AI Explanation (A & B)...")
                # 同時生成 A 版與 B 版的解釋，讓使用者比較差異
                explanation_a = ai_explain.explain_results(user_question, results, version='A')
                explanation_b = ai_explain.explain_results(user_question, results, version='B')
            else:
                msg = "搜尋引擎未找到相關文章，無法生成解釋。"
                explanation_a = msg
                explanation_b = msg

        except Exception as e:
            print(f"處理過程發生錯誤: {e}")
            error_msg = f"系統發生錯誤: {e}"
    
    # --- 渲染網頁 (傳入所有 A/B 版資料) ---
    return render_template('results.html',
                           user_question=user_question,
                           
                           # 傳入兩組資料
                           genai_queries_a=genai_queries_a,
                           genai_queries_b=genai_queries_b,
                           explanation_a=explanation_a,
                           explanation_b=explanation_b,
                           
                           results=results,
                           time_taken=time_taken,
                           error_msg=error_msg
                          )

@app.route('/about')
def about():
    return render_template('about.html', total_pages=stats["total_pages"])

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)