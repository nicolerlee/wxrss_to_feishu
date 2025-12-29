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


def format_ai_report_to_feishu(report):
    """
    将AI分析报告格式化为飞书富文本消息格式
    
    参数:
        report: AI分析报告 (dict)
    
    返回:
        飞书富文本消息内容 (JSON字符串)
    """
    date = report.get("date", datetime.now().strftime("%Y-%m-%d"))
    statistics = report.get("statistics", {})
    inspirations = report.get("inspirations", [])  # ✅ 修正字段名
    deep_reading = report.get("deep_reading", [])
    hot_topics = report.get("hot_topics", [])
    
    # 构建飞书富文本内容
    content = {
        "zh_cn": {
            "title": f"🤖 AI选题日报 - {date}",
            "content": []
        }
    }
    
    # 添加概览部分
    content["zh_cn"]["content"].append([
        {"tag": "text", "text": "📊 ", "style": ["bold"]},
        {"tag": "text", "text": "今日概览", "style": ["bold"]},
    ])
    content["zh_cn"]["content"].append([
        {"tag": "text", "text": f"• 分析文章数: {statistics.get('total_articles', 0)}"}
    ])
    content["zh_cn"]["content"].append([
        {"tag": "text", "text": f"• 订阅账号数: {statistics.get('accounts_count', 0)}"}
    ])
    content["zh_cn"]["content"].append([
        {"tag": "text", "text": f"• 主要话题: "}
    ])
    content["zh_cn"]["content"].append([{"tag": "text", "text": ""}])  # 空行
    
    # 添加选题灵感部分
    if inspirations:
        content["zh_cn"]["content"].append([
            {"tag": "text", "text": "💡 ", "style": ["bold"]},
            {"tag": "text", "text": "选题灵感", "style": ["bold"]},
        ])
        for i, topic in enumerate(inspirations, 1):
            content["zh_cn"]["content"].append([
                {"tag": "text", "text": f"{i}. {topic.get('title', '')}", "style": ["bold"]}
            ])
            content["zh_cn"]["content"].append([
                {"tag": "text", "text": f"   角度: {topic.get('angle', '')}"}
            ])
            content["zh_cn"]["content"].append([
                {"tag": "text", "text": f"   目标: {topic.get('target', '')}"}
            ])
            content["zh_cn"]["content"].append([
                {"tag": "text", "text": f"   价值: {topic.get('value', '')}"}
            ])
            
            # 添加参考文章
            if topic.get('references'):
                content["zh_cn"]["content"].append([
                    {"tag": "text", "text": "   参考文章:"}
                ])
                for article in topic.get('references', []):
                    content["zh_cn"]["content"].append([
                        {"tag": "text", "text": f"   • "},
                        {"tag": "a", "text": article.get('article_title', ''), "href": article.get('url', '')},
                        {"tag": "text", "text": f" ({article.get('source', '')})"}
                    ])
            content["zh_cn"]["content"].append([{"tag": "text", "text": ""}])  # 空行
    
    # 添加深度阅读推荐部分
    if deep_reading:
        content["zh_cn"]["content"].append([
            {"tag": "text", "text": "📚 ", "style": ["bold"]},
            {"tag": "text", "text": "深度阅读推荐", "style": ["bold"]},
        ])
        for i, article in enumerate(deep_reading, 1):
            content["zh_cn"]["content"].append([
                {"tag": "text", "text": f"{i}. ", "style": ["bold"]},
                {"tag": "a", "text": article.get('article_title', ''), "href": article.get('article_url', ''), "style": ["bold"]},
            ])
            content["zh_cn"]["content"].append([
                {"tag": "text", "text": f"   作者: {article.get('source', '')} | 评分: {article.get('score', 0)}"}
            ])
            content["zh_cn"]["content"].append([
                {"tag": "text", "text": f"   推荐理由: {article.get('recommendation', '')}"}
            ])
            
            # 添加价值点
            if article.get('value_point'):
                content["zh_cn"]["content"].append([
                    {"tag": "text", "text": f"   核心价值: {article.get('value_point', '')}"}
                ])
            
            # 添加符合的标准
            if article.get('meets_criteria'):
                content["zh_cn"]["content"].append([
                    {"tag": "text", "text": "   符合标准:"}
                ])
                for criterion in article.get('meets_criteria', []):
                    content["zh_cn"]["content"].append([
                        {"tag": "text", "text": f"   ✓ {criterion}"}
                    ])
            content["zh_cn"]["content"].append([{"tag": "text", "text": ""}])  # 空行
    
    # 添加热点话题部分
    if hot_topics:
        content["zh_cn"]["content"].append([
            {"tag": "text", "text": "🔥 ", "style": ["bold"]},
            {"tag": "text", "text": "本周热点话题", "style": ["bold"]},
        ])
        for i, topic in enumerate(hot_topics, 1):
            content["zh_cn"]["content"].append([
                {"tag": "text", "text": f"{i}. {topic.get('topic_name', '')}", "style": ["bold"]}
            ])
            content["zh_cn"]["content"].append([
                {"tag": "text", "text": f"   热度: {topic.get('heat_level', '')} | 讨论次数: {topic.get('mention_count', 0)}"}
            ])
            content["zh_cn"]["content"].append([
                {"tag": "text", "text": f"   分析: {topic.get('analysis', '')}"}
            ])
            content["zh_cn"]["content"].append([{"tag": "text", "text": ""}])  # 空行
    
    # 添加底部信息
    content["zh_cn"]["content"].append([
        {"tag": "text", "text": "---"}
    ])
    content["zh_cn"]["content"].append([
        {"tag": "text", "text": f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
    ])
    content["zh_cn"]["content"].append([
        {"tag": "text", "text": "🤖 由AI自动生成"}
    ])
    
    return json.dumps(content, ensure_ascii=False)


def push_report_to_feishu(report, app_id, app_secret, chat_id):
    """
    将AI报告推送到飞书群
    
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
        
        # 2. 格式化报告
        print(f"\n📝 正在格式化报告...")
        content = format_ai_report_to_feishu(report)
        
        # 3. 发送消息
        result = send_message_to_group(token, chat_id, "post", content)
        
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


