import os
from google import genai

# --- 修改點：改從環境變數讀取 ---
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ 錯誤: 未偵測到 GEMINI_API_KEY 環境變數。")

client = genai.Client(api_key=API_KEY)

# ★ 設定為 Gemma 模型
model_name = 'gemma-3-12b-it'

def explain_results(user_question, search_results, version='B'):
    if not search_results:
        return "找不到相關資料，無法回答您的問題。"

    print(f"--- [Gemma] 正在閱讀 {len(search_results)} 筆搜尋結果... ---")

    context = ""
    for i, res in enumerate(search_results):
        title = res.get('title', 'No Title')
        snippet = res.get('snippet', '')
        context += f"[Source {i+1}] Title: {title}\nSnippet: {snippet}\n\n"

    # Gemma 的 Prompt 微調：Gemma 有時比較囉嗦，要明確叫它用繁體中文
    if version == 'A':
        prompt = f"""
        Answer in Traditional Chinese based on snippets:
        Question: {user_question}
        Snippets: {context}
        """
    else:
        prompt = f"""
        You are a research assistant.
        User Question: "{user_question}"
        
        Search Results:
        {context}
        
        Instructions:
        1. Answer in **Traditional Chinese (繁體中文)**.
        2. Base answer ONLY on Search Results.
        3. Cite sources like [Source 1].
        4. Keep it concise (3-5 sentences).
        """

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Gemma 解釋生成失敗: {str(e)}"