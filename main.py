#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeChat RSS → AI选题日报
主程序：整合所有模块，实现完整功能
"""

import sys
import json
from datetime import datetime
from pathlib import Path
import config
from rss_fetcher import fetch_rss_articles
from data_cleaner import clean_articles_v2
from ai_analyzer import analyze_articles
from feishu_pusher import push_report_to_feishu
from feishu_bitable import save_articles_to_feishu_bitable


def save_json(data, filename, output_dir=None):
    """
    保存数据到JSON文件
    
    参数:
        data: 要保存的数据
        filename: 文件名
        output_dir: 输出目录（默认为当前目录）
    """
    # 如果指定了输出目录，创建完整路径
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        filepath = output_path / filename
    else:
        filepath = Path(filename)
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据已保存到: {filepath}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print(" " * 25 + "🤖 WeChat RSS → AI选题日报")
    print("=" * 80)
    print(f"\n⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # ==================== 第1步：爬取RSS文章 ====================
        print("\n" + "=" * 80)
        print("📡 第1步：爬取RSS文章")
        print("=" * 80)
        
        articles = fetch_rss_articles(
            opml_file=config.OPML_FILE,
            filter_24h=True  # 只获取24小时内的文章
        )
        
        if not articles:
            print("\n⚠️  没有找到符合条件的文章")
            print("可能原因:")
            print("  1. RSS源没有更新")
            print("  2. 时间过滤太严格（可以调整 DAYS_AGO 参数）")
            print("  3. wechat2rss服务未运行")
            sys.exit(0)
        
        print(f"\n✅ 成功获取 {len(articles)} 篇文章")
        
        # 保存原始数据（可选）
        if getattr(config, 'SAVE_RAW_DATA', False):
            save_json(articles, "raw_articles.json", output_dir="data")
        
        # ==================== 第2步：清洗数据 ====================
        print("\n" + "=" * 80)
        print("🧹 第2步：清洗数据")
        print("=" * 80)
        
        cleaned_articles = clean_articles_v2(
            articles=articles,
            min_word_count=getattr(config, 'MIN_WORD_COUNT', 500)
        )
        
        if not cleaned_articles:
            print("\n⚠️  清洗后没有符合条件的文章")
            print("可能原因:")
            print("  1. 文章字数太少（可以调整 MIN_WORD_COUNT 参数）")
            print("  2. 广告过滤太严格")
            sys.exit(0)
        
        print(f"\n✅ 清洗完成，剩余 {len(cleaned_articles)} 篇文章")
        
        # ==================== 第2.5步：保存到飞书多维表格（如果配置了）====================
        push_mode = getattr(config, 'FEISHU_PUSH_MODE', 'group')
        
        if push_mode in ['bitable', 'both']:
            print("\n" + "=" * 80)
            print("📊 第2.5步：保存清洗后的数据到飞书多维表格")
            print("=" * 80)
            
            # 检查配置
            if (hasattr(config, 'FEISHU_BITABLE_APP_TOKEN') and 
                hasattr(config, 'FEISHU_BITABLE_TABLE_ID') and
                config.FEISHU_BITABLE_APP_TOKEN != "xxx" and
                config.FEISHU_BITABLE_TABLE_ID != "xxx"):
                
                try:
                    save_articles_to_feishu_bitable(
                        articles=cleaned_articles,
                        app_id=config.FEISHU_APP_ID,
                        app_secret=config.FEISHU_APP_SECRET,
                        app_token=config.FEISHU_BITABLE_APP_TOKEN,
                        table_id=config.FEISHU_BITABLE_TABLE_ID,
                        check_fields=False
                    )
                except Exception as e:
                    print(f"❌ 保存到多维表格失败: {e}")
                    print("   继续执行后续步骤...")
            else:
                print("⚠️  未配置多维表格参数，跳过保存")
                print("   如需保存到多维表格，请配置:")
                print("   - FEISHU_BITABLE_APP_TOKEN")
                print("   - FEISHU_BITABLE_TABLE_ID")
        
        # ==================== 第3步：AI分析（可选）====================
        # 如果只保存到多维表格，可以跳过AI分析
        if push_mode == 'bitable':
            print("\n" + "=" * 80)
            print("✅ 数据已保存到多维表格，跳过AI分析")
            print("=" * 80)
            print(f"\n📊 执行摘要:")
            print(f"   • 原始文章: {len(articles)} 篇")
            print(f"   • 清洗后: {len(cleaned_articles)} 篇")
            print(f"   • 已保存到飞书多维表格")
            print(f"\n⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return
        
        print("\n" + "=" * 80)
        print("🤖 第3步：AI分析")
        print("=" * 80)
        
        # 获取AI配置
        ai_provider = getattr(config, 'AI_PROVIDER', 'deepseek')
        
        if ai_provider.lower() == 'deepseek':
            api_key = config.DEEPSEEK_API_KEY
            model = getattr(config, 'DEEPSEEK_MODEL', 'deepseek-chat')
        elif ai_provider.lower() == 'claude':
            api_key = config.CLAUDE_API_KEY
            model = getattr(config, 'CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
        elif ai_provider.lower() == 'openai':
            api_key = config.OPENAI_API_KEY
            model = getattr(config, 'OPENAI_MODEL', 'gpt-4-turbo-preview')
        else:
            print(f"❌ 不支持的AI提供商: {ai_provider}")
            sys.exit(1)
        
        if not api_key or api_key in ['sk-xxx', 'sk-ant-xxx']:
            print(f"❌ 请先配置 {ai_provider.upper()}_API_KEY")
            print(f"   打开 config.py，修改对应的API Key")
            sys.exit(1)
        
        print(f"使用 {ai_provider.upper()} 进行分析...")
        print(f"模型: {model}")
        
        report = analyze_articles(
            articles=cleaned_articles,
            ai_provider=ai_provider,
            api_key=api_key,
            model=model
        )
        
        # 保存报告到 reports 目录
        report_filename = f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_json(report, report_filename, output_dir="reports")
        
        # ==================== 第4步：推送AI报告到飞书群（可选）====================
        if push_mode in ['group', 'both']:
            print("\n" + "=" * 80)
            print("📱 第4步：推送AI报告到飞书群")
            print("=" * 80)
            
            # 检查飞书配置
            if not hasattr(config, 'FEISHU_APP_ID') or config.FEISHU_APP_ID == "cli_xxx":
                print("⚠️  未配置飞书APP_ID，跳过推送")
                print("   如需推送到飞书，请配置 config.py 中的飞书参数")
            elif not hasattr(config, 'FEISHU_CHAT_ID') or config.FEISHU_CHAT_ID.strip() == "oc_xxx":
                print("⚠️  未配置飞书CHAT_ID，跳过推送")
                print("   如需推送到飞书群，请配置 config.py 中的 FEISHU_CHAT_ID")
            else:
                try:
                    push_report_to_feishu(
                        report=report,
                        app_id=config.FEISHU_APP_ID,
                        app_secret=config.FEISHU_APP_SECRET,
                        chat_id=config.FEISHU_CHAT_ID.strip()
                    )
                except Exception as e:
                    print(f"❌ 推送到飞书失败: {e}")
                    print("   报告已保存到本地，可以手动查看")
        else:
            print("\n⏩ 跳过飞书群推送（当前模式：只保存到多维表格）")
        
        # ==================== 完成 ====================
        print("\n" + "=" * 80)
        print("✅ 全部完成！")
        print("=" * 80)
        
        print(f"\n📊 执行摘要:")
        print(f"   • 原始文章: {len(articles)} 篇")
        print(f"   • 清洗后: {len(cleaned_articles)} 篇")
        print(f"   • 选题灵感: {len(report.get('topic_inspirations', []))} 条")
        print(f"   • 深度推荐: {len(report.get('deep_reading', []))} 篇")
        print(f"   • 热点话题: {len(report.get('hot_topics', []))} 个")
        print(f"\n📁 报告文件: reports/{report_filename}")
        print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        sys.exit(0)
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ 执行失败")
        print("=" * 80)
        print(f"\n错误信息: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

