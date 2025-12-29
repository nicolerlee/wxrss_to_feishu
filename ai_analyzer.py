"""
AI分析模块 - 使用DeepSeek/Claude/OpenAI分析文章并生成报告
"""

import json
from datetime import datetime
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def load_prompt_template():
    """加载提示词模板"""
    prompt_path = Path(__file__).parent / "docs" / "prompts" / "analyze_prompt.md"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def prepare_articles_data(articles):
    """
    准备文章数据，转换为简洁的格式给AI
    
    Args:
        articles: 清洗后的文章列表
    
    Returns:
        格式化的JSON字符串
    """
    # 只给AI关键信息，节省token
    simplified = []
    for article in articles:
        # 优先使用Markdown格式，降级到纯文本
        content = article.get("content_markdown") or article.get("content_text", "")
        
        # 兼容不同的字段名（url 或 link）
        url = article.get("url") or article.get("link", "")
        
        simplified.append({
            "title": article.get("title", ""),
            "author": article.get("author", ""),
            "url": url,
            "publish_time": article.get("publish_time", ""),
            # 如果文章太长，只取前2000字
            "content": content[:2000] + "..." if len(content) > 2000 else content,
            "word_count": article.get("word_count", 0)
        })
    
    return json.dumps(simplified, ensure_ascii=False, indent=2)


def analyze_with_claude(articles, api_key):
    """
    使用Claude分析文章
    
    Args:
        articles: 清洗后的文章列表
        api_key: Claude API密钥
    
    Returns:
        分析报告的JSON数据
    """
    # 加载提示词模板
    prompt_template = load_prompt_template()
    
    # 准备数据
    articles_json = prepare_articles_data(articles)
    account_names = set([a["author"] for a in articles])
    
    # 替换模板变量
    prompt = prompt_template.replace("{article_count}", str(len(articles)))
    prompt = prompt.replace("{account_count}", str(len(account_names)))
    prompt = prompt.replace("{articles_data}", articles_json)
    
    # 调用Claude API
    client = Anthropic(api_key=api_key)
    
    print("正在调用Claude API分析...")
    print(f"文章数量: {len(articles)}")
    print(f"预计token数: ~{len(prompt)//4}")
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8000,
        temperature=0.7,  # 保持一定创造性
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    # 解析返回的JSON
    result_text = response.content[0].text
    
    # 清理可能的代码块标记
    result_text = result_text.strip()
    if result_text.startswith("```json"):
        result_text = result_text[7:]
    if result_text.startswith("```"):
        result_text = result_text[3:]
    if result_text.endswith("```"):
        result_text = result_text[:-3]
    result_text = result_text.strip()
    
    try:
        report = json.loads(result_text)
        print("✅ AI分析完成")
        return report
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        print(f"原始返回内容:\n{result_text}")
        raise


def analyze_with_deepseek(articles, api_key, base_url="https://api.deepseek.com", model="deepseek-chat"):
    """
    使用DeepSeek分析文章（推荐：便宜好用）
    
    Args:
        articles: 清洗后的文章列表
        api_key: DeepSeek API密钥
        base_url: API地址
        model: 模型名称
    
    Returns:
        分析报告的JSON数据
    """
    if OpenAI is None:
        raise ImportError("需要安装openai库: pip install openai")
    
    # 加载提示词模板
    prompt_template = load_prompt_template()
    
    # 准备数据
    articles_json = prepare_articles_data(articles)
    account_names = set([a["author"] for a in articles])
    
    # 替换模板变量
    prompt = prompt_template.replace("{article_count}", str(len(articles)))
    prompt = prompt.replace("{account_count}", str(len(account_names)))
    prompt = prompt.replace("{articles_data}", articles_json)
    
    # 调用DeepSeek API（兼容OpenAI格式）
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    print("🚀 正在调用DeepSeek API分析...")
    print(f"📊 文章数量: {len(articles)}")
    print(f"💰 预计token数: ~{len(prompt)//4}")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位资深的AI领域内容分析师和选题策划专家。请严格按照JSON格式返回分析结果。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=8000,
            response_format={"type": "json_object"}  # 强制JSON输出
        )
        
        # 解析返回的JSON
        result_text = response.choices[0].message.content
        
        try:
            report = json.loads(result_text)
            print("✅ DeepSeek分析完成")
            print(f"💰 Token使用: 输入{response.usage.prompt_tokens}, 输出{response.usage.completion_tokens}")
            return report
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"原始返回内容:\n{result_text[:500]}...")
            raise
            
    except Exception as e:
        print(f"❌ DeepSeek API调用失败: {e}")
        raise


def analyze_with_openai(articles, api_key, base_url="https://api.openai.com/v1", model="gpt-4o-mini"):
    """
    使用OpenAI分析文章（备选方案）
    
    Args:
        articles: 清洗后的文章列表
        api_key: OpenAI API密钥
        base_url: API地址（可用于代理）
        model: 模型名称
    
    Returns:
        分析报告的JSON数据
    """
    if OpenAI is None:
        raise ImportError("需要安装openai库: pip install openai")
    
    # 加载提示词模板
    prompt_template = load_prompt_template()
    
    # 准备数据
    articles_json = prepare_articles_data(articles)
    account_names = set([a["author"] for a in articles])
    
    # 替换模板变量
    prompt = prompt_template.replace("{article_count}", str(len(articles)))
    prompt = prompt.replace("{account_count}", str(len(account_names)))
    prompt = prompt.replace("{articles_data}", articles_json)
    
    # 调用OpenAI API
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    print("正在调用OpenAI API分析...")
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一位资深的AI内容分析师。请严格按照JSON格式返回结果。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=8000,
        response_format={"type": "json_object"}  # 强制JSON输出
    )
    
    # 解析返回的JSON
    result_text = response.choices[0].message.content
    
    try:
        report = json.loads(result_text)
        print("✅ AI分析完成")
        return report
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        print(f"原始返回内容:\n{result_text}")
        raise


def analyze_articles(articles, ai_provider="deepseek", api_key=None, **kwargs):
    """
    分析文章的统一入口
    
    Args:
        articles: 清洗后的文章列表
        ai_provider: "deepseek", "claude" 或 "openai"
        api_key: API密钥
        **kwargs: 额外参数（如base_url, model等）
    
    Returns:
        分析报告的JSON数据
    """
    if not articles:
        raise ValueError("文章列表为空，无法分析")
    
    if not api_key:
        raise ValueError("请提供API密钥")
    
    # 添加当前日期
    today = datetime.now().strftime("%Y-%m-%d")
    
    ai_provider = ai_provider.lower()
    
    if ai_provider == "deepseek":
        base_url = kwargs.get("base_url", "https://api.deepseek.com")
        model = kwargs.get("model", "deepseek-chat")
        report = analyze_with_deepseek(articles, api_key, base_url, model)
    elif ai_provider == "claude":
        if Anthropic is None:
            raise ImportError("需要安装anthropic库: pip install anthropic")
        report = analyze_with_claude(articles, api_key)
    elif ai_provider == "openai":
        base_url = kwargs.get("base_url", "https://api.openai.com/v1")
        model = kwargs.get("model", "gpt-4o-mini")
        report = analyze_with_openai(articles, api_key, base_url, model)
    else:
        raise ValueError(f"不支持的AI提供商: {ai_provider}. 支持: deepseek, claude, openai")
    
    # 确保日期字段正确
    report["date"] = today
    
    return report


# 测试代码
if __name__ == "__main__":
    # 模拟数据测试
    test_articles = [
        {
            "title": "AI工具实战：如何用ChatGPT提升工作效率10倍",
            "author": "陈老师AI进化论",
            "url": "http://example.com/1",
            "publish_time": "2025-12-28 10:00:00",
            "content_text": "最近很多朋友问我，ChatGPT到底怎么用才能真正提升效率...",
            "word_count": 2500
        },
        {
            "title": "N8N工作流实战：打造个人AI助手",
            "author": "ai瑞斯白-n8n版",
            "url": "http://example.com/2",
            "publish_time": "2025-12-28 15:30:00",
            "content_text": "今天教大家用N8N搭建一个智能助手...",
            "word_count": 3200
        }
    ]
    
    # 需要设置你的API Key
    API_KEY = "your_api_key_here"
    
    try:
        report = analyze_articles(test_articles, ai_provider="claude", api_key=API_KEY)
        print("\n" + "="*50)
        print("分析报告:")
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"测试失败: {e}")

