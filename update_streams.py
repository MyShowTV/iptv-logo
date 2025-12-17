import requests
import re
import os
import urllib.parse

# ==========================================================
# 频道清单 (请确保名字与 TWTV.m3u 里的名称完全一致)
# ==========================================================
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://www.cditv.cn/',
        'Origin': 'https://www.cditv.cn'
    }
    try:
        # 1. 获取网页内容
        res = requests.get(page_url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        # 关键处理：去掉所有的反斜杠干扰，把内容拉平
        content = res.text.replace('\\', '')

        # 2. 定位“发号器”接口
        # 只要包含 getLiveUrl?url= 的内容，全部抓出来
        api_pattern = r'(https?://[^\s\'"]+getLiveUrl\?url=[^\s\'"]+)'
        api_match = re.search(api_pattern, content)
        
        if api_match:
            # 清理 URL (处理 HTML 实体如 &amp;)
            api_url = api_match.group(0).split('"')[0].split("'")[0]
            api_url = urllib.parse.unquote(api_url).replace('&amp;', '&')
            print(f"🔍 [{name}] 成功定位发号器: {api_url[:60]}...")
            
            # 3. 访问发号器，获取带 wsSecret 的最终播放地址
            api_res = requests.get(api_url, headers=headers, timeout=10)
            # 在返回的内容中寻找 .m3u8?wsSecret=...
            final_match = re.search(r'(https?://[^\s\'"]+\.m3u8\?[^\s\'"]+)', api_res.text.replace('\\', ''))
            
            if final_match:
                real_url = final_match.group(0).split('"')[0].split("'")[0]
                print(f"✅ [{name}] 授权地址获取成功！")
                return real_url
        
        # 4. 兜底逻辑：如果接口失效，寻找普通地址
        normal_match = re.search(r'(https?://[^\s\'"]+\.m3u8)', content)
        if normal_match:
            print(f"⚠️ [{name}] 未能通过接口授权，回退到普通地址")
            return normal_match.group(0)

        print(f"❌ [{name}] 网页中未发现任何有效流地址")
        return page_url
    except Exception as e:
        print(f"❌ [{name}] 运行异常: {e}")
        return page_url

def main():
    file_path = "TWTV.m3u"
    if not os.path.exists(file_path): 
        print(f"错误: 找不到文件 {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    total = len(lines)
    success_count = 0

    while i < total:
        line = lines[i]
        new_lines.append(line)
        
        # 频道名匹配
        matched = False
        for name, page_url in DYNAMIC_CHANNELS.items():
            if f'tvg-name="{name}"' in line or line.strip().endswith(f',{name}'):
                real_url = get_real_url(name, page_url)
                new_lines.append(real_url + "\n")
                i += 1 
                success_count += 1
                matched = True
                break
        i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"\n--- 任务完成：成功更新了 {success_count} 个成都频道 ---")

if __name__ == "__main__":
    main()
