"""
数据清洗模块 V2 - 使用Markdown格式（推荐）
"""

from bs4 import BeautifulSoup
import markdownify
import re


def clean_html_to_markdown(html_content, keep_images='full'):
    """
    将HTML清洗并转换为Markdown格式
    
    Args:
        html_content: HTML内容
        keep_images: 图片处理策略
            - 'full': 保留完整图片链接（默认）
            - 'simplified': 简化为[图片N]
            - 'remove': 完全移除图片
    
    Returns:
        Markdown格式的文本
    """
    if not html_content:
        return ""
    
    try:
        # 步骤1：用BeautifulSoup清理垃圾标签
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除script、style、iframe等无用标签
        for tag in soup(['script', 'style', 'iframe', 'noscript']):
            tag.decompose()
        
        # 步骤2：转换为Markdown
        markdown = markdownify.markdownify(
            str(soup),
            heading_style='ATX',        # 使用 # 风格的标题
            bullets='*',                 # 使用 * 作为列表符号
            strip=['a'],                 # 可选：移除链接但保留文本
        )
        
        # 步骤3：处理图片
        if keep_images == 'remove':
            # 完全移除图片
            markdown = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', markdown)
        elif keep_images == 'simplified':
            # 简化为[图片N]
            img_count = 0
            def replace_img(match):
                nonlocal img_count
                img_count += 1
                return f'[图片{img_count}]'
            markdown = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', replace_img, markdown)
        # else: keep_images == 'full', 保持原样
        
        # 步骤4：清理多余的空行
        lines = markdown.split('\n')
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            is_empty = not line.strip()
            # 最多保留一个空行
            if is_empty:
                if not prev_empty:
                    cleaned_lines.append(line)
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False
        
        return '\n'.join(cleaned_lines).strip()
        
    except Exception as e:
        print(f"⚠️  HTML转Markdown失败: {e}")
        # 降级处理：直接去除HTML标签
        return re.sub(r'<[^>]+>', '', html_content)


def remove_ads_markdown(markdown_text):
    """
    从Markdown文本中去除广告内容
    
    Args:
        markdown_text: Markdown文本
    
    Returns:
        去除广告后的Markdown文本
    """
    # 广告关键词列表
    ad_keywords = [
        '扫码关注', '长按二维码', '识别二维码', '关注公众号',
        '点击阅读原文', '阅读原文', '原文链接',
        '限时优惠', '限时特惠', '报名链接', '点击报名',
        '加微信', '添加微信', '微信咨询',
        '推广', '广告', '赞助',
        '转发朋友圈', '分享到朋友圈',
        '点击购买', '立即购买', '马上购买',
        '课程链接', '购买链接',
        '跳转微信打开',  # RSS特有的
    ]
    
    # 按行处理
    lines = markdown_text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # 检查是否包含广告关键词
        has_ad = False
        for keyword in ad_keywords:
            if keyword in line:
                has_ad = True
                break
        
        # 检查是否是微信号/电话号码
        if re.search(r'微信[：:]\s*[a-zA-Z0-9_-]+', line):
            has_ad = True
        if re.search(r'电话[：:]\s*\d{11}', line):
            has_ad = True
        
        # 过滤图片链接（可选）
        # if line.strip().startswith('![](') and 'img-proxy' in line:
        #     has_ad = True
        
        # 如果不是广告，保留这一行
        if not has_ad:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def calculate_word_count_markdown(markdown_text):
    """
    计算Markdown文本的字数（去除Markdown标记）
    
    Args:
        markdown_text: Markdown文本
    
    Returns:
        字数
    """
    if not markdown_text:
        return 0
    
    # 移除Markdown标记
    # 移除标题标记 (# ## ###)
    text = re.sub(r'^#+\s+', '', markdown_text, flags=re.MULTILINE)
    
    # 移除加粗/斜体标记 (** __ * _)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # 移除链接 [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # 移除图片 ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
    
    # 移除列表标记 (* - 1.)
    text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # 移除引用标记 (>)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # 移除代码块标记 (```)
    text = re.sub(r'```[^\n]*\n.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # 去除所有空白字符后统计
    text_no_space = re.sub(r'\s+', '', text)
    return len(text_no_space)


def deduplicate_articles(articles):
    """
    去重（基于URL和标题）
    
    Args:
        articles: 文章列表
    
    Returns:
        去重后的文章列表
    """
    seen = set()
    unique_articles = []
    
    for article in articles:
        # 使用 URL 或 (author, title) 组合作为唯一键
        key = article.get('url', '')
        if not key:
            key = (article.get('author', ''), article.get('title', ''))
        
        if key not in seen:
            seen.add(key)
            unique_articles.append(article)
    
    duplicate_count = len(articles) - len(unique_articles)
    if duplicate_count > 0:
        print(f"   🔄 去重: 移除 {duplicate_count} 篇重复文章")
    
    return unique_articles


def filter_low_quality(articles, min_word_count=500):
    """
    过滤低质量文章
    
    Args:
        articles: 文章列表
        min_word_count: 最小字数
    
    Returns:
        过滤后的文章列表
    """
    filtered = []
    removed_count = 0
    
    for article in articles:
        # 检查字数
        if article.get('word_count', 0) < min_word_count:
            removed_count += 1
            continue
        
        # 检查标题
        title = article.get('title', '').lower()
        if '测试' in title or 'test' in title:
            removed_count += 1
            continue
        
        # 检查内容是否为空
        content = article.get('content_markdown', '')
        if not content or len(content.strip()) < 100:
            removed_count += 1
            continue
        
        filtered.append(article)
    
    if removed_count > 0:
        print(f"   🗑️  过滤: 移除 {removed_count} 篇低质量文章")
    
    return filtered


def clean_articles_v2(articles, min_word_count=500):
    """
    清洗文章数据的主函数（Markdown版本）
    
    Args:
        articles: 原始文章列表
        min_word_count: 最小字数阈值
    
    Returns:
        清洗后的文章列表（包含Markdown格式）
    """
    print("\n" + "=" * 60)
    print("🧹 开始清洗数据（Markdown格式）")
    print("=" * 60)
    
    print(f"\n原始文章数: {len(articles)}")
    
    # 1. 转换为Markdown并去除广告
    print("\n1️⃣  转换为Markdown格式...")
    for article in articles:
        # 转换HTML为Markdown
        html_content = article.get('content_html', '')
        markdown = clean_html_to_markdown(html_content)
        
        # 去除广告
        markdown = remove_ads_markdown(markdown)
        
        # 保存Markdown
        article['content_markdown'] = markdown
        
        # 计算字数
        article['word_count'] = calculate_word_count_markdown(markdown)
        
        # 处理摘要
        if not article.get('summary'):
            # 如果没有摘要，取前200字（去除Markdown标记）
            plain_text = re.sub(r'[#*_\[\]()>]', '', markdown)
            article['summary'] = plain_text[:200] + '...' if len(plain_text) > 200 else plain_text
    
    print(f"   ✅ Markdown转换完成")
    
    # 2. 去重
    print("\n2️⃣  去除重复文章...")
    articles = deduplicate_articles(articles)
    print(f"   ✅ 当前文章数: {len(articles)}")
    
    # 3. 过滤低质量
    print(f"\n3️⃣  过滤低质量文章（最小字数: {min_word_count}）...")
    articles = filter_low_quality(articles, min_word_count)
    print(f"   ✅ 当前文章数: {len(articles)}")
    
    # 4. 统计
    print("\n" + "=" * 60)
    print("✅ 数据清洗完成！")
    print(f"   最终文章数: {len(articles)}")
    
    if articles:
        total_words = sum(a['word_count'] for a in articles)
        avg_words = total_words // len(articles)
        print(f"   平均字数: {avg_words}")
        print(f"   字数范围: {min(a['word_count'] for a in articles)} - {max(a['word_count'] for a in articles)}")
    
    return articles


# 测试代码
if __name__ == "__main__":
    print("测试HTML → Markdown转换:")
    test_html = """
    <div class="article">
        <h1>AI工具教程</h1>
        <p>这是一段<strong>重要</strong>的内容。</p>
        <ul>
            <li>Claude：最强的AI助手</li>
            <li>GPT-4：OpenAI的旗舰模型</li>
        </ul>
        <script>console.log('should be removed')</script>
        <p>扫码关注我们的公众号</p>
        <p>微信：test123456</p>
        <p>这是正常内容。</p>
    </div>
    """
    
    markdown = clean_html_to_markdown(test_html)
    markdown = remove_ads_markdown(markdown)
    
    print(markdown)
    print(f"\n字数: {calculate_word_count_markdown(markdown)}")

