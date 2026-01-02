import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

# --- 1. 設定區 ---
SEED_URLS = [
    "https://techcrunch.com/category/artificial-intelligence/",
    "https://www.wired.com/tag/artificial-intelligence/",
    "https://www.technologyreview.com/topic/artificial-intelligence/",
    "https://venturebeat.com/category/ai/",
    "https://www.ithome.com.tw/tags/AI",
    "https://buzzorange.com/techorange/tag/ai/",
    "https://www.bnext.com.tw/categories/ai",
    # 建議：如果首頁都爬過了，可以手動加入第2頁的網址，例如：
    # "https://www.ithome.com.tw/tags/AI?page=1", 
]

MAX_NEW_PAGES = 200   # 目標新增頁數
TOTAL_LIMIT = 2000    # 總資料庫上限
CRAWL_DELAY = 0.5
OUTPUT_FILE = "crawled_data.json"

# --- Helper: 取得正規化網域 (移除 www.) ---
def get_domain(url):
    netloc = urlparse(url).netloc
    if netloc.startswith("www."):
        return netloc[4:]
    return netloc

# --- 2. 爬蟲核心邏輯 ---
def crawl():
    existing_data = []
    visited_urls = set()
    
    # 1. 載入舊資料
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                for item in existing_data:
                    visited_urls.add(item['url'])
            print(f"已載入現有資料庫，共 {len(existing_data)} 筆。")
        except:
            existing_data = []

    if len(existing_data) >= TOTAL_LIMIT:
        print("資料庫已達上限，停止爬取。")
        return

    # 2. 準備佇列與允許網域
    queue = list(SEED_URLS)
    
    # 建立允許網域白名單 (使用 loose matching)
    allowed_domains = set()
    for url in SEED_URLS:
        allowed_domains.add(get_domain(url))
    
    print(f"允許的網域根目錄: {allowed_domains}")

    new_crawled_data = []
    robot_parsers = {}

    print(f"開始爬取，目標新增 {MAX_NEW_PAGES} 頁...")

    while queue and len(existing_data) + len(new_crawled_data) < TOTAL_LIMIT and len(new_crawled_data) < MAX_NEW_PAGES:
        current_url = queue.pop(0)

        # 檢查是否已訪問 (若是種子則強制重爬)
        if current_url in visited_urls and current_url not in SEED_URLS:
            continue

        # 禮貌延遲
        current_count = len(existing_data) + len(new_crawled_data) + 1
        print(f"[{current_count}/{TOTAL_LIMIT}] 正在爬取: {current_url}")
        time.sleep(CRAWL_DELAY)

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(current_url, headers=headers, timeout=10)
            
            if response.status_code != 200 or 'text/html' not in response.headers.get('Content-Type', ''):
                continue

            visited_urls.add(current_url)

            # 解析
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # --- 儲存邏輯 (僅當不是重複的種子頁時才儲存) ---
            # 我們假設種子頁是列表頁，不需要存內文，只需要它的連結
            # 但如果你也想存種子頁內容，可以把下方 if 判斷拿掉
            is_seed = current_url in SEED_URLS
            if not is_seed:
                # 清理內文
                for script in soup(["script", "style", "nav", "footer"]):
                    script.extract()
                text = soup.get_text(separator=' ', strip=True)
                
                if len(text) > 100: # 過濾太短的
                    title = soup.title.string.strip() if soup.title else current_url
                    new_crawled_data.append({
                        "url": current_url,
                        "title": title,
                        "text": text,
                        "fetch_time": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(f"   >>> 成功儲存頁面 (目前新增: {len(new_crawled_data)})")

            # --- 連結提取與除錯 ---
            links = soup.find_all('a', href=True)
            added_count = 0
            skipped_domain = 0
            skipped_visited = 0

            for link in links:
                new_url = urljoin(current_url, link['href']).split('#')[0]
                
                # 簡單過濾非 http 連結
                if not new_url.startswith('http'):
                    continue

                new_domain = get_domain(new_url)

                # 寬容網域檢查：只要 new_domain 包含在 allowed 列表中的任何一個，就算通過
                # 例如：buzzorange.com 包含在 buzzorange.com/techorange 邏輯內
                domain_match = False
                for allowed in allowed_domains:
                    if allowed in new_domain or new_domain in allowed:
                        domain_match = True
                        break
                
                if domain_match:
                    if new_url not in visited_urls and new_url not in queue:
                        queue.append(new_url)
                        added_count += 1
                    else:
                        skipped_visited += 1
                else:
                    skipped_domain += 1
            
            # ★ 關鍵除錯訊息：告訴我為什麼這一頁沒貢獻新連結
            print(f"   (連結分析: 找到 {len(links)} 個, 加入佇列 {added_count} 個, 已訪問跳過 {skipped_visited}, 網域不符跳過 {skipped_domain})")

        except Exception as e:
            print(f"爬取錯誤 {current_url}: {e}")

    # 存檔
    if new_crawled_data:
        total = existing_data + new_crawled_data
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(total, f, ensure_ascii=False, indent=4)
        print(f"\n任務完成！本次新增 {len(new_crawled_data)} 筆，總計 {len(total)} 筆。")
    else:
        print("\n任務結束，未新增任何資料。")

if __name__ == "__main__":
    crawl()