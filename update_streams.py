import requests
import re
import os

# 配置你想更新的频道和对应的“钥匙”(API地址)
# 这样即使 M3U 里的地址变了，脚本依然知道去哪里换票
CHANNELS_MAP = {
    "成都新闻综合": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv1high%2FCDTV1High.flv%2Fplaylist.m3u8",
    "成都经济资讯": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv2high%2FCDTV2High.flv%2Fplaylist.m3u8",
    "成都都市生活": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv3high%2FCDTV3High.flv%2Fplaylist.m3u8",
    "成都影视文艺": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv4high%2FCDTV4High.flv%2Fplaylist.m3u8",
    "成都公共": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv5high%2FCDTV5High.flv%2Fplaylist.m3u8",
    "成都少儿": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv6high%2FCDTV6High.flv%2Fplaylist.m3u8"
}

def get_new_ticket(api_url):
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.cditv.cn/'}
    try:
        res = requests.get(api_url, headers=headers, timeout=10)
        # 提取带 wsSecret 的地址
        match = re.search(r'https?://[^\s\'"]+\.m3u8\?[^\s\'"]+', res.text)
        if match:
            return match.group(0).replace('\\/', '/')
    except:
        return None
    return None

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
        
        # 寻找频道名
        for name, api_url in CHANNELS_MAP.items():
            if f'tvg-name="{name}"' in line or line.strip().endswith(f',{name}'):
                print(f"🔄 正在为 [{name}] 领新门票...")
                new_ticket = get_new_ticket(api_url)
                if new_ticket:
                    new_lines.append(new_ticket + "\n")
                    print("✅ 领票成功")
                else:
                    if i + 1 < len(lines): new_lines.append(lines[i+1])
                    print("❌ 领票失败，保留旧地址")
                i += 1 # 跳过旧地址行
                break
        i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    main()
