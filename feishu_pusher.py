#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
飞书推送模块
功能：将AI分析报告推送到飞书群
"""

import requests
import json
from datetime import datetime


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


def format_ai_report_to_feishu_card(report):
    """
    将AI分析报告格式化为飞书消息卡片格式
    
    参数:
        report: AI分析报告 (dict)
    
    返回:
        飞书消息卡片内容 (JSON字符串)
    """
    date = report.get("date", datetime.now().strftime("%Y-%m-%d"))
    statistics = report.get("statistics", {})
    inspirations = report.get("inspirations", [])  # 选题灵感
    deep_reading = report.get("deep_reading", [])  # 深度阅读
    hot_topics = report.get("hot_topics", [])  # 热点话题
    
    # 构建飞书消息卡片（使用正确的格式）
    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": f"🤖 AI选题日报 - {date}"
            },
            "template": "blue"  # 蓝色主题
        },
        "elements": []
    }
    
    # ==================== 今日概览部分 ====================
    overview_text = f"📊 **今日概览**\n"
    overview_text += f"• 分析文章数: {statistics.get('total_articles', 0)}\n"
    overview_text += f"• 订阅账号数: {statistics.get('accounts_count', 0)}\n"
    
    card["elements"].append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": overview_text
        }
    })
    
    # 添加分割线
    card["elements"].append({"tag": "hr"})
    
    # ==================== 选题灵感部分 ====================
    if inspirations:
        card["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "💡 **选题灵感**"
            }
        })
        
        for i, topic in enumerate(inspirations, 1):
            inspiration_text = f"**{i}. {topic.get('title', '')}**\n"
            inspiration_text += f"📐 角度: {topic.get('angle', '')}\n"
            inspiration_text += f"🎯 目标: {topic.get('target', '')}\n"
            inspiration_text += f"💎 价值: {topic.get('value', '')}\n"
            
            # 添加参考文章
            if topic.get('references'):
                inspiration_text += f"\n📚 参考文章:\n"
                for article in topic.get('references', []):
                    article_title = article.get('article_title', '文章')
                    article_url = article.get('url', '')
                    source = article.get('source', '')
                    inspiration_text += f"• [{article_title}]({article_url}) ({source})\n"
            
            card["elements"].append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": inspiration_text
                }
            })
        
        # 添加分割线
        card["elements"].append({"tag": "hr"})
    
    # ==================== 深度阅读推荐部分 ====================
    if deep_reading:
        card["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "📚 **深度阅读推荐**"
            }
        })
        
        for i, article in enumerate(deep_reading, 1):
            article_title = article.get('article_title', '文章')
            article_url = article.get('article_url', '')
            source = article.get('source', '')
            score = article.get('score', 0)
            recommendation = article.get('recommendation', '')
            value_point = article.get('value_point', '')
            
            reading_text = f"**{i}. [{article_title}]({article_url})**\n"
            reading_text += f"👤 作者: {source} | ⭐ 评分: {score}\n"
            reading_text += f"💬 推荐理由: {recommendation}\n"
            
            if value_point:
                reading_text += f"💡 核心价值: {value_point}\n"
            
            # 添加符合的标准
            if article.get('meets_criteria'):
                reading_text += f"\n✅ 符合标准:\n"
                for criterion in article.get('meets_criteria', []):
                    reading_text += f"  ✓ {criterion}\n"
            
            card["elements"].append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": reading_text
                }
            })
        
        # 添加分割线
        card["elements"].append({"tag": "hr"})
    
    # ==================== 热点话题部分 ====================
    if hot_topics:
        card["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "🔥 **本周热点话题**"
            }
        })
        
        for i, topic in enumerate(hot_topics, 1):
            topic_name = topic.get('topic_name', '')
            heat_level = topic.get('heat_level', '')
            mention_count = topic.get('mention_count', 0)
            analysis = topic.get('analysis', '')
            
            topic_text = f"**{i}. {topic_name}**\n"
            topic_text += f"🔥 热度: {heat_level} | 💬 讨论次数: {mention_count}\n"
            topic_text += f"📊 分析: {analysis}\n"
            
            card["elements"].append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": topic_text
                }
            })
        
        # 添加分割线
        card["elements"].append({"tag": "hr"})
    
    # ==================== 底部信息 ====================
    footer_text = f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    footer_text += f"🤖 由AI自动生成"
    
    card["elements"].append({
        "tag": "div",
        "text": {
            "tag": "plain_text",
            "content": footer_text
        }
    })
    
    return json.dumps(card, ensure_ascii=False)


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
        
        # 3. 发送消息（使用 interactive 类型）
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


