import json
import os
import re
from google import genai
from google.genai import types

# --- 修改點：改從環境變數讀取 ---
# 如果讀不到 (None)，會拋出錯誤提醒你設定
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    # 這裡建議直接報錯，避免程式在沒有 Key 的狀況下空轉
    raise ValueError("❌ 錯誤: 未偵測到 GEMINI_API_KEY 環境變數。請在 Render 或本地環境中設定。")

client = genai.Client(api_key=API_KEY)

# 模型設定 (維持上次決定的 gemini-2.0-flash)
model_name = 'gemini-2.0-flash' 

def clean_json_text(text):
    """
    (保留你的清洗邏輯，以防萬一)
    """
    text = text.replace("```json", "").replace("```", "")
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text.strip()

def rewrite_query(user_question, version='B'):
    # ... (這裡的邏輯保持不變) ...
    # 為了節省篇幅，請保留你原本的 rewrite_query 內容
    # 只要確保上面 API_KEY 的讀取方式改了就好
    print(f"--- [GenAI] 正在思考如何改寫: '{user_question}' ---")
    
    if version == 'A':
        prompt = f"""
        Rewrite the question into 3-4 keywords. Output pure JSON.
        Question: "{user_question}"
        JSON Format: {{"queries": ["k1", "k2"]}}
        """
    else:
        prompt = f"""
        You are an SEO expert.
        User Question: "{user_question}"
        Task: Generate 4-5 keyword queries in BOTH Traditional Chinese and English.
        CRITICAL OUTPUT RULE: Output ONLY valid JSON.
        Format: {{"queries": ["English Query", "Chinese Query"]}}
        """

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        
        if not response.text:
            return [user_question]

        cleaned_text = clean_json_text(response.text)
        data = json.loads(cleaned_text)
        queries = data.get("queries", [])
        return queries if queries else [user_question]

    except Exception as e:
        print(f"GenAI 呼叫失敗: {e}")
        return [user_question]