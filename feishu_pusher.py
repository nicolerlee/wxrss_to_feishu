#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
飞书推送模块
功能：将AI分析报告推送到飞书群
"""

import requests
import json
from datetime import datetime
from pathlib import Path


def get_tenant_access_token(app_id, app_secret):
    """
    获取tenant_access_token
    """
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    
    print(f"📡 正在获取 tenant_access_token...")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        
        if result.get("code") != 0:
            print(f"❌ 获取 tenant_access_token 失败: {result}")
            raise Exception(f"Failed to get tenant_access_token: {result.get('msg')}")
        
        print(f"✅ 获取 tenant_access_token 成功")
        return result["tenant_access_token"]
    
    except Exception as e:
        print(f"❌ 获取 tenant_access_token 时发生错误: {e}")
        raise


def send_message_to_group(tenant_access_token, chat_id, msg_type, content):
    """
    向飞书群发送消息
    
    参数:
        tenant_access_token: 访问令牌
        chat_id: 群ID
        msg_type: 消息类型 (text, post, interactive等)
        content: 消息内容(字符串格式的JSON)
    """
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    
    payload = {
        "receive_id": chat_id,
        "msg_type": msg_type,
        "content": content
    }
    
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    print(f"📤 正在发送消息到群聊 (chat_id: {chat_id})...")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        
        if result.get("code") != 0:
            print(f"❌ 发送消息失败: {result}")
            raise Exception(f"Failed to send message: {result.get('msg')}")
        
        message_data = result.get("data", {})
        print(f"✅ 消息发送成功!")
        print(f"   Message ID: {message_data.get('message_id')}")
        print(f"   Create Time: {message_data.get('create_time')}")
        
        return message_data
    
    except Exception as e:
        print(f"❌ 发送消息时发生错误: {e}")
        raise


# ==================== 卡片元素构建辅助函数 ====================

def create_markdown_element(content):
    """创建Markdown文本元素"""
    return {
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": content
        }
    }


def create_plain_text_element(content):
    """创建纯文本元素"""
    return {
        "tag": "div",
        "text": {
            "tag": "plain_text",
            "content": content
        }
    }


def create_hr_element():
    """创建分割线元素"""
    return {"tag": "hr"}


def build_overview_section(statistics):
    """构建今日概览部分"""
    lines = [
        "📊 **今日概览**",
        f"• 分析文章数: {statistics.get('total_articles', 0)}",
        f"• 订阅账号数: {statistics.get('accounts_count', 0)}",
    ]
    return create_markdown_element("\n".join(lines))


def build_inspiration_section(inspirations):
    """构建选题灵感部分"""
    if not inspirations:
        return []
    
    elements = [
        create_markdown_element("💡 **选题灵感**")
    ]
    
    for i, topic in enumerate(inspirations, 1):
        lines = [
            f"**{i}. {topic.get('title', '')}**",
            f"📐 角度: {topic.get('angle', '')}",
            f"🎯 目标: {topic.get('target', '')}",
            f"💎 价值: {topic.get('value', '')}",
        ]
        
        # 添加参考文章
        references = topic.get('references', [])
        if references:
            lines.append("")
            lines.append("📚 参考文章:")
            for article in references:
                article_title = article.get('article_title', '文章')
                article_url = article.get('url', '')
                source = article.get('source', '')
                lines.append(f"• [{article_title}]({article_url}) ({source})")
        
        elements.append(create_markdown_element("\n".join(lines)))
    
    return elements


def build_deep_reading_section(deep_reading):
    """构建深度阅读推荐部分"""
    if not deep_reading:
        return []
    
    elements = [
        create_markdown_element("📚 **深度阅读推荐**")
    ]
    
    for i, article in enumerate(deep_reading, 1):
        article_title = article.get('article_title', '文章')
        article_url = article.get('article_url', '')
        source = article.get('source', '')
        score = article.get('score', 0)
        recommendation = article.get('recommendation', '')
        value_point = article.get('value_point', '')
        
        lines = [
            f"**{i}. [{article_title}]({article_url})**",
            f"👤 作者: {source} | ⭐ 评分: {score}",
            f"💬 推荐理由: {recommendation}",
        ]
        
        if value_point:
            lines.append(f"💡 核心价值: {value_point}")
        
        # 添加符合的标准
        meets_criteria = article.get('meets_criteria', [])
        if meets_criteria:
            lines.append("")
            lines.append("✅ 符合标准:")
            for criterion in meets_criteria:
                lines.append(f"  ✓ {criterion}")
        
        elements.append(create_markdown_element("\n".join(lines)))
    
    return elements


def build_hot_topics_section(hot_topics):
    """构建热点话题部分"""
    if not hot_topics:
        return []
    
    elements = [
        create_markdown_element("🔥 **本周热点话题**")
    ]
    
    for i, topic in enumerate(hot_topics, 1):
        topic_name = topic.get('topic_name', '')
        heat_level = topic.get('heat_level', '')
        mention_count = topic.get('mention_count', 0)
        analysis = topic.get('analysis', '')
        
        lines = [
            f"**{i}. {topic_name}**",
            f"🔥 热度: {heat_level} | 💬 讨论次数: {mention_count}",
            f"📊 分析: {analysis}",
        ]
        
        elements.append(create_markdown_element("\n".join(lines)))
    
    return elements


def build_footer_section():
    """构建底部信息"""
    footer_lines = [
        f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "🤖 由AI自动生成"
    ]
    return create_plain_text_element("\n".join(footer_lines))


# ==================== 主函数：组装卡片 ====================

def format_ai_report_to_feishu_card(report):
    """
    将AI分析报告格式化为飞书消息卡片格式（使用规范的JSON结构）
    
    参数:
        report: AI分析报告 (dict)
    
    返回:
        飞书消息卡片内容 (JSON字符串)
    """
    date = report.get("date", datetime.now().strftime("%Y-%m-%d"))
    statistics = report.get("statistics", {})
    inspirations = report.get("inspirations", [])
    deep_reading = report.get("deep_reading", [])
    hot_topics = report.get("hot_topics", [])
    
    # 基础卡片结构
    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": f"🤖 AI选题日报 - {date}"
            },
            "template": "blue"
        },
        "elements": []
    }
    
    # 组装各个部分（使用辅助函数）
    elements = []
    
    # 1. 今日概览
    elements.append(build_overview_section(statistics))
    elements.append(create_hr_element())
    
    # 2. 选题灵感
    inspiration_elements = build_inspiration_section(inspirations)
    if inspiration_elements:
        elements.extend(inspiration_elements)
        elements.append(create_hr_element())
    
    # 3. 深度阅读推荐
    reading_elements = build_deep_reading_section(deep_reading)
    if reading_elements:
        elements.extend(reading_elements)
        elements.append(create_hr_element())
    
    # 4. 热点话题
    topic_elements = build_hot_topics_section(hot_topics)
    if topic_elements:
        elements.extend(topic_elements)
        elements.append(create_hr_element())
    
    # 5. 底部信息
    elements.append(build_footer_section())
    
    # 将元素添加到卡片
    card["elements"] = elements
    
    return json.dumps(card, ensure_ascii=False)


def save_card_json_to_file(card_json_str, report_date=None):
    """
    保存卡片JSON到文件
    
    参数:
        card_json_str: 卡片JSON字符串
        report_date: 报告日期（用于文件名）
    
    返回:
        保存的文件路径
    """
    # 创建输出目录
    output_dir = Path(__file__).parent / "data" / "cards"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名（带时间戳）
    if report_date:
        date_str = report_date.replace("-", "")
    else:
        date_str = datetime.now().strftime("%Y%m%d")
    
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"card_{date_str}_{timestamp}.json"
    filepath = output_dir / filename
    
    # 格式化JSON并保存
    card_dict = json.loads(card_json_str)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(card_dict, f, ensure_ascii=False, indent=2)
    
    return str(filepath)


def push_report_to_feishu(report, app_id, app_secret, chat_id):
    """
    将AI报告推送到飞书群（使用消息卡片格式）
    
    参数:
        report: AI分析报告
        app_id: 飞书应用ID
        app_secret: 飞书应用Secret
        chat_id: 飞书群ID
    
    返回:
        消息发送结果
    """
    print("\n" + "=" * 60)
    print("📱 开始推送到飞书群")
    print("=" * 60)
    
    try:
        # 1. 获取 tenant_access_token
        token = get_tenant_access_token(app_id, app_secret)
        
        # 2. 格式化报告为卡片
        print(f"\n📝 正在格式化报告为消息卡片...")
        content = format_ai_report_to_feishu_card(report)
        
        # 3. 打印卡片JSON（格式化显示）
        print("\n" + "=" * 60)
        print("📋 生成的卡片JSON：")
        print("=" * 60)
        card_dict = json.loads(content)
        formatted_json = json.dumps(card_dict, ensure_ascii=False, indent=2)
        print(formatted_json)
        
        # 4. 保存到文件
        report_date = report.get("date")
        filepath = save_card_json_to_file(content, report_date)
        print("\n" + "=" * 60)
        print(f"💾 卡片JSON已保存到: {filepath}")
        print("=" * 60)
        
        # 5. 发送消息（使用 interactive 类型）
        result = send_message_to_group(token, chat_id, "interactive", content)
        
        print("\n" + "=" * 60)
        print("✅ 推送完成!")
        print("=" * 60)
        
        return result
    
    except Exception as e:
        print(f"\n❌ 推送失败: {e}")
        raise


if __name__ == "__main__":
    # 测试代码
    print("⚠️  这是飞书推送模块，请通过main.py调用")
    print("或者运行 test_feishu_push.py 进行测试")


