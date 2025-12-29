"""
工具函数模块
"""

from datetime import datetime, timedelta
import pytz
import xml.etree.ElementTree as ET


def parse_opml(opml_file):
    """
    解析OPML文件，提取公众号信息
    
    Args:
        opml_file: OPML文件路径
    
    Returns:
        公众号列表 [{"name": "公众号名", "rss_url": "RSS地址", "bid": "公众号ID"}]
    """
    tree = ET.parse(opml_file)
    root = tree.getroot()
    
    accounts = []
    for outline in root.findall('.//outline[@type="rss"]'):
        name = outline.get('text') or outline.get('title')
        rss_url = outline.get('xmlUrl')
        
        # 从RSS URL中提取bid
        # 格式: http://192.168.0.121:8081/feed/3074462761.xml
        bid = None
        if rss_url:
            parts = rss_url.split('/')
            if len(parts) > 0:
                filename = parts[-1]  # 3074462761.xml
                bid = filename.replace('.xml', '')  # 3074462761
        
        if name and rss_url and bid:
            accounts.append({
                "name": name,
                "rss_url": rss_url,
                "bid": bid
            })
    
    return accounts


def is_within_last_24_hours(pub_date_str):
    """
    判断文章发布时间是否在最近24小时内
    
    Args:
        pub_date_str: 发布时间字符串（RSS格式）
    
    Returns:
        bool: True表示在24小时内
    """
    try:
        # RSS常见时间格式：
        # "Wed, 28 Dec 2025 15:30:00 +0800"
        # "2025-12-28T15:30:00+08:00"
        
        # 尝试解析RFC 2822格式（RSS 2.0标准）
        try:
            from email.utils import parsedate_to_datetime
            pub_date = parsedate_to_datetime(pub_date_str)
        except:
            # 尝试ISO 8601格式
            pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
        
        # 获取当前时间（带时区）
        now = datetime.now(pytz.timezone('Asia/Shanghai'))
        
        # 确保pub_date有时区信息
        if pub_date.tzinfo is None:
            pub_date = pytz.timezone('Asia/Shanghai').localize(pub_date)
        else:
            # 转换到上海时区
            pub_date = pub_date.astimezone(pytz.timezone('Asia/Shanghai'))
        
        # 计算时间差
        time_diff = now - pub_date
        
        # 判断是否在24小时内
        return timedelta(hours=0) <= time_diff <= timedelta(hours=24)
        
    except Exception as e:
        print(f"⚠️  时间解析失败: {pub_date_str}, 错误: {e}")
        return False


def format_datetime(pub_date_str):
    """
    格式化时间为统一格式
    
    Args:
        pub_date_str: 发布时间字符串
    
    Returns:
        格式化后的时间字符串: "2025-12-28 15:30:00"
    """
    try:
        # 尝试解析
        try:
            from email.utils import parsedate_to_datetime
            pub_date = parsedate_to_datetime(pub_date_str)
        except:
            pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
        
        # 转换到上海时区
        if pub_date.tzinfo is None:
            pub_date = pytz.timezone('Asia/Shanghai').localize(pub_date)
        else:
            pub_date = pub_date.astimezone(pytz.timezone('Asia/Shanghai'))
        
        # 格式化
        return pub_date.strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception as e:
        print(f"⚠️  时间格式化失败: {pub_date_str}, 错误: {e}")
        return pub_date_str


def extract_bid_from_url(url):
    """
    从URL中提取公众号ID
    
    Args:
        url: RSS URL
    
    Returns:
        bid: 公众号ID
    """
    try:
        parts = url.split('/')
        filename = parts[-1]
        return filename.replace('.xml', '')
    except:
        return None


# 测试代码
if __name__ == "__main__":
    # 测试OPML解析
    print("测试OPML解析:")
    accounts = parse_opml("wechat2rss_subscriptions.opml")
    for acc in accounts:
        print(f"  - {acc['name']}: bid={acc['bid']}")
    
    print(f"\n共找到 {len(accounts)} 个公众号")
    
    # 测试时间判断
    print("\n测试时间判断:")
    test_times = [
        "Wed, 28 Dec 2024 15:30:00 +0800",  # 可能不在24小时内
        datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800"),  # 当前时间
    ]
    
    for t in test_times:
        result = is_within_last_24_hours(t)
        print(f"  {t} -> {result}")

