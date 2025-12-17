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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.cditv.cn/'
    }
    try:
        # 1. 访问频道网页获取 API 接口地址
        res = requests.get(page_url, headers=headers, timeout=10)
        # 匹配类似于 getLiveUrl?url=... 的接口地址
        api_match = re.search(r'https?://[^\s\'"]+getLiveUrl\?url=[^\s\'"]+', res.text)
        
        if api_match:
            api_url = api_match.group(0).replace('&amp;', '&')
            # 2. 核心步骤：请求接口以获得带 wsSecret 和 wsTime 的真实播放地址
            api_res = requests.get(api_url, headers=headers, timeout=10)
            # 从返回的结果中寻找带参数的 .m3u8
            final_url_match = re.search(r'https?://[^\s\'"]+\.m3u8\?[^\s\'"]+', api_res.text)
            if final_url_match:
                real_url = final_url_match.group(0)
                print(f"成功为 {name} 抓取到带授权参数的流地址")
                return real_url
        
        # 如果不是成都台这种特殊接口，尝试通用匹配（针对龙华电影等）
        links = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', res.text)
        for link in links:
            if "getLiveUrl" not in link: return link
            
        return page_url # 失败则返回原网页地址
    except Exception as e:
        print(f"解析 {name} 时发生错误: {e}")
        return page_url

def main():
    file_path = "TWTV.m3u"
    if not os.path.exists(file_path): 
        print(f"错误: 找不到 {file_path}")
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
            # 这里的匹配逻辑：如果当前行是配置中的频道信息行
            if f'tvg-name="{name}"' in line or line.strip().endswith(f',{name}'):
                real_url = get_real_url(name, page_url)
                new_lines.append(real_url + "\n")
                i += 1 # 跳过旧的地址行
                found = True
                break
        i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("M3U 文件同步完成")

if __name__ == "__main__":
    main()
