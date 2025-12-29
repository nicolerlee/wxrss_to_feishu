# 飞书卡片自定义指南

## 代码重构说明

### 重构前 vs 重构后

**之前的问题**：
- ❌ 大量字符串拼接，代码冗长
- ❌ 难以维护和修改样式
- ❌ JSON结构不清晰
- ❌ 重复代码多

**重构后的优势**：
- ✅ 使用辅助函数构建元素，代码模块化
- ✅ JSON结构清晰，易于理解
- ✅ 修改样式只需改辅助函数
- ✅ 代码可读性和可维护性大幅提升

### 新的代码结构

```python
# 1. 辅助函数：构建不同类型的元素
create_markdown_element()     # Markdown文本
create_plain_text_element()   # 纯文本
create_hr_element()           # 分割线

# 2. 业务函数：构建各个部分
build_overview_section()      # 今日概览
build_inspiration_section()   # 选题灵感
build_deep_reading_section()  # 深度阅读
build_hot_topics_section()    # 热点话题
build_footer_section()        # 底部信息

# 3. 主函数：组装卡片
format_ai_report_to_feishu_card()
```

## 如何自定义卡片样式

### 1. 修改卡片主题颜色

在 `format_ai_report_to_feishu_card()` 函数中找到：

```python
card = {
    "config": {
        "wide_screen_mode": True
    },
    "header": {
        "title": {
            "tag": "plain_text",
            "content": f"🤖 AI选题日报 - {date}"
        },
        "template": "blue"  # 👈 修改这里
    },
    "elements": []
}
```

**可选颜色**：
- `blue` - 蓝色（默认）
- `red` - 红色
- `green` - 绿色
- `yellow` - 黄色
- `orange` - 橙色
- `purple` - 紫色
- `wathet` - 浅蓝色
- `carmine` - 胭脂红
- `violet` - 紫罗兰
- `indigo` - 靛蓝

### 2. 修改标题样式

在 `format_ai_report_to_feishu_card()` 函数中：

```python
"header": {
    "title": {
        "tag": "plain_text",
        "content": f"🤖 AI选题日报 - {date}"  # 👈 修改标题文字
    },
    "template": "blue"
}
```

### 3. 修改各部分的图标和标题

**修改"今日概览"部分**：

在 `build_overview_section()` 函数中：

```python
def build_overview_section(statistics):
    """构建今日概览部分"""
    lines = [
        "📊 **今日概览**",  # 👈 修改图标或标题
        f"• 分析文章数: {statistics.get('total_articles', 0)}",
        f"• 订阅账号数: {statistics.get('accounts_count', 0)}",
    ]
    return create_markdown_element("\n".join(lines))
```

**修改"选题灵感"部分**：

在 `build_inspiration_section()` 函数中：

```python
elements = [
    create_markdown_element("💡 **选题灵感**")  # 👈 修改这里
]
```

**其他部分同理**：
- `build_deep_reading_section()` - 修改 "📚 **深度阅读推荐**"
- `build_hot_topics_section()` - 修改 "🔥 **本周热点话题**"

### 4. 添加新的内容字段

假设你想在"今日概览"中添加"高价值文章数"：

```python
def build_overview_section(statistics):
    """构建今日概览部分"""
    lines = [
        "📊 **今日概览**",
        f"• 分析文章数: {statistics.get('total_articles', 0)}",
        f"• 订阅账号数: {statistics.get('accounts_count', 0)}",
        f"• 高价值文章: {statistics.get('high_value_count', 0)}",  # 👈 新增
    ]
    return create_markdown_element("\n".join(lines))
```

### 5. 修改选题灵感的显示格式

在 `build_inspiration_section()` 函数中修改：

```python
for i, topic in enumerate(inspirations, 1):
    lines = [
        f"**{i}. {topic.get('title', '')}**",
        f"📐 角度: {topic.get('angle', '')}",      # 可以修改图标
        f"🎯 目标: {topic.get('target', '')}",    # 可以修改图标
        f"💎 价值: {topic.get('value', '')}",     # 可以修改图标
    ]
    
    # 如果想添加新字段，例如"难度"：
    # if topic.get('difficulty'):
    #     lines.append(f"⚡ 难度: {topic.get('difficulty')}")
```

### 6. 自定义分割线样式

分割线目前是简单的 `<hr>`，如果需要更复杂的样式，可以：

**方案1：使用空行代替**
```python
def create_spacer_element():
    """创建空白间隔"""
    return create_plain_text_element("")
```

**方案2：使用装饰性文本**
```python
def create_divider_element():
    """创建装饰性分割线"""
    return create_markdown_element("---")
```

### 7. 添加按钮（交互元素）

如果需要添加可点击的按钮：

```python
def create_button_element(text, url):
    """创建按钮元素"""
    return {
        "tag": "action",
        "actions": [
            {
                "tag": "button",
                "text": {
                    "tag": "plain_text",
                    "content": text
                },
                "type": "primary",  # primary, default, danger
                "url": url
            }
        ]
    }

# 在主函数中使用：
# elements.append(create_button_element("查看详细报告", "https://your-report-url"))
```

## 常见自定义场景

### 场景1：改为简洁模式（不显示热点话题）

在 `format_ai_report_to_feishu_card()` 函数中注释掉：

```python
# 4. 热点话题
# topic_elements = build_hot_topics_section(hot_topics)
# if topic_elements:
#     elements.extend(topic_elements)
#     elements.append(create_hr_element())
```

### 场景2：调整元素顺序

在 `format_ai_report_to_feishu_card()` 函数中调整顺序：

```python
# 原顺序：概览 → 灵感 → 阅读 → 话题 → 底部
# 改为：概览 → 阅读 → 灵感 → 话题 → 底部

elements.append(build_overview_section(statistics))
elements.append(create_hr_element())

# 先显示深度阅读
reading_elements = build_deep_reading_section(deep_reading)
if reading_elements:
    elements.extend(reading_elements)
    elements.append(create_hr_element())

# 再显示选题灵感
inspiration_elements = build_inspiration_section(inspirations)
if inspiration_elements:
    elements.extend(inspiration_elements)
    elements.append(create_hr_element())
```

### 场景3：添加折叠展开功能

飞书支持折叠面板，可以这样实现：

```python
def create_collapsible_section(title, content):
    """创建可折叠的内容区域"""
    return {
        "tag": "column_set",
        "flex_mode": "none",
        "background_style": "default",
        "columns": [
            {
                "tag": "column",
                "width": "weighted",
                "weight": 1,
                "elements": [
                    {
                        "tag": "markdown",
                        "content": f"**{title}**\n{content}"
                    }
                ]
            }
        ]
    }
```

### 场景4：使用不同的文本颜色

Markdown支持有限的样式，可以使用：

```python
lines = [
    "**粗体文本**",           # 粗体
    "*斜体文本*",            # 斜体
    "~~删除线文本~~",        # 删除线
    "`代码文本`",            # 代码样式
    "[链接文本](url)",       # 超链接
]
```

## 完整示例：自定义一个"周报"卡片

```python
def format_weekly_report_card(report):
    """自定义周报卡片"""
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {
                "tag": "plain_text",
                "content": f"📅 AI行业周报 - 第{report.get('week')}周"
            },
            "template": "green"  # 使用绿色主题
        },
        "elements": []
    }
    
    # 自定义内容
    elements = [
        create_markdown_element("## 本周数据\n• 阅读量: 5000\n• 点赞数: 300"),
        create_hr_element(),
        create_markdown_element("## 重点关注\n本周AI领域的重大进展..."),
        create_button_element("查看完整报告", "https://example.com/report"),
        create_plain_text_element("📅 生成于 2025-12-29")
    ]
    
    card["elements"] = elements
    return json.dumps(card, ensure_ascii=False)
```

## 测试你的修改

修改后，使用以下命令测试：

```bash
cd /Users/nicolerli/nico/AITools/claude/wxrss_to_feishu
python -c "
from feishu_pusher import format_ai_report_to_feishu_card
import json

# 测试数据
test_report = {'date': '2025-12-29', 'statistics': {...}, ...}

# 生成卡片
card_json = format_ai_report_to_feishu_card(test_report)
card = json.loads(card_json)

# 查看结构
print(json.dumps(card, indent=2, ensure_ascii=False))
"
```

## 调试技巧

### 1. 查看生成的JSON结构

```python
card_json = format_ai_report_to_feishu_card(report)
print(json.dumps(json.loads(card_json), indent=2, ensure_ascii=False))
```

### 2. 验证JSON格式

使用在线工具：https://open.feishu.cn/tool/cardbuilder

将生成的JSON复制到卡片搭建工具中预览效果。

### 3. 常见错误

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 卡片不显示 | JSON格式错误 | 检查括号、逗号、引号 |
| 链接不可点击 | URL格式错误 | 使用 `[文本](url)` 格式 |
| 样式不生效 | 不支持的Markdown | 只用基础语法 |
| 元素太多卡片太长 | 内容过多 | 精简内容或分段 |

## 相关资源

- 📖 [飞书卡片搭建工具](https://open.feishu.cn/tool/cardbuilder)
- 📖 [飞书消息卡片设计规范](https://open.feishu.cn/document/ukTMukTMukTM/uAzMwUjLwMDM14CMzATN)
- 📖 [Markdown语法支持](https://open.feishu.cn/document/ukTMukTMukTM/uYjNwUjL2YDM14iN2ATN)

---

**更新日期**: 2025-12-29  
**版本**: v2.0 (重构版)

