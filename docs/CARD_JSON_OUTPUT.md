# 卡片JSON输出功能说明

## 功能概述

每次推送飞书消息卡片时，系统会自动：

1. ✅ **在控制台打印**完整的卡片JSON（格式化显示）
2. ✅ **保存到文件**供后续查看和调试

## 使用方式

### 正常运行时自动保存

```bash
python main.py
```

运行时会自动：
1. 生成卡片JSON
2. 在控制台打印完整的JSON结构
3. 保存到 `data/cards/` 目录

### 查看保存的文件

```bash
# 查看所有保存的卡片JSON
ls -lh data/cards/

# 查看最新的卡片
cat data/cards/card_20251229_*.json | jq .
```

## 文件命名规则

```
data/cards/card_YYYYMMDD_HHMMSS.json
```

**示例**：
- `card_20251229_200351.json` - 2025年12月29日 20:03:51 生成的卡片

## 文件结构

保存的JSON文件是标准的飞书消息卡片格式：

```json
{
  "config": {
    "wide_screen_mode": true
  },
  "header": {
    "title": {
      "tag": "plain_text",
      "content": "🤖 AI选题日报 - 2025-12-29"
    },
    "template": "blue"
  },
  "elements": [
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "📊 **今日概览**\n..."
      }
    },
    ...
  ]
}
```

## 输出示例

### 控制台输出

```
============================================================
📋 生成的卡片JSON：
============================================================
{
  "config": {
    "wide_screen_mode": true
  },
  "header": {
    "title": {
      "tag": "plain_text",
      "content": "🤖 AI选题日报 - 2025-12-29"
    },
    "template": "blue"
  },
  "elements": [
    ...完整的JSON结构...
  ]
}

============================================================
💾 卡片JSON已保存到: data/cards/card_20251229_200351.json
============================================================
```

## 使用场景

### 1. 调试卡片样式

当卡片显示不正常时，可以查看JSON结构：

```bash
# 查看最新的卡片JSON
cat data/cards/card_*.json | tail -n +1
```

### 2. 复制到卡片搭建工具

1. 打开 [飞书卡片搭建工具](https://open.feishu.cn/tool/cardbuilder)
2. 复制保存的JSON内容
3. 粘贴到工具中预览效果

### 3. 对比不同版本

```bash
# 比较两个卡片的差异
diff data/cards/card_20251229_200351.json \
     data/cards/card_20251229_180432.json
```

### 4. 作为测试数据

在开发时可以使用保存的JSON作为测试数据：

```python
import json

# 读取保存的卡片JSON
with open('data/cards/card_20251229_200351.json', 'r') as f:
    card = json.load(f)

# 用于测试
print(card['header']['title']['content'])
```

## 文件管理

### 查看文件列表

```bash
# 按时间倒序查看
ls -lt data/cards/

# 只看今天的
ls -lt data/cards/card_$(date +%Y%m%d)_*.json
```

### 清理旧文件

```bash
# 删除7天前的卡片文件
find data/cards/ -name "card_*.json" -mtime +7 -delete

# 只保留最近10个文件
cd data/cards && ls -t card_*.json | tail -n +11 | xargs rm -f
```

### 目录结构

```
wxrss_to_feishu/
├── data/
│   └── cards/                      # 卡片JSON保存目录
│       ├── card_20251229_200351.json
│       ├── card_20251229_180432.json
│       └── card_20251228_093015.json
├── feishu_pusher.py               # 推送模块（包含保存功能）
└── main.py                        # 主程序
```

## 代码实现

### 核心函数

```python
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
    
    # 生成文件名
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
```

### 在推送流程中使用

```python
def push_report_to_feishu(report, app_id, app_secret, chat_id):
    # 1. 生成卡片
    content = format_ai_report_to_feishu_card(report)
    
    # 2. 打印到控制台
    card_dict = json.loads(content)
    formatted_json = json.dumps(card_dict, ensure_ascii=False, indent=2)
    print(formatted_json)
    
    # 3. 保存到文件
    filepath = save_card_json_to_file(content, report.get("date"))
    print(f"💾 卡片JSON已保存到: {filepath}")
    
    # 4. 发送
    result = send_message_to_group(token, chat_id, "interactive", content)
```

## 高级用法

### 批量处理卡片JSON

```python
import json
from pathlib import Path

# 读取所有卡片JSON
cards_dir = Path("data/cards")
for card_file in cards_dir.glob("card_*.json"):
    with open(card_file, 'r') as f:
        card = json.load(f)
    
    # 统计元素数量
    print(f"{card_file.name}: {len(card['elements'])} 个元素")
```

### 提取卡片信息

```python
import json

def analyze_card(card_path):
    """分析卡片结构"""
    with open(card_path, 'r') as f:
        card = json.load(f)
    
    info = {
        "主题颜色": card['header']['template'],
        "标题": card['header']['title']['content'],
        "元素数量": len(card['elements']),
        "div元素": sum(1 for e in card['elements'] if e.get('tag') == 'div'),
        "分割线": sum(1 for e in card['elements'] if e.get('tag') == 'hr'),
    }
    
    return info

# 使用
info = analyze_card("data/cards/card_20251229_200351.json")
print(json.dumps(info, ensure_ascii=False, indent=2))
```

### 自动生成样式预览

```python
def generate_preview_html(card_path):
    """生成HTML预览"""
    with open(card_path, 'r') as f:
        card = json.load(f)
    
    html = f"""
    <html>
    <head><title>卡片预览</title></head>
    <body>
        <h1>{card['header']['title']['content']}</h1>
        <pre>{json.dumps(card, ensure_ascii=False, indent=2)}</pre>
    </body>
    </html>
    """
    
    preview_path = card_path.replace('.json', '.html')
    with open(preview_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"预览文件: {preview_path}")
```

## 常见问题

### Q1: 文件太多了，占用空间怎么办？

A: 可以定期清理旧文件，或者修改代码只在调试模式下保存：

```python
# 在 config.py 中添加
DEBUG_MODE = True  # 或 False

# 在 feishu_pusher.py 中修改
import config

if getattr(config, 'DEBUG_MODE', False):
    filepath = save_card_json_to_file(content, report_date)
```

### Q2: 如何只打印不保存？

A: 注释掉保存文件的代码行：

```python
# filepath = save_card_json_to_file(content, report_date)
# print(f"💾 卡片JSON已保存到: {filepath}")
```

### Q3: 文件保存位置可以修改吗？

A: 可以，修改 `save_card_json_to_file()` 函数中的路径：

```python
# 修改保存目录
output_dir = Path("/your/custom/path/cards")
```

### Q4: 如何在文件名中添加更多信息？

A: 修改文件名生成逻辑：

```python
# 添加文章数量到文件名
article_count = report.get('statistics', {}).get('total_articles', 0)
filename = f"card_{date_str}_{timestamp}_art{article_count}.json"
```

## 总结

这个功能的主要优势：

1. ✅ **调试方便** - 可以随时查看生成的JSON结构
2. ✅ **版本对比** - 保留历史记录，便于对比
3. ✅ **快速复现** - 使用保存的JSON快速复现问题
4. ✅ **文档化** - 自动记录每次推送的卡片内容
5. ✅ **测试数据** - 可作为单元测试的测试数据

---

**更新日期**: 2025-12-29  
**功能版本**: v1.0

