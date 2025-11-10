from flask import Flask, render_template, request
import search_logic # 匯入我們剛剛寫好的搜尋邏輯！
import json
import time

# 建立 Flask App
app = Flask(__name__)

# --- 讀取統計資料 (用於 About 頁面) ---
def get_stats():
    """ 載入 metadata 來計算索引頁數 """
    try:
        with open(search_logic.METADATA_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        return {"total_pages": len(metadata)}
    except FileNotFoundError:
        return {"total_pages": 0}
    
stats = get_stats()

# --- 1. 建立「首頁」路由 (Route) ---
@app.route('/')
def index():
    """
    渲染首頁 (index.html)
    """
    return render_template('index.html')


# --- 2. 建立「搜尋結果頁」路由 ---
@app.route('/search')
def search():
    """
    接收查詢、執行搜尋，並渲染結果頁 (results.html)
    """
    # 1. 從 URL 參數中取得查詢 (e.g., /search?q=AI)
    #    request.args.get('q', '') 中的 'q' 對應 index.html 中 <input name="q">
    query = request.args.get('q', '')
    
    results = []
    time_taken = 0.0
    error_msg = None

    # 2. 只有在 query 非空時才執行搜尋
    if query:
        print(f"Flask App 收到查詢: {query}")
        try:
            results, time_taken = search_logic.perform_search(query)
            
            # 檢查 search_logic 是否回傳錯誤
            if isinstance(results, dict) and "error" in results:
                error_msg = results["error"]
                results = [] # 清空結果

        except Exception as e:
            print(f"搜尋時發生未預期錯誤: {e}")
            error_msg = f"搜尋時發生錯誤: {e}"
            results = []
    
    # 3. 渲染 results.html 模板，並傳入變數
    return render_template('results.html',
                           query=query,              # 使用者輸入的查詢
                           results=results,          # 搜尋結果列表
                           time_taken=time_taken,    # 查詢花費時間 (毫秒)
                           error_msg=error_msg       # 錯誤訊息 (如果有的話)
                          )

# --- 3. (選用) 建立「關於」頁面 ---
@app.route('/about')
def about():
    """
    顯示索引統計資料 (作業要求)
    """
    return render_template('about.html',
                           total_pages=stats["total_pages"])


# --- 4. 啟動 Flask App ---
if __name__ == "__main__":
    # debug=True 讓我們在修改程式碼後，伺服器會自動重啟
    # host='0.0.0.0' 讓區域網路內的其他裝置也能連線 (可選)
    app.run(debug=True, host='0.0.0.0', port=5000)