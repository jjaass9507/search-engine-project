import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

# --- 1. 設定區 ---
# 你的種子 URLs (請在這裡填入你決定的網址)
SEED_URLS = [
    "https://techcrunch.com/category/artificial-intelligence/",
    "https://www.wired.com/tag/artificial-intelligence/"
    # ... 填入你的 5-10 個種子 URLs
]

MAX_PAGES = 1000  # 作業要求最多 1000 頁
CRAWL_DELAY = 2     # 作業要求 ≥ 2 秒
OUTPUT_FILE = "crawled_data.json" # 儲存結果的檔案

# --- 2. 爬蟲核心邏輯 ---

def crawl():
    print(f"開始爬取，目標 {MAX_PAGES} 頁，延遲 {CRAWL_DELAY} 秒...")
    
    # 用 set 來儲存已訪問過的 URL，避免重複
    visited_urls = set()
    
    # 用 list 當作佇列 (Queue)，存放待爬取的 URL
    # 我們從種子 URLs 開始
    queue = list(SEED_URLS)
    
    # 儲存爬取結果的 list
    crawled_data = []

    # 準備 robots.txt 解析器
    robot_parsers = {}

    while queue and len(crawled_data) < MAX_PAGES:
        # 1. 從佇列取出一個 URL
        current_url = queue.pop(0)

        # 2. 檢查是否已經爬過
        if current_url in visited_urls:
            continue

        # 3. 檢查 robots.txt (禮貌原則)
        parsed_url = urlparse(current_url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        if domain not in robot_parsers:
            rp = RobotFileParser()
            rp.set_url(urljoin(domain, "robots.txt"))
            try:
                rp.read()
                robot_parsers[domain] = rp
            except Exception as e:
                print(f"無法讀取 {domain}/robots.txt: {e}")
                robot_parsers[domain] = None # 標記為無法讀取
        
        rp = robot_parsers.get(domain)
        if rp and not rp.can_fetch("*", current_url):
            print(f"[跳過] robots.txt 不允許爬取: {current_url}")
            continue

        # 4. 禮貌延遲
        print(f"正在爬取 ({len(crawled_data) + 1}/{MAX_PAGES}): {current_url}")
        time.sleep(CRAWL_DELAY)

        # 5. 抓取網頁
        try:
            response = requests.get(current_url, timeout=5)
            response.raise_for_status() # 如果狀態碼不是 200，會拋出例外
            
            # 確保是 HTML 內容
            if 'text/html' not in response.headers.get('Content-Type', ''):
                print(f"[跳過] 非 HTML 內容: {current_url}")
                visited_urls.add(current_url)
                continue

            visited_urls.add(current_url) # 標記為已訪問

            # 6. 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取標題
            title = soup.title.string.strip() if soup.title else "No Title"

            # 提取主要內文 (這裡用 <p> 標籤當範例，你可能需要根據目標網站調整)
            paragraphs = soup.find_all('p')
            text = "\n".join([p.get_text().strip() for p in paragraphs if p.get_text()])

            if not text:
                print(f"[跳過] 找不到內文: {current_url}")
                continue

            # 7. 儲存結果
            crawled_data.append({
                "url": current_url,
                "title": title,
                "text": text,
                "fetch_time": time.strftime("%Y-%m-%d %H:%M:%S")
            })

            # 8. 找出頁面上的所有連結，並加入佇列
            links = soup.find_all('a', href=True)
            for link in links:
                new_url = urljoin(current_url, link['href'])
                
                # 清理 URL (去掉 # 標記)
                new_url = new_url.split('#')[0]
                
                # 簡單過濾：只爬取同網域或特定網域的 (可選，但建議)
                # 這裡我們只爬取和種子 URL "看起來" 相關的 (簡易判斷)
                if any(seed_domain in new_url for seed_domain in ["techcrunch.com", "wired.com"]): # 記得換成你的
                    if new_url not in visited_urls and new_url not in queue:
                        queue.append(new_url)

        except requests.RequestException as e:
            print(f"爬取失敗: {current_url} (錯誤: {e})")
        except Exception as e:
            print(f"處理失敗: {current_url} (錯誤: {e})")

    # 9. 爬取結束，儲存到 JSON 檔案
    print(f"\n爬取完成！共抓取 {len(crawled_data)} 頁。")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(crawled_data, f, ensure_ascii=False, indent=4)
    print(f"資料已儲存至 {OUTPUT_FILE}")

# --- 3. 執行爬蟲 ---
if __name__ == "__main__":
    crawl()