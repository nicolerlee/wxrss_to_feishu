# 微信公众号RSS → AI选题日报系统

自动爬取微信公众号文章，AI智能分析生成每日选题日报，推送到飞书。

---

## ✨ 功能特点

### 核心功能
- 📡 **自动爬取**: 基于RSS订阅，自动获取公众号文章
- 🧹 **智能清洗**: HTML → Markdown，去广告，保留结构
- 🤖 **AI分析**: 生成选题灵感、深度阅读推荐、数据统计
- 📊 **多维表格**: 保存到飞书多维表格，方便管理和检索
- 📱 **群消息推送**: AI报告自动推送到飞书群聊
- ⚙️ **三种模式**: bitable（只存表）/ group（只推群）/ both（都要）

### 技术特点
- ✅ 无需数据库，配置简单
- ✅ 模块化设计，易于扩展
- ✅ 完整的错误处理和日志
- ✅ 配置检查工具，自动诊断
- ✅ 成本可控（¥0.03/天，使用DeepSeek）

---

## 🚀 快速开始

### 前置条件

1. **Docker Desktop**（运行wechat2rss服务）
2. **Python 3.8+**
3. **飞书企业应用**
4. **AI API Key**（推荐DeepSeek）

### 5分钟快速部署

```bash
# 1. 启动RSS服务
cd wechatrss
docker-compose up -d

# 2. 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 配置
cp config.example.py config.py
# 编辑 config.py，填入API密钥

# 4. 检查配置
python check_config.py

# 5. 运行
python main.py
```

详细配置步骤请查看 [使用指南](./docs/USAGE_GUIDE.md)

---

## 📊 工作模式

### 模式1：只收集数据（免费）
**配置**: `FEISHU_PUSH_MODE = "bitable"`

```
爬取 → 清洗 → 保存到多维表格
```

适合建立文章数据库，手动筛选分析

---

### 模式2：只生成AI报告
**配置**: `FEISHU_PUSH_MODE = "group"`

```
爬取 → 清洗 → AI分析 → 推送到群聊
```

适合快速获取AI洞察，不需要原始数据

**成本**: ~¥0.03/天（DeepSeek）

---

### 模式3：全功能（推荐）
**配置**: `FEISHU_PUSH_MODE = "both"`

```
爬取 → 清洗 → 保存到多维表格 + AI分析 → 推送到群聊
```

既要数据备份，又要AI分析

---

## 📂 项目结构

```
wechatrss/
├── 🔧 核心模块
│   ├── main.py                      # 主程序
│   ├── rss_fetcher.py              # RSS爬取
│   ├── data_cleaner.py             # 数据清洗（Markdown）
│   ├── ai_analyzer.py              # AI分析
│   ├── feishu_pusher.py            # 飞书群推送
│   ├── feishu_bitable.py           # 飞书多维表格
│   ├── check_config.py             # 配置检查
│   └── utils.py                    # 工具函数
│
├── ⚙️ 配置
│   ├── config.py                   # 实际配置（需创建）
│   ├── config.example.py           # 配置模板
│   ├── docker-compose.yml          # Docker配置
│   └── wechat2rss_subscriptions.opml  # RSS订阅源
│
└── 📖 文档
    ├── README.md                       # 项目说明（本文档）
    └── docs/                          # 文档目录
        ├── USAGE_GUIDE.md             # 使用指南
        ├── BITABLE_GUIDE.md           # 多维表格配置指南
        ├── PROJECT_RETROSPECTIVE.md   # 项目复盘与最佳实践
        └── prompts/                   # 提示词目录
            └── analyze_prompt.md       # AI分析提示词 ⭐
```

---

## 🎯 核心功能详解

### 1. RSS爬取

从wechat2rss服务获取公众号文章，自动过滤24小时内发布的内容。

**关键模块**: `rss_fetcher.py`

```python
# 获取昨天的文章
articles = fetch_rss_articles(
    opml_file="wechat2rss_subscriptions.opml",
    rss_domain="http://localhost:8081",
    filter_24h=True
)
```

---

### 2. 数据清洗

将HTML转为Markdown，去除广告，保留图片和结构。

**关键模块**: `data_cleaner.py`

**处理流程**:
- HTML → Markdown（使用 markdownify）
- 去除广告内容（正则匹配）
- 去重（基于URL和标题）
- 过滤低质量（字数<500）

**为什么用Markdown？**
- 保留文章结构（标题、列表、引用）
- AI理解更准确
- 节省Token成本（比HTML简洁）

---

### 3. AI分析

使用大语言模型分析文章，生成选题日报。

**关键模块**: `ai_analyzer.py`, `prompt/analyze_prompt.md`

**AI任务**:
1. 统计数据（文章数、公众号数、高价值文章数）
2. 生成3个选题灵感（可商业化的角度）
3. 推荐3篇深度阅读（实操价值高的）

**支持的AI提供商**:
- DeepSeek（推荐，¥0.03/次）
- OpenAI（¥0.1/次）
- Claude（¥0.3/次）

**如何调整提示词？**

编辑 `prompt/analyze_prompt.md`：

```markdown
# 想要更多选题
修改: ### 任务2：生成选题灵感（精选3个）
改为: ### 任务2：生成选题灵感（精选5个）

# 改变评分权重
实用性 50% ← 提高
深度   20% ← 降低

# 调整目标读者
修改: 这份日报的读者是：AI从业者、产品经理...
改为: 这份日报的读者是：企业管理者、投资人...
```

---

### 4. 飞书推送

#### 4.1 群消息推送

**关键模块**: `feishu_pusher.py`

将AI报告格式化为富文本消息，推送到飞书群聊。

**消息格式**:
- 📊 数据统计（卡片）
- 💡 选题灵感（列表）
- 📖 深度阅读推荐（链接）

---

#### 4.2 多维表格存储

**关键模块**: `feishu_bitable.py`

将清洗后的文章保存到飞书多维表格，方便后续检索。

**表格字段**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 标题 | 单行文本 | 文章标题 |
| 作者 | 单行文本 | 公众号名称 |
| 链接 | URL | 原文链接 |
| 发布时间 | 日期 | 发布时间戳 |
| 摘要 | 多行文本 | 文章摘要（200字） |
| 内容 | 多行文本 | Markdown格式正文 |
| 字数 | 数字 | 文章字数 |
| 采集时间 | 日期 | 爬取时间 |

详细配置见 [多维表格指南](./docs/BITABLE_GUIDE.md)

---

## 🔧 配置说明

### 核心配置项

```python
# config.py

# ==================== RSS配置 ====================
RSS_DOMAIN = "http://localhost:8081"
OPML_FILE = "wechat2rss_subscriptions.opml"

# ==================== AI配置 ====================
AI_PROVIDER = "deepseek"  # deepseek/claude/openai
DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxx"

# ==================== 飞书配置 ====================
FEISHU_APP_ID = "cli_xxxxxxxxxxxx"
FEISHU_APP_SECRET = "xxxxxxxxxxxxx"
FEISHU_CHAT_ID = "oc_xxxxxxxxxxxx"  # 群ID

# 推送模式
FEISHU_PUSH_MODE = "both"  # bitable/group/both

# 多维表格（如果PUSH_MODE包含bitable）
FEISHU_BITABLE_APP_TOKEN = "BBYpbAWEbawNUgsmcI9cOlYqnSc"
FEISHU_BITABLE_TABLE_ID = "tbldmogzEjRdaqeH"

# ==================== 数据过滤配置 ====================
MIN_WORD_COUNT = 500  # 最小字数
```

### 配置检查

运行配置检查工具，自动诊断问题：

```bash
python check_config.py
```

---

## 📚 文档导航

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [README.md](./README.md) | 项目概述（本文档） | 所有人 |
| [USAGE_GUIDE.md](./docs/USAGE_GUIDE.md) | 详细使用指南 | 新手用户 |
| [BITABLE_GUIDE.md](./docs/BITABLE_GUIDE.md) | 多维表格配置 | 需要数据存储 |
| [PROJECT_RETROSPECTIVE.md](./docs/PROJECT_RETROSPECTIVE.md) | 项目复盘与最佳实践 | 开发者、项目经理 |
| [analyze_prompt.md](./docs/prompts/analyze_prompt.md) | AI分析提示词 | 想调优AI效果 |

---

## 🎓 项目复盘

这个项目经历了~50轮对话才完成，期间遇到了很多问题和返工。

我们总结了一套**需求梳理最佳实践**，可以让类似项目的开发效率提升60%：

📖 **查看完整复盘**: [PROJECT_RETROSPECTIVE.md](./docs/PROJECT_RETROSPECTIVE.md)

**亮点内容**:
- ✨ 5步需求梳理法
- ✨ 可复用的需求文档模板
- ✨ 10条黄金法则
- ✨ 快速检查清单
- ✨ 实际vs理想对比分析

**适用场景**: AI辅助开发、项目启动、需求梳理

---

## 🔧 常见问题

### Q1: RSS服务启动失败
**A:** 
```bash
# 检查Docker
docker ps

# 查看日志
docker-compose logs -f

# 重启
docker-compose restart
```

### Q2: 飞书推送失败
**A:** 
1. 检查应用权限（`im:message`, `im:message:send_as_bot`）
2. **必须点击「发布版本」**
3. 确认机器人已加入群聊

### Q3: 多维表格插入失败
**A:** 
1. 检查字段名是否完全匹配
2. 应用是否添加为表格协作者（可编辑权限）
3. 权限是否开通（`bitable:app`, `base:record:create`）

### Q4: AI分析太贵
**A:** 
- 使用 DeepSeek（¥0.03/次 vs OpenAI ¥0.1/次）
- 调整 `MIN_WORD_COUNT` 减少文章数量
- 使用模式1（只收集）+ 手动分析

### Q5: 如何添加更多公众号
**A:** 
1. 在 http://localhost:8081 添加公众号
2. 导出订阅源，替换 `wechat2rss_subscriptions.opml`

更多问题见 [USAGE_GUIDE.md](./docs/USAGE_GUIDE.md)

---

## 💰 成本分析

### DeepSeek（推荐）
- **每次运行**: ¥0.03
- **每月**: ¥0.9（每天1次）
- **年成本**: ¥10.8

### OpenAI GPT-4o-mini
- **每次运行**: ¥0.1
- **每月**: ¥3

### Claude
- **每次运行**: ¥0.3
- **每月**: ¥9

### 飞书API
- **完全免费** ✅

---

## 🚀 后续扩展

可以考虑添加的功能：

### 短期（P1）
- [ ] 定时任务（crontab）
- [ ] 错误通知（飞书/邮件）
- [ ] 成本监控

### 中期（P2）
- [ ] 周报/月报汇总
- [ ] 热门关键词词云
- [ ] 特定话题追踪

### 长期（P3）
- [ ] 多账号支持
- [ ] Web管理界面
- [ ] 数据可视化
- [ ] 用户收藏和标注

---

## 📊 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 主要开发语言 |
| Docker | - | wechat2rss服务 |
| feedparser | 6.0.10 | RSS解析 |
| BeautifulSoup4 | 4.12.2 | HTML解析 |
| markdownify | 0.11.6 | HTML→Markdown |
| anthropic | - | Claude API |
| openai | - | OpenAI/DeepSeek API |
| lark-oapi | 1.5.2 | 飞书API |

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

**贡献指南**:
1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📝 License

MIT License - 详见 [LICENSE](./LICENSE) 文件

---

## 🙏 致谢

- [wechat2rss](https://github.com/ttttmr/wechat2rss) - 微信公众号RSS服务
- [feedparser](https://feedparser.readthedocs.io/) - RSS解析库
- [markdownify](https://github.com/matthewwithanm/python-markdownify) - HTML转Markdown
- [飞书开放平台](https://open.feishu.cn/) - API支持
- [DeepSeek](https://www.deepseek.com/) - 性价比最高的AI

---

## 📞 联系方式

有问题或建议？

- 📧 Email: [你的邮箱]
- 💬 飞书群: [群号]
- 🐛 Issue: [GitHub Issues](https://github.com/你的用户名/项目名/issues)

---

**⭐ 如果这个项目对你有帮助，请给个Star！**

**📖 强烈推荐阅读**: [项目复盘与最佳实践](./docs/PROJECT_RETROSPECTIVE.md)

---

<div align="center">
Made with ❤️ by [你的名字]
</div>
