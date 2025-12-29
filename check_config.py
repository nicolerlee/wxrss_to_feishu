#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置检查脚本
运行此脚本检查所有配置是否就绪
"""

import config
import requests
from feishu_bitable import get_tenant_access_token, get_table_fields


def check_config():
    """检查所有配置项"""
    print("\n" + "=" * 70)
    print("🔍 配置检查工具")
    print("=" * 70)
    print()
    
    all_good = True
    
    # 1. 检查AI配置
    print("🤖 检查AI配置...")
    ai_provider = getattr(config, 'AI_PROVIDER', 'deepseek')
    
    if ai_provider == 'deepseek':
        if hasattr(config, 'DEEPSEEK_API_KEY') and config.DEEPSEEK_API_KEY != "sk-xxx":
            print(f"   ✅ DeepSeek API Key: {config.DEEPSEEK_API_KEY[:20]}...")
        else:
            print(f"   ❌ DeepSeek API Key 未配置")
            all_good = False
    elif ai_provider == 'claude':
        if hasattr(config, 'CLAUDE_API_KEY') and config.CLAUDE_API_KEY != "sk-ant-xxx":
            print(f"   ✅ Claude API Key: {config.CLAUDE_API_KEY[:20]}...")
        else:
            print(f"   ❌ Claude API Key 未配置")
            all_good = False
    
    print()
    
    # 2. 检查飞书应用配置
    print("📱 检查飞书应用配置...")
    if hasattr(config, 'FEISHU_APP_ID') and config.FEISHU_APP_ID != "cli_xxx":
        print(f"   ✅ APP_ID: {config.FEISHU_APP_ID}")
    else:
        print(f"   ❌ FEISHU_APP_ID 未配置")
        all_good = False
    
    if hasattr(config, 'FEISHU_APP_SECRET') and config.FEISHU_APP_SECRET != "xxx":
        print(f"   ✅ APP_SECRET: {config.FEISHU_APP_SECRET[:20]}...")
    else:
        print(f"   ❌ FEISHU_APP_SECRET 未配置")
        all_good = False
    
    print()
    
    # 3. 检查飞书群配置
    push_mode = getattr(config, 'FEISHU_PUSH_MODE', 'group')
    print(f"📋 推送模式: {push_mode}")
    
    if push_mode in ['group', 'both']:
        print("   检查飞书群配置...")
        if hasattr(config, 'FEISHU_CHAT_ID') and config.FEISHU_CHAT_ID.strip() not in ["oc_xxx", ""]:
            print(f"   ✅ CHAT_ID: {config.FEISHU_CHAT_ID}")
        else:
            print(f"   ❌ FEISHU_CHAT_ID 未配置")
            all_good = False
    
    print()
    
    # 4. 检查多维表格配置
    if push_mode in ['bitable', 'both']:
        print("📊 检查多维表格配置...")
        if hasattr(config, 'FEISHU_BITABLE_APP_TOKEN') and config.FEISHU_BITABLE_APP_TOKEN != "xxx":
            print(f"   ✅ APP_TOKEN: {config.FEISHU_BITABLE_APP_TOKEN}")
        else:
            print(f"   ❌ FEISHU_BITABLE_APP_TOKEN 未配置")
            all_good = False
        
        if hasattr(config, 'FEISHU_BITABLE_TABLE_ID') and config.FEISHU_BITABLE_TABLE_ID != "xxx":
            print(f"   ✅ TABLE_ID: {config.FEISHU_BITABLE_TABLE_ID}")
        else:
            print(f"   ❌ FEISHU_BITABLE_TABLE_ID 未配置")
            all_good = False
    
    print()
    
    # 5. 测试飞书API连接
    if all_good:
        print("🔗 测试飞书API连接...")
        try:
            token = get_tenant_access_token(config.FEISHU_APP_ID, config.FEISHU_APP_SECRET)
            print("   ✅ 成功获取 tenant_access_token")
            
            # 如果配置了多维表格，测试字段获取
            if push_mode in ['bitable', 'both']:
                print()
                print("📊 检查多维表格字段...")
                try:
                    fields = get_table_fields(token, config.FEISHU_BITABLE_APP_TOKEN, config.FEISHU_BITABLE_TABLE_ID)
                    print(f"   ✅ 表格有 {len(fields)} 个字段")
                    
                    # 检查必需字段
                    field_names = [f.get('field_name') for f in fields]
                    required_fields = ['标题', '作者', '链接', '发布时间', '内容', '字数', '采集时间']
                    
                    missing_fields = [f for f in required_fields if f not in field_names]
                    
                    if missing_fields:
                        print(f"   ⚠️  缺少字段: {', '.join(missing_fields)}")
                        print("   请在多维表格中创建这些字段")
                        all_good = False
                    else:
                        print("   ✅ 所有必需字段都存在")
                    
                except Exception as e:
                    print(f"   ❌ 无法访问多维表格: {e}")
                    print("   可能原因:")
                    print("      - 应用未开通多维表格权限")
                    print("      - 应用未添加为表格协作者")
                    all_good = False
            
        except Exception as e:
            print(f"   ❌ 连接失败: {e}")
            all_good = False
    
    print()
    
    # 6. 检查RSS配置
    print("📡 检查RSS配置...")
    if hasattr(config, 'RSS_DOMAIN'):
        print(f"   ✅ RSS_DOMAIN: {config.RSS_DOMAIN}")
        
        # 测试RSS服务是否可访问
        try:
            test_url = config.RSS_DOMAIN.rstrip('/')
            response = requests.get(test_url, timeout=3)
            if response.status_code == 200:
                print(f"   ✅ RSS服务运行正常")
            else:
                print(f"   ⚠️  RSS服务返回状态码: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 无法访问RSS服务: {e}")
            print("   请确保 wechat2rss 服务正在运行")
            all_good = False
    else:
        print(f"   ❌ RSS_DOMAIN 未配置")
        all_good = False
    
    print()
    print("=" * 70)
    
    if all_good:
        print("🎉 所有配置检查通过！")
        print()
        print("✅ 你可以运行以下命令:")
        print("   python main.py")
    else:
        print("⚠️  存在配置问题，请检查上述错误")
        print()
        print("💡 参考文档:")
        print("   - USAGE_GUIDE.md (飞书群配置)")
        print("   - BITABLE_GUIDE.md (多维表格配置)")
    
    print("=" * 70)
    print()
    
    return all_good


if __name__ == "__main__":
    check_config()

