import requests
import re
import os

# ==========================================================
# 频道清单
# ==========================================================
DYNAMIC_CHANNELS = {
    "成都新闻综合": "https://www.cditv.cn/show/4845-563.html",
    "成都经济资讯": "https://www.cditv.cn/show/4845-562.html", 
    "成都都市生活": "https://www.cditv.cn/show/4845-561.html",
    "成都影视文艺": "https://www.cditv.cn/show/4845-560.html",
    "成都公共": "https://www.cditv.cn/show/4845-559.html",
    "成都少儿": "https://www.cditv.cn/show/4845-558.html",
    "成都高新台": "https://www.cditv.cn/show/4845-591.html",
    "龙华电影": "https://www.ofiii.com/channel/watch/litv-longturn03",
}

def get_real_url(name, page_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        # 1. 访问频道网页
        res = requests.get(page_url, headers=headers, timeout=10)
        # 2. 寻找 getLiveUrl 接口
        api_match = re.search(r'https?://[^\s\'"]+getLiveUrl\?url=[^\s\'"]+', res.text)
        
        if api_match:
            api_url = api_match.group(0).replace('&amp;', '&')
            # 3. 访问接口获取最终带 Token 的 m3u8
            api_res = requests.get(api_url, headers=headers, timeout=10)
            final_url_match = re.search(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', api_res.text)
            if final_url_match:
                return final_url_match.group(0)
        
        # 如果不是成都台这种接口，尝试通用匹配（针对龙华电影等）
        links = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', res.text)
        for link in links:
            if "getLiveUrl" not in link: return link
            
        return page_url # 实在抓不到就返回原地址
    except:
        return page_url

def main():
    file_path = "TWTV.m3u"
    if not os.path.exists(file_path): 
        print("找不到 TWTV.m3u 檔案")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        found = False
        for name, page_url in DYNAMIC_CHANNELS.items():
            if f'tvg-name="{name}"' in line or line.strip().endswith(f',{name}'):
                print(f"正在更新: {name}")
                real_url = get_real_url(name, page_url)
                new_lines.append(real_url + "\n")
                i += 1 
                found = True
                break
        i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    main()
