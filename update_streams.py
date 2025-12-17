import requests
import re
import os
import urllib.parse

# 频道清单 (确保名字与 M3U 完全一致)
DYNAMIC_CHANNELS = {
    "成都新闻综合": "https://www.cditv.cn/show/4845-563.html",
    "成都经济资讯": "https://www.cditv.cn/show/4845-562.html", 
    "成都都市生活": "https://www.cditv.cn/show/4845-561.html",
    "成都影视文艺": "https://www.cditv.cn/show/4845-560.html",
    "成都公共": "https://www.cditv.cn/show/4845-559.html",
    "成都少儿": "https://www.cditv.cn/show/4845-558.html",
    "成都高新台": "https://www.cditv.cn/show/4845-591.html"
}

def get_real_url(name, page_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.cditv.cn/'
    }
    try:
        # 1. 获取网页内容
        res = requests.get(page_url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        content = res.text

        # 2. 寻找成都台的核心接口 (getLiveUrl)
        # 即使地址被转义（如 \/ 或 &amp;），我们也要把它找出来
        api_pattern = r'(https?://[^\s\'"]+getLiveUrl\?url=[^\s\'"]+)'
        api_match = re.search(api_pattern, content.replace('\\/', '/'))
        
        if api_match:
            api_url = api_match.group(0).replace('&amp;', '&')
            # 3. 请求接口换取带 wsSecret 的真实播放地址
            api_res = requests.get(api_url, headers=headers, timeout=10)
            # 在返回的 JSON 或文本中寻找真正的 m3u8
            final_match = re.search(r'(https?://[^\s\'"]+\.m3u8\?[^\s\'"]+)', api_res.text)
            if final_match:
                print(f"✅ [{name}] 成功抓取授权地址")
                return final_match.group(0)
        
        # 4. 如果没找到接口，才降级寻找普通地址
        normal_match = re.search(r'(https?://[^\s\'"]+\.m3u8)', content)
        if normal_match:
            print(f"⚠️ [{name}] 仅发现普通流地址(可能无法播放)")
            return normal_match.group(0)

        return page_url
    except Exception as e:
        print(f"❌ [{name}] 错误: {e}")
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
        for name, page_url in DYNAMIC_CHANNELS.items():
            if f'tvg-name="{name}"' in line or line.strip().endswith(f',{name}'):
                real_url = get_real_url(name, page_url)
                new_lines.append(real_url + "\n")
                i += 1 
                break
        i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("--- 同步结束 ---")

if __name__ == "__main__":
    main()
