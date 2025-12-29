#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
飞书多维表格模块
功能：将清洗后的文章数据保存到飞书多维表格
"""

import requests
import json
from datetime import datetime
from typing import List, Dict


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


def get_table_fields(tenant_access_token, app_token, table_id):
    """
    获取多维表格的字段信息
    用于调试和验证表结构
    
    参考文档: https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/list
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    print(f"📋 正在获取表格字段信息...")
    
    try:
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result.get("code") != 0:
            print(f"❌ 获取字段信息失败: {result}")
            raise Exception(f"Failed to get table fields: {result.get('msg')}")
        
        fields = result.get("data", {}).get("items", [])
        print(f"✅ 表格有 {len(fields)} 个字段:")
        for field in fields:
            print(f"   • {field.get('field_name')} ({field.get('type')}) - ID: {field.get('field_id')}")
        
        return fields
    
    except Exception as e:
        print(f"❌ 获取字段信息时发生错误: {e}")
        raise


def format_article_for_bitable(article):
    """
    将清洗后的文章格式化为多维表格记录格式
    
    参数:
        article: 清洗后的文章数据
    
    返回:
        多维表格记录格式的字典
    """
    # 提取发布时间（Unix时间戳，毫秒）
    published_timestamp = None
    
    # 尝试多种时间字段（兼容不同的数据格式）
    if article.get('published_parsed'):
        # feedparser的时间格式转为Unix时间戳
        import time
        published_timestamp = int(time.mktime(article['published_parsed']) * 1000)
    elif article.get('publish_time') or article.get('publish_time_raw') or article.get('published'):
        # 如果有字符串格式的时间，尝试解析
        time_str = article.get('publish_time') or article.get('publish_time_raw') or article.get('published')
        try:
            from dateutil import parser as date_parser
            dt = date_parser.parse(time_str)
            published_timestamp = int(dt.timestamp() * 1000)
        except Exception as e:
            print(f"⚠️  解析时间失败: {time_str} - {e}")
            pass
    
    # 当前时间作为采集时间
    collected_timestamp = int(datetime.now().timestamp() * 1000)
    
    # 验证必需字段
    title = article.get('title', '').strip()
    # 兼容 link 和 url 两种字段名
    link = article.get('link', article.get('url', '')).strip()
    
    if not title or not link:
        raise ValueError(f"标题或链接为空: title={title}, link={link}")
    
    # 构建记录数据
    # 注意：字段名需要与多维表格中的实际字段名匹配
    record = {
        "标题": title,
        "作者": article.get('author', '').strip() or '未知作者',
        "链接": {
            "link": link,
            "text": title  # URL字段需要对象格式
        },
        "内容": article.get('content_markdown', '').strip()[:50000],  # 限制长度，避免超出限制
        "字数": article.get('word_count', 0),
    }
    
    # 添加时间字段（如果存在）
    if published_timestamp:
        record["发布时间"] = published_timestamp
    
    record["采集时间"] = collected_timestamp
    
    # 如果有摘要字段
    if article.get('summary'):
        # 清理HTML标签
        import re
        summary = re.sub(r'<[^>]+>', '', article.get('summary', ''))
        record["摘要"] = summary[:500]  # 限制长度
    
    return record


def batch_insert_articles_to_bitable(tenant_access_token, app_token, table_id, articles):
    """
    批量插入文章到多维表格
    
    参数:
        tenant_access_token: 访问令牌
        app_token: 多维表格app_token
        table_id: 数据表table_id
        articles: 文章列表
    
    返回:
        插入结果
        
    参考文档: https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/batch_create
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
    
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    # 格式化文章数据
    records = []
    for article in articles:
        try:
            # 验证文章是否有有效内容
            if not article.get('title') or not article.get('title').strip():
                print(f"⚠️  跳过空标题文章")
                continue
            
            # 兼容 link 和 url 两种字段名
            article_link = article.get('link') or article.get('url')
            if not article_link or not article_link.strip():
                print(f"⚠️  跳过无链接文章: {article.get('title', 'Unknown')}")
                continue
            
            record = format_article_for_bitable(article)
            
            # 再次验证格式化后的记录
            if not record.get('标题') or not record.get('标题').strip():
                print(f"⚠️  跳过格式化后标题为空的记录")
                continue
            
            records.append({"fields": record})
        except Exception as e:
            print(f"⚠️  格式化文章失败: {article.get('title', 'Unknown')} - {e}")
            continue
    
    if not records:
        print("❌ 没有可插入的记录")
        return None
    
    # 飞书API限制：每次最多插入500条
    batch_size = 500
    all_results = []
    
    for i in range(0, len(records), batch_size):
        batch_records = records[i:i + batch_size]
        
        payload = {
            "records": batch_records
        }
        
        print(f"📤 正在插入第 {i+1}-{min(i+batch_size, len(records))} 条记录...")
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()
            
            if result.get("code") != 0:
                print(f"❌ 插入记录失败: {result}")
                # 如果是权限问题，给出提示
                if result.get("code") == 403:
                    print("\n💡 权限不足，请检查:")
                    print("   1. 应用是否开通了多维表格权限")
                    print("   2. 应用是否有该多维表格的编辑权限")
                    print("   3. 参考: https://open.feishu.cn/document/server-docs/docs/bitable-v1/notification")
                raise Exception(f"Failed to insert records: {result.get('msg')}")
            
            inserted_count = len(result.get("data", {}).get("records", []))
            print(f"✅ 成功插入 {inserted_count} 条记录")
            all_results.extend(result.get("data", {}).get("records", []))
            
        except Exception as e:
            print(f"❌ 插入记录时发生错误: {e}")
            raise
    
    return all_results


def save_articles_to_feishu_bitable(articles, app_id, app_secret, app_token, table_id, check_fields=False):
    """
    将清洗后的文章保存到飞书多维表格
    
    参数:
        articles: 清洗后的文章列表
        app_id: 飞书应用ID
        app_secret: 飞书应用Secret
        app_token: 多维表格app_token
        table_id: 数据表table_id
        check_fields: 是否先检查表格字段（调试用）
    
    返回:
        插入结果
    """
    print("\n" + "=" * 70)
    print("📊 开始保存到飞书多维表格")
    print("=" * 70)
    
    try:
        # 1. 获取 tenant_access_token
        token = get_tenant_access_token(app_id, app_secret)
        
        # 2. 检查表格字段（可选，用于调试）
        if check_fields:
            print()
            get_table_fields(token, app_token, table_id)
        
        # 3. 批量插入文章
        print()
        print(f"📝 准备插入 {len(articles)} 篇文章...")
        results = batch_insert_articles_to_bitable(token, app_token, table_id, articles)
        
        if results is None or len(results) == 0:
            print("\n" + "=" * 70)
            print("⚠️  没有成功插入任何记录")
            print("=" * 70)
            return []
        
        print("\n" + "=" * 70)
        print(f"✅ 保存完成！成功插入 {len(results)} 条记录")
        print("=" * 70)
        
        return results
    
    except Exception as e:
        print(f"\n❌ 保存失败: {e}")
        raise


if __name__ == "__main__":
    # 测试代码
    print("⚠️  这是飞书多维表格模块，请通过main.py调用")
    print("或者运行 test_bitable.py 进行测试")

