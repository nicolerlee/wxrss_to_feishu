# 🚀 WeChat RSS → AI选题日报 使用指南

## 📋 项目简介

这是一个自动化的微信公众号内容聚合和分析系统，可以：
- 📡 自动爬取订阅的微信公众号文章
- 🧹 智能清洗数据（HTML → Markdown）
- 📊 保存到飞书多维表格（便于管理）
- 🤖 AI分析生成选题日报
- 📱 推送到飞书群聊

---

## 🎯 三种工作模式

### 模式1：只收集数据（免费）
**配置：** `FEISHU_PUSH_MODE = "bitable"`

**流程：**
```
爬取文章 → 清洗数据 → 保存到多维表格
```

**适用场景：**
- 建立文章数据库
- 手动筛选和分析
- 节省AI成本

---

### 模式2：只生成AI报告
**配置：** `FEISHU_PUSH_MODE = "group"`

**流程：**
```
爬取文章 → 清洗数据 → AI分析 → 推送到群聊
```

**适用场景：**
- 每天看AI生成的选题灵感
- 不需要保存原始文章
- 快速获取内容洞察

**成本：** 约 ¥0.03/天（DeepSeek）

---

### 模式3：全功能（推荐）
**配置：** `FEISHU_PUSH_MODE = "both"`

**流程：**
```
爬取文章 → 清洗数据 → 保存到多维表格 → AI分析 → 推送到群聊
```

**适用场景：**
- 既要数据备份，又要AI分析
- 最完整的解决方案

**成本：** 约 ¥0.03/天（DeepSeek）

---

## 🚀 快速开始

### 前置条件

1. **Docker Desktop**（用于运行 wechat2rss 服务）
2. **Python 3.8+**
3. **飞书企业应用**
4. **DeepSeek API Key**（推荐）或 Claude/OpenAI

---

### 第1步：启动 RSS 服务

```bash
cd wechatrss

# 启动 Docker Desktop（GUI操作）

# 启动 wechat2rss 服务
docker-compose up -d

# 验证服务
curl http://localhost:8081/
```

---

### 第2步：配置飞书应用

#### 2.1 创建飞书企业应用
1. 访问：https://open.feishu.cn/app/
2. 点击「创建企业自建应用」
3. 填写应用名称（如：AI选题日报）
4. 点击「创建」

#### 2.2 获取应用凭证
1. 进入应用详情页
2. 在「凭证与基础信息」中复制：
   - `App ID`
   - `App Secret`

#### 2.3 开通权限

**如果使用群推送（模式2或3）：**
- ✅ `im:message` - 获取与发送消息
- ✅ `im:message:send_as_bot` - 以应用身份发消息

**如果使用多维表格（模式1或3）：**
- ✅ `bitable:app` - 查看、评论和编辑多维表格
- ✅ `base:record:create` - 新增记录

**⚠️ 开通权限后必须点击「发布版本」！**

#### 2.4 添加到群聊（如需群推送）
1. 在飞书创建/打开一个群
2. 群设置 → 群机器人 → 添加机器人
3. 搜索你的应用名称，添加

#### 2.5 获取群ID（如需群推送）
- 飞书网页版打开群聊
- URL中找到 `oc_xxxxx` 格式的ID

#### 2.6 配置多维表格（如需表格保存）

**创建多维表格字段：**

| 字段名 | 字段类型 | 必需 |
|--------|---------|------|
| 标题 | 单行文本 | ✅ |
| 作者 | 单行文本 | ✅ |
| 链接 | URL | ✅ |
| 发布时间 | 日期 | ✅ |
| 摘要 | 多行文本 | 可选 |
| 内容 | 多行文本 | ✅ |
| 字数 | 数字 | ✅ |
| 采集时间 | 日期 | ✅ |

**获取表格参数：**
- 打开表格，从 URL 提取：
  - `app_token`: `base/` 后面的部分
  - `table_id`: `table=` 后面的部分

**添加应用为协作者：**
1. 表格右上角「分享」
2. 添加你的应用
3. 权限设为「可编辑」

详细教程：参考 [BITABLE_GUIDE.md](./BITABLE_GUIDE.md)

---

### 第3步：配置项目

```bash
# 安装虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp config.example.py config.py

# 编辑配置
nano config.py  # 或用你喜欢的编辑器
```

**配置示例：**

```python
# ==================== RSS配置 ====================
RSS_DOMAIN = "http://localhost:8081"
OPML_FILE = "wechat2rss_subscriptions.opml"

# ==================== AI配置 ====================
AI_PROVIDER = "deepseek"
DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxx"  # 从 https://platform.deepseek.com/ 获取

# ==================== 飞书配置 ====================
FEISHU_APP_ID = "cli_xxxxxxxxxxxx"
FEISHU_APP_SECRET = "xxxxxxxxxxxxx"

# 群ID（如果用群推送）
FEISHU_CHAT_ID = "oc_xxxxxxxxxxxx"

# 推送模式：bitable（只存表）/ group（只推群）/ both（都要）
FEISHU_PUSH_MODE = "both"  

# 多维表格配置（如果用表格保存）
FEISHU_BITABLE_APP_TOKEN = "BBYpbAWEbawNUgsmcI9cOlYqnSc"
FEISHU_BITABLE_TABLE_ID = "tbldmogzEjRdaqeH"

# ==================== 数据过滤配置 ====================
MIN_WORD_COUNT = 500  # 最小字数
```

---

### 第4步：验证配置

```bash
python check_config.py
```

如果看到：
```
🎉 所有配置检查通过！
```

就可以运行了！

---

### 第5步：运行

```bash
python main.py
```

**预期输出：**
```
第1步: 📡 爬取RSS文章 ✅
第2步: 🧹 清洗数据 ✅
第3步: 📊 保存到多维表格 ✅  (如果配置了)
第4步: 🤖 AI分析 ✅  (如果配置了)
第5步: 📱 推送到飞书群 ✅  (如果配置了)
```

---

## 📊 技术架构

### 核心技术栈

| 技术 | 用途 | 说明 |
|------|------|------|
| **wechat2rss** | RSS源 | Docker服务，将公众号转为RSS |
| **feedparser** | RSS解析 | Python库，解析RSS Feed |
| **BeautifulSoup4** | HTML解析 | 清理HTML标签 |
| **markdownify** | 格式转换 | HTML → Markdown |
| **DeepSeek API** | AI分析 | 最便宜的大模型（推荐）|
| **飞书开放平台** | 数据推送 | 群消息 + 多维表格 |

### 数据流程

```
RSS Feed (XML)
    ↓ feedparser
原始文章数据 (Dict)
    ↓ BeautifulSoup4 + markdownify
Markdown 格式文章
    ↓ 过滤 + 去重
清洗后的文章
    ↓
    ├─→ 飞书多维表格 (原始数据备份)
    └─→ DeepSeek API (AI分析)
            ↓
        AI选题日报
            ↓
        飞书群消息 (富文本)
```

### 文件结构

```
wechatrss/
├── 📄 核心模块
│   ├── main.py                      # 主程序入口
│   ├── rss_fetcher.py              # RSS爬取
│   ├── data_cleaner.py             # 数据清洗（Markdown）
│   ├── ai_analyzer.py              # AI分析
│   ├── feishu_pusher.py            # 飞书群推送
│   ├── feishu_bitable.py           # 飞书多维表格
│   └── utils.py                    # 工具函数
│
├── ⚙️ 配置
│   ├── config.py                   # 实际配置（需创建）
│   ├── config.example.py           # 配置模板
│   ├── wechat2rss_subscriptions.opml  # RSS订阅源
│   └── docker-compose.yml          # Docker配置
│
├── 📝 文档
│   └── docs/prompts/analyze_prompt.md    # AI分析提示词
│
├── 🔧 工具
│   ├── check_config.py             # 配置检查
│   └── requirements.txt            # Python依赖
│
└── 📖 文档
    ├── README.md                   # 项目说明
    ├── USAGE_GUIDE.md             # 使用指南（本文档）
    └── BITABLE_GUIDE.md           # 多维表格配置指南
```

---

## 🎯 常见问题

### Q1: Docker服务启动失败
**A:** 
```bash
# 检查 Docker 是否运行
docker ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart
```

### Q2: RSS爬取失败，503错误
**A:** 
- 检查 `config.py` 中的 `RSS_DOMAIN`
- 应该是 `http://localhost:8081`，不是 IP 地址
- 确认 wechat2rss 服务正在运行

### Q3: 飞书推送失败，权限不足
**A:** 
1. 检查应用权限是否开通
2. **必须点击「发布版本」**
3. 等待1-2分钟让权限生效

### Q4: 多维表格插入失败
**A:** 
1. 检查字段名是否完全匹配
2. 应用是否添加为表格协作者
3. 权限是否为「可编辑」

### Q5: AI分析太慢或太贵
**A:** 
- 使用 DeepSeek：速度快，成本低（¥0.03/次）
- 调整 `MIN_WORD_COUNT` 减少文章数量
- 使用模式1（只收集）+ 手动分析

### Q6: 如何修改AI提示词
**A:** 
编辑 `docs/prompts/analyze_prompt.md` 文件，根据需求调整分析标准和输出格式。

### Q7: 如何添加更多公众号
**A:** 
1. 在 wechat2rss 网页（http://localhost:8081）添加公众号
2. 导出订阅源，替换 `wechat2rss_subscriptions.opml`
3. 或手动编辑 OPML 文件添加 RSS Feed URL

---

## 🔧 高级配置

### 自定义过滤规则

编辑 `config.py`：

```python
# 文章最小字数
MIN_WORD_COUNT = 500

# 是否保存原始JSON（调试用）
SAVE_RAW_DATA = False
```

### 切换AI提供商

```python
# 使用 DeepSeek（推荐，便宜）
AI_PROVIDER = "deepseek"
DEEPSEEK_API_KEY = "sk-xxx"

# 使用 Claude（质量好，贵）
AI_PROVIDER = "claude"
CLAUDE_API_KEY = "sk-ant-xxx"

# 使用 OpenAI
AI_PROVIDER = "openai"
OPENAI_API_KEY = "sk-xxx"
```

### 添加定时任务

**方法1：使用 crontab（推荐）**

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天早上8点）
0 8 * * * cd /path/to/wechatrss && source venv/bin/activate && python main.py >> logs/cron.log 2>&1
```

**方法2：使用 schedule 库**

自己写一个调度脚本（需要时我可以帮你）

---

## 💰 成本分析

### DeepSeek（推荐）
- **输入**：¥0.001 / 1K tokens
- **输出**：¥0.002 / 1K tokens
- **每次运行**：约 ¥0.03
- **每月**：¥0.9（每天一次）

### OpenAI GPT-4o-mini
- **每次运行**：约 ¥0.1
- **每月**：¥3（每天一次）

### Claude
- **每次运行**：约 ¥0.3
- **每月**：¥9（每天一次）

### 飞书API
- **完全免费** ✅

---

## 📚 相关文档

- [飞书开放平台文档](https://open.feishu.cn/document/)
- [DeepSeek API文档](https://platform.deepseek.com/docs)
- [wechat2rss 项目](https://github.com/ttttmr/wechat2rss)
- [多维表格配置指南](./BITABLE_GUIDE.md)

---

## 🎉 完成！

现在你的AI选题日报系统已经可以运行了！

**推荐工作流：**

1. **每天自动运行** - 设置 crontab 定时任务
2. **早上查看** - 飞书群收到AI报告
3. **深入研究** - 在多维表格中查看原文
4. **创作内容** - 基于AI洞察创作

享受你的AI助手吧！ 🚀

---

**有问题？**
- 查看 [BITABLE_GUIDE.md](./BITABLE_GUIDE.md) 了解多维表格配置
- 运行 `python check_config.py` 检查配置
- 查看项目 README.md
