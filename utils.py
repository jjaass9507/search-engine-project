# utils.py
import jieba

def jieba_tokenizer(text):
    """
    共用的斷詞函式，確保 indexer 和 search_logic 都能引用同一個定義。
    """
    # 搜尋引擎模式斷詞
    seg_list = jieba.cut_for_search(text)
    
    tokens = []
    for word in seg_list:
        word = word.strip()
        # 保留長度大於1的詞，或英數字
        if word and (len(word) > 1 or word.isalnum()):
            tokens.append(word)
    
    return tokens