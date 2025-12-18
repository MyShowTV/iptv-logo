import requests
import re

# 定义频道名和对应的 API
channels = {
    "成都新闻综合": "https://www.cditv.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv1high%2FCDTV1High.flv%2Fplaylist.m3u8",
    "成都经济资讯": "https://www.cditv.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv2high%2FCDTV2High.flv%2Fplaylist.m3u8",
    "成都公共": "https://www.cditv.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv5high%2FCDTV5High.flv%2Fplaylist.m3u8"
}

def get_real_url(api):
    headers = {"Referer": "https://www.cditv.cn/", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(api, headers=headers, timeout=10)
        match = re.search(r'https?://[^\s\'"]+\.m3u8\?[^\s\'"]+', r.text.replace('\\/', '/'))
        return match.group(0) if match else None
    except:
        return None

m3u_content = "#EXTM3U\n"
for name, api in channels.items():
    real_url = get_real_url(api)
    if real_url:
        m3u_content += f'#EXTINF:-1 tvg-name="{name}",{name}\n{real_url}\n'

with open("cdtv.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)
