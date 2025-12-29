"""
RSS爬取模块 - 从RSS源获取文章
"""

import feedparser
import requests
from datetime import datetime
from utils import parse_opml, is_within_last_24_hours, format_datetime


def fetch_rss_feed(rss_url, timeout=10):
    """
    获取单个RSS源的内容
    
    Args:
        rss_url: RSS源地址
        timeout: 超时时间（秒）
    
    Returns:
        feedparser解析后的对象
    """
    try:
        # 使用requests先获取内容（更好的错误处理）
        response = requests.get(rss_url, timeout=timeout)
        response.raise_for_status()
        
        # 使用feedparser解析
        feed = feedparser.parse(response.content)
        return feed
        
    except requests.RequestException as e:
        print(f"❌ 获取RSS失败: {rss_url}")
        print(f"   错误: {e}")
        return None
    except Exception as e:
        print(f"❌ 解析RSS失败: {rss_url}")
        print(f"   错误: {e}")
        return None


def extract_articles_from_feed(feed, account_name):
    """
    从feed对象中提取文章信息
    
    Args:
        feed: feedparser解析后的对象
        account_name: 公众号名称
    
    Returns:
        文章列表
    """
    articles = []
    
    if not feed or not hasattr(feed, 'entries'):
        return articles
    
    for entry in feed.entries:
        try:
            # 提取基本信息
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            
            # 提取发布时间
            pub_date_str = entry.get('published', '') or entry.get('updated', '')
            
            # 提取内容（尝试多个可能的字段）
            content_html = ''
            if hasattr(entry, 'content') and len(entry.content) > 0:
                content_html = entry.content[0].get('value', '')
            elif hasattr(entry, 'summary'):
                content_html = entry.summary
            elif hasattr(entry, 'description'):
                content_html = entry.description
            
            # 提取摘要
            summary = entry.get('summary', '')
            
            # 构造文章对象
            article = {
                'title': title,
                'author': account_name,
                'url': link,
                'publish_time_raw': pub_date_str,
                'publish_time': format_datetime(pub_date_str) if pub_date_str else '',
                'content_html': content_html,
                'summary': summary
            }
            
            articles.append(article)
            
        except Exception as e:
            print(f"⚠️  解析文章失败: {entry.get('title', 'Unknown')}")
            print(f"   错误: {e}")
            continue
    
    return articles


def fetch_rss_articles(opml_file='wechat2rss_subscriptions.opml', filter_24h=True):
    """
    从OPML中的所有RSS源获取文章
    
    Args:
        opml_file: OPML文件路径
        filter_24h: 是否只获取24小时内的文章
    
    Returns:
        所有文章列表
    """
    print("=" * 60)
    print("🚀 开始爬取RSS文章")
    print("=" * 60)
    
    # 1. 解析OPML获取公众号列表
    print("\n📋 解析OPML文件...")
    accounts = parse_opml(opml_file)
    print(f"✅ 找到 {len(accounts)} 个公众号")
    
    # 2. 遍历每个公众号，获取文章
    all_articles = []
    
    for i, account in enumerate(accounts, 1):
        print(f"\n[{i}/{len(accounts)}] 正在爬取: {account['name']}")
        print(f"   RSS: {account['rss_url']}")
        
        # 获取RSS内容
        feed = fetch_rss_feed(account['rss_url'])
        
        if not feed:
            print(f"   ⚠️  跳过")
            continue
        
        # 提取文章
        articles = extract_articles_from_feed(feed, account['name'])
        print(f"   📄 获取到 {len(articles)} 篇文章")
        
        # 过滤24小时内的文章
        if filter_24h:
            filtered_articles = []
            for article in articles:
                if article['publish_time_raw'] and is_within_last_24_hours(article['publish_time_raw']):
                    filtered_articles.append(article)
            
            print(f"   ⏰ 24小时内: {len(filtered_articles)} 篇")
            all_articles.extend(filtered_articles)
        else:
            all_articles.extend(articles)
    
    # 3. 统计
    print("\n" + "=" * 60)
    print(f"✅ 爬取完成！")
    print(f"   总文章数: {len(all_articles)}")
    
    # 按时间排序（最新的在前）
    all_articles.sort(key=lambda x: x['publish_time_raw'], reverse=True)
    
    return all_articles


# 测试代码
if __name__ == "__main__":
    # 测试爬取
    articles = fetch_rss_articles(
        opml_file='wechat2rss_subscriptions.opml',
        filter_24h=True  # 只获取24小时内的
    )
    
    # 显示前3篇
    print("\n" + "=" * 60)
    print("📰 最新文章预览:")
    print("=" * 60)
    
    for i, article in enumerate(articles[:3], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   作者: {article['author']}")
        print(f"   时间: {article['publish_time']}")
        print(f"   链接: {article['url']}")
        print(f"   内容长度: {len(article['content_html'])} 字符")
        
        # 显示内容前200字符
        if article['content_html']:
            preview = article['content_html'][:200].replace('\n', ' ')
            print(f"   内容预览: {preview}...")

