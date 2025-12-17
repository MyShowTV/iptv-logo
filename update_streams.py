import requests
import os
import re

# 成都台发号器接口（你提供的）
CHANNELS = {
    "成都新闻综合": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv1high%2FCDTV1High.flv%2Fplaylist.m3u8",
    "成都经济资讯": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv2high%2FCDTV2High.flv%2Fplaylist.m3u8",
    "成都都市生活": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv3high%2FCDTV3High.flv%2Fplaylist.m3u8",
    "成都影视文艺": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv4high%2FCDTV4High.flv%2Fplaylist.m3u8",
    "成都公共": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv5high%2FCDTV5High.flv%2Fplaylist.m3u8",
    "成都少儿": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv6high%2FCDTV6High.flv%2Fplaylist.m3u8"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://cditv.cn/"
}


def fetch_real_url(api_url):
    """访问发号器接口，提取真实 m3u8 地址"""
    try:
        res = requests.get(api_url, headers=HEADERS, timeout=10)

        # 优先尝试 JSON 格式
        try:
            data = res.json()
            if "data" in data and isinstance(data["data"], str) and data["data"].startswith("http"):
                return data["data"]
        except:
            pass

        # 如果不是 JSON，则尝试正则兜底
        text = res.text.replace("\\", "")
        match = re.search(r"https?://[^\s\"']+\.m3u8[^\s\"']*", text)
        if match:
            return match.group(0)

        return None

    except Exception as e:
        print("请求失败:", e)
        return None


def main():
    m3u_file = "TWTV.m3u"

    if not os.path.exists(m3u_file):
        print("错误：找不到 TWTV.m3u 文件")
        return

    with open(m3u_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    updated = 0
    i = 0
    total = len(lines)

    while i < total:
        line = lines[i]
        new_lines.append(line)

        # 检查是否匹配频道
        for name, api_url in CHANNELS.items():
            if f'tvg-name="{name}"' in line or line.strip().endswith(f",{name}"):

                print(f"\n正在更新：{name}")
                real_url = fetch_real_url(api_url)

                if real_url:
                    print(f"✅ 成功：{real_url}")
                    new_lines.append(real_url + "\n")
                    updated += 1
                else:
                    print("❌ 失败，保留旧地址")
                    new_lines.append(lines[i+1])

                i += 1
                break

        i += 1

    # 写回文件
    with open(m3u_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"\n✅ 更新完成，共更新 {updated} 个频道")


if __name__ == "__main__":
    main()
