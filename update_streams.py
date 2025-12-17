import os
import re
from playwright.sync_api import sync_playwright

# 频道配置
DYNAMIC_CHANNELS = {
    "成都新闻综合": "https://www.cditv.cn/show/4845-563.html",
    "成都经济资讯": "https://www.cditv.cn/show/4845-562.html",
    "成都都市生活": "https://www.cditv.cn/show/4845-561.html",
    "成都影视文艺": "https://www.cditv.cn/show/4845-560.html",
    "成都公共": "https://www.cditv.cn/show/4845-559.html",
    "成都少儿": "https://www.cditv.cn/show/4845-558.html",
    "成都高新台": "https://www.cditv.cn/show/4845-591.html"
}

def get_dynamic_url(name, page_url):
    print(f"🚀 正在抓取: {name}...")
    found_url = None
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        # 定义监听逻辑
        def handle_request(request):
            nonlocal found_url
            url = request.url
            # 只要看到带 wsSecret 的 m3u8，立刻锁定
            if ".m3u8?" in url and "wsSecret=" in url:
                found_url = url
            # 或者看到发号器接口
            elif "getLiveUrl" in url and not found_url:
                found_url = url

        page.on("request", handle_request)
        
        try:
            # 修改 1：将等待条件改为 'commit' (只要服务器响应了就开始抓)
            # 修改 2：将超时增加到 60 秒，应对跨境网络延迟
            page.goto(page_url, wait_until="commit", timeout=60000)
            
            # 修改 3：强制等待 15 秒给 JavaScript 运行时间，通常这时候授权地址就会出现了
            page.wait_for_timeout(15000) 
        except Exception as e:
            print(f"⚠️ [{name}] 访问提醒: {e}")
        
        browser.close()
    
    # 二次处理：如果是发号器地址，转为真实地址
    if found_url and "getLiveUrl" in found_url and "wsSecret" not in found_url:
        import requests
        try:
            res = requests.get(found_url, timeout=10)
            match = re.search(r'https?://[^\s\'"]+\.m3u8\?[^\s\'"]+', res.text)
            if match: found_url = match.group(0)
        except: pass

    if found_url:
        print(f"✅ [{name}] 抓取成功: {found_url[:50]}...")
        return found_url
    else:
        print(f"❌ [{name}] 未能截获授权地址，保持原样")
        return page_url

def main():
    file_path = "TWTV.m3u"
    if not os.path.exists(file_path): return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        for name, url in DYNAMIC_CHANNELS.items():
            if f'tvg-name="{name}"' in line or line.strip().endswith(f',{name}'):
                real_url = get_dynamic_url(name, url)
                new_lines.append(real_url + "\n")
                i += 1
                break
        i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    main()
