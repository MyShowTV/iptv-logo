import requests
import re
import os

# ==========================================================
# 在這裡添加你想自動抓取的頻道。
# 注意：名稱必須和你 TWTV.m3u 裡的頻道名稱（逗號後面的字）一模一樣。
# ==========================================================
DYNAMIC_CHANNELS = {
    "成都综合": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv1high%2FCDTV1High.flv%2Fplaylist.m3u8",
    "龙华电影": "https://www.ofiii.com/channel/watch/litv-longturn03",
}

def get_real_url(name, api_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(api_url, headers=headers, timeout=15)
        # 尋找內容中的 m3u8 地址
        links = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', res.text)
        for link in links:
            if "getLiveUrl" not in link: return link
        return api_url
    except:
        return api_url

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
        
        # 判斷這一行是不是我們要更新的頻道
        found = False
        for name, api_url in DYNAMIC_CHANNELS.items():
            # 匹配 tvg-name="頻道名" 或以 ,頻道名 結尾
            if f'tvg-name="{name}"' in line or line.strip().endswith(f',{name}'):
                print(f"正在更新: {name}")
                real_url = get_real_url(name, api_url)
                new_lines.append(real_url + "\n")
                i += 1 # 跳過舊檔案中的舊網址
                found = True
                break
        i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    main()
