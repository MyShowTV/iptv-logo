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
    print(f"🚀 正在通过 Playwright 抓取: {name}...")
    final_url = page_url
    
    with sync_playwright() as p:
        # 启动 Chromium (无头模式)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        # 核心逻辑：监听所有网络请求
        def handle_request(request):
            nonlocal final_url
            url = request.url
            # 优先寻找带授权参数的最终 m3u8
            if ".m3u8?" in url and "wsSecret=" in url:
                final_url = url
            # 备选：寻找发号器接口
            elif "getLiveUrl" in url and final_url == page_url:
                final_url = url

        page.on("request", handle_request)
        
        try:
            # 访问网页并等待网络空闲
            page.goto(page_url, wait_until="networkidle", timeout=30000)
            # 模拟点击播放（有时需要触发）
            page.wait_for_timeout(5000) 
        except Exception as e:
            print(f"⚠️ [{name}] 访问超时或出错: {e}")
        
        browser.close()
    
    # 如果抓到的是发号器 API，我们需要请求它获取最终地址
    if "getLiveUrl" in final_url and "wsSecret" not in final_url:
        import requests
        try:
            res = requests.get(final_url, timeout=10)
            match = re.search(r'https?://[^\s\'"]+\.m3u8\?[^\s\'"]+', res.text)
            if match: final_url = match.group(0)
        except: pass

    return final_url

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
                print(f"✅ {name} 更新完毕")
                break
        i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    main()
