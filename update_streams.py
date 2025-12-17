import requests
import re
import os

# 频道配置
CHANNELS_MAP = {
    "成都新闻综合": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv1high%2FCDTV1High.flv%2Fplaylist.m3u8",
    "成都经济资讯": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv2high%2FCDTV2High.flv%2Fplaylist.m3u8",
    "成都都市生活": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv3high%2FCDTV3High.flv%2Fplaylist.m3u8",
    "成都影视文艺": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv4high%2FCDTV4High.flv%2Fplaylist.m3u8",
    "成都公共": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv5high%2FCDTV5High.flv%2Fplaylist.m3u8",
    "成都少儿": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv6high%2FCDTV6High.flv%2Fplaylist.m3u8"
}

def get_new_ticket(name, api_url):
    # 模拟真实浏览器的请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://www.cditv.cn/',
        'Origin': 'https://www.cditv.cn',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    try:
        # 使用 verify=False 避免某些 SSL 证书问题
        res = requests.get(api_url, headers=headers, timeout=15, verify=True)
        
        # 打印调试信息（你在 Actions 日志里能看到回传了什么）
        print(f"DEBUG [{name}] 状态码: {res.status_code}")
        
        # 提取带 wsSecret 的地址
        # 兼容处理回传内容中可能的反斜杠转义
        text = res.text.replace('\\/', '/')
        match = re.search(r'https?://[^\s\'"]+\.m3u8\?[^\s\'"]+', text)
        
        if match:
            return match.group(0)
        else:
            print(f"DEBUG [{name}] 内容截断: {res.text[:100]}") # 没匹配到时看下回传的前100个字
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def main():
    file_path = "TWTV.m3u"
    if not os.path.exists(file_path): 
        print(f"找不到文件: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        updated = False
        for name, api_url in CHANNELS_MAP.items():
            if f'tvg-name="{name}"' in line or line.strip().endswith(f',{name}'):
                print(f"🔄 正在为 [{name}] 换取最新授权地址...")
                new_url = get_new_ticket(name, api_url)
                if new_url:
                    new_lines.append(new_url + "\n")
                    print(f"✅ 成功: {new_url[:60]}...")
                else:
                    if i + 1 < len(lines):
                        new_lines.append(lines[i+1])
                    print(f"❌ 失败: 未能在接口返回中找到有效流地址")
                i += 1
                updated = True
                break
        i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    main()
