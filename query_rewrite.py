import json
import os
import re  # 新增正則表達式模組
from google import genai
from google.genai import types

# 請換成你的 API Key
API_KEY = "AIzaSyCvxJDe_NhnLsscY_xD1ZPSDeZ3yAE3W5Y"
client = genai.Client(api_key=API_KEY)

# ★ 設定為 Gemma 模型 (請確認你的列表中有這個名稱，通常要有 -it 結尾)
# 例如: 'gemma-3-12b-it' 或 'gemma-3-4b-it'
model_name = 'gemma-3-12b-it' 

def clean_json_text(text):
    """
    清洗 Gemma 回傳的文字，移除 Markdown 標記，嘗試提取 JSON 部分
    """
    # 1. 移除 ```json 和 ``` 標記
    text = text.replace("```json", "").replace("```", "")
    
    # 2. 嘗試找出第一個 { 和最後一個 } 之間的內容
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text.strip()

def rewrite_query(user_question, version='B'):
    print(f"--- [Gemma] 正在思考如何改寫: '{user_question}' ---")
    
    if version == 'A':
        prompt = f"""
        Rewrite the question into 3-4 keywords. Output pure JSON.
        Question: "{user_question}"
        JSON Format: {{"queries": ["k1", "k2"]}}
        """
    else:
        # Prompt B: 針對 Gemma 加強語氣，要求不要輸出 Markdown
        prompt = f"""
        You are an SEO expert.
        User Question: "{user_question}"
        
        Task:
        Generate 4-5 keyword queries in BOTH Traditional Chinese and English.
        
        CRITICAL OUTPUT RULE:
        1. Output ONLY valid JSON.
        2. DO NOT use Markdown blocks (no ```). 
        3. NO intro or outro text.
        
        Format:
        {{"queries": ["English Query", "Chinese Query"]}}
        """

    try:
        # ★ 關鍵修改：移除了 config=... 的 JSON 設定
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        if not response.text:
            return [user_question]

        # ★ 手動清洗與解析
        cleaned_text = clean_json_text(response.text)
        # print(f"DEBUG (Raw): {cleaned_text}") # 如果解析失敗可以打開這行檢查
        
        data = json.loads(cleaned_text)
        queries = data.get("queries", [])
        return queries if queries else [user_question]

    except Exception as e:
        print(f"Gemma 呼叫或解析失敗: {e}")
        # 失敗時回傳原問題，避免網頁崩潰
        return [user_question]

if __name__ == "__main__":
    print(rewrite_query("深度學習是什麼？"))