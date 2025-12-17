import requests
import re
import os

# 1. 钥匙清单：每个频道对应的 API 获取地址（发号器）
# 这些地址是固定的，但换出来的 m3u8 是带过期参数的
CHANNELS_MAP = {
    "成都新闻综合": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv1high%2FCDTV1High.flv%2Fplaylist.m3u8",
    "成都经济资讯": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv2high%2FCDTV2High.flv%2Fplaylist.m3u8",
    "成都都市生活": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv3high%2FCDTV3High.flv%2Fplaylist.m3u8",
    "成都影视文艺": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv4high%2FCDTV4High.flv%2Fplaylist.m3u8",
    "成都公共": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv5high%2FCDTV5High.flv%2Fplaylist.m3u8",
    "成都少儿": "https://cstvweb.cdmp.candocloud.cn/live/getLiveUrl?url=https%3A%2F%2Fcdn1.cditv.cn%2Fcdtv6high%2FCDTV6High.flv%2Fplaylist.m3u8"
}

def get_new_ticket(name, api_url):
    # 模拟真实播放器的请求头，防止 403 屏蔽
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://www.cditv.cn/',
        'Origin': 'https://www.cditv.cn',
        'Accept': '*/*'
    }
    try:
        # 禁用 SSL 警告并请求接口
        response = requests.get(api_url, headers=headers, timeout=15, verify=False)
        
        # 打印状态码辅助排查
        print(f"[{name}] 状态码: {response.status_code}")
        
        # 处理返回内容中的转义斜杠
        clean_text = response.text.replace('\\/', '/')
        
        # 正则匹配带参数的最终 m3u8 地址
        match = re.search(r'https?://[^\s\'"]+\.m3u8\?[^\s\'"]+', clean_text)
        
        if match:
            return match.group(0).split('"')[0].split("'")[0]
        else:
            print(f"DEBUG [{name}] 接口未返回有效授权链接。返回内容：{response.text[:100]}")
            return None
    except Exception as e:
        print(f"❌ [{name}] 请求失败: {e}")
        return None

def main():
    file_path = "TWTV.m3u"
    if not os.path.exists(file_path):
        print(f"错误: 找不到文件 {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    total_lines = len(lines)
    success_count = 0

    while i < total_lines:
        line = lines[i]
        new_lines.append(line)
        
        # 检测是否是我们要更新的频道
        for name, api_url in CHANNELS_MAP.items():
            if f'tvg-name="{name}"' in line or line.strip().endswith(f',{name}'):
                print(f"🔄 正在换取 [{name}] 的最新授权...")
                new_url = get_new_ticket(name, api_url)
                
                if new_url:
                    new_lines.append(new_url + "\n")
                    success_count += 1
                    print(f"✅ 获取成功")
                else:
                    # 失败则保留 M3U 中的原有地址行（下一行）
                    if i + 1 < total_lines:
                        new_lines.append(lines[i+1])
                    print(f"❌ 获取失败")
                
                i += 1 # 跳过旧的地址行
                break
        i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    print(f"\n--- 处理完成：成功更新 {success_count} 个频道 ---")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings() # 隐藏不安全的请求警告
    main()
