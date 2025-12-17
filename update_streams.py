import requests
import re
import os
import time

# ==========================================================
# 1. 频道配置清单
# 格式: "M3U文件里的频道名": "官方网页地址"
# 机器人会根据这里的名字去 TWTV.m3u 里找对应的位置并替换下一行网址
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
    """
    抓取核心逻辑：
    1. 访问网页寻找到 getLiveUrl 接口
    2. 请求接口换取带 wsSecret 和 wsTime 参数的真实流地址
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.cditv.cn/'
    }
    
    try:
        # 第一步：访问频道网页
        response = requests.get(page_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        # 寻找成都台特有的 getLiveUrl 接口地址
        # 匹配格式如: https://.../getLiveUrl?url=...
        api_match = re.search(r'https?://[^\s\'"]+getLiveUrl\?url=[^\s\'"]+', response.text)
        
        if api_match:
            api_url = api_match.group(0).replace('&amp;', '&')
            print(f"[{name}] 发现加密接口: {api_url[:60]}...")
            
            # 第二步：核心！向接口请求带通行证(wsSecret)的真实地址
            api_res = requests.get(api_url, headers=headers, timeout=10)
            # 匹配带参数的 m3u8 地址
            final_url_match = re.search(r'https?://[^\s\'"]+\.m3u8\?[^\s\'"]+', api_res.text)
            
            if final_url_match:
                real_url = final_url_match.group(0)
                print(f"✅ [{name}] 成功获取带通行证地址")
                return real_url

        # 通用匹配逻辑（针对龙华电影等普通网页）
        links = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', response.text)
        for link in links:
            if "getLiveUrl" not in link:
                print(f"✅ [{name}] 发现普通流地址")
                return link
                
        print(f"❌ [{name}] 未能在网页中解析到有效地址")
        return page_url # 没抓到则返回原始网页地址防止出错
        
    except Exception as e:
        print(f"❌ [{name}] 抓取过程中出错: {e}")
        return page_url

def main():
    file_path = "TWTV.m3u"
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"找不到文件: {file_path}")
        return

    # 读取旧的 M3U 内容
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    total_len = len(lines)
    update_count = 0

    while i < total_len:
        line = lines[i]
        new_lines.append(line)
        
        # 检查这一行是否包含我们配置的频道名
        matched = False
        for name, page_url in DYNAMIC_CHANNELS.items():
            # 匹配方式：tvg-name="频道名" 或者以 ,频道名 结尾
            if f'tvg-name="{name}"' in line or line.strip().endswith(f',{name}'):
                # 抓取最新真实地址
                real_url = get_real_url(name, page_url)
                # 写入新地址并换行
                new_lines.append(real_url + "\n")
                # 跳过旧 M3U 文件里的那行旧地址
                i += 1 
                update_count += 1
                matched = True
                break
        i += 1

    # 将更新后的内容写回文件
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    print(f"--- 任务结束：共检查 {len(DYNAMIC_CHANNELS)} 个频道，成功更新 {update_count} 个地址 ---")

if __name__ == "__main__":
    main()
