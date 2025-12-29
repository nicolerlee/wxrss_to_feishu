# 📊 飞书多维表格配置指南

## 🎯 功能说明

将清洗后的文章数据保存到飞书多维表格，方便：
- 📝 集中管理所有文章
- 🔍 搜索和筛选
- 🏷️ 分类和标记
- 📊 数据分析和统计

---

## 📋 第1步：创建多维表格

### 1. 在飞书中创建多维表格

打开飞书 → 点击「+」→ 选择「多维表格」

### 2. 创建以下字段

| 字段名 | 字段类型 | 说明 | 是否必需 |
|--------|---------|------|---------|
| 📰 标题 | 单行文本 | 文章标题 | ✅ 必需 |
| ✍️ 作者 | 单行文本 | 公众号名称 | ✅ 必需 |
| 🔗 链接 | URL | 文章链接 | ✅ 必需 |
| 📅 发布时间 | 日期 | 文章发布时间 | ✅ 必需 |
| 📝 内容 | 多行文本 | Markdown格式内容 | ✅ 必需 |
| 🔢 字数 | 数字 | 文章字数 | ✅ 必需 |
| ⏰ 采集时间 | 日期 | 数据采集时间 | ✅ 必需 |
| 📋 摘要 | 多行文本 | 文章摘要 | 可选 |
| 🏷️ 标签 | 多选 | 自定义标签 | 可选 |
| ⭐ 评分 | 评分 | 文章质量评分 | 可选 |

**⚠️ 重要：字段名必须完全匹配（包括emoji），否则数据无法插入！**

---

## 🔑 第2步：获取表格参数

### 获取 `app_token` 和 `table_id`

打开你创建的多维表格，查看URL：

```
https://xxx.feishu.cn/base/BBYpbAWEbawNUgsmcI9cOlYqnSc?table=tbldmogzEjRdaqeH&view=vewRRKLYVW
```

提取参数：
- `base/` 后面的部分 → **app_token**: `BBYpbAWEbawNUgsmcI9cOlYqnSc`
- `table=` 后面的部分 → **table_id**: `tbldmogzEjRdaqeH`

---

## ⚙️ 第3步：配置应用权限

### 1. 打开飞书开放平台

访问：https://open.feishu.cn/app/

找到你的应用（如果没有，参考[USAGE_GUIDE.md](./USAGE_GUIDE.md)创建）

### 2. 开通多维表格权限

进入「权限管理」，搜索并开通：

- ✅ `bitable:app` - 查看、评论和编辑多维表格
- ✅ `bitable:app:readonly` - 查看多维表格（只读）

**然后点击「发布版本」使权限生效！**

### 3. 添加协作者

在多维表格中：
1. 点击右上角「分享」
2. 添加协作者 → 搜索你的应用名称
3. 设置权限为「可编辑」

---

## 🔧 第4步：配置项目

编辑 `config.py`：

```python
# ==================== 飞书配置 ====================
FEISHU_APP_ID = "cli_a9c0bcb966389ccd"  # 你的应用ID
FEISHU_APP_SECRET = "xxx"  # 你的应用密钥

# 飞书群ID（如果需要推送群消息）
FEISHU_CHAT_ID = "oc_xxx"

# 推送方式
FEISHU_PUSH_MODE = "bitable"  # 只保存到多维表格
# FEISHU_PUSH_MODE = "both"   # 同时推送群+表格
# FEISHU_PUSH_MODE = "group"  # 只推送群（传统方式）

# ===== 多维表格配置 =====
FEISHU_BITABLE_APP_TOKEN = "BBYpbAWEbawNUgsmcI9cOlYqnSc"  # 从URL获取
FEISHU_BITABLE_TABLE_ID = "tbldmogzEjRdaqeH"  # 从URL获取
```

---

## 🧪 第5步：测试

```bash
cd wechatrss
source venv/bin/activate

# 测试多维表格插入
python test_bitable.py
```

如果配置正确，你会在多维表格中看到3条测试数据！

---

## 🚀 第6步：正式运行

```bash
# 运行完整流程
python main.py
```

根据 `FEISHU_PUSH_MODE` 的配置：
- `bitable` → 只保存到多维表格（不做AI分析）
- `both` → 保存表格 + AI分析 + 推送群
- `group` → 只AI分析 + 推送群（不保存表格）

---

## 🔍 常见问题

### Q1: 插入数据失败，提示 403 权限不足

**A:** 检查以下几点：
1. 应用是否开通了 `bitable:app` 权限
2. 应用是否已发布版本
3. 应用是否被添加为多维表格的协作者
4. 协作者权限是否为「可编辑」

### Q2: 插入数据失败，提示字段不存在

**A:** 检查多维表格中的字段名是否与代码中完全一致：
- 字段名：`标题`、`作者`、`链接`、`内容`、`字数`、`发布时间`、`采集时间`
- 必须完全匹配（包括emoji）

如果字段名不一致，需要修改 `feishu_bitable.py` 中的 `format_article_for_bitable` 函数。

### Q3: 如何自定义表格字段？

**A:** 修改 `feishu_bitable.py` 中的 `format_article_for_bitable` 函数：

```python
def format_article_for_bitable(article):
    record = {
        "你的字段名1": article.get('title', ''),
        "你的字段名2": article.get('author', ''),
        # ... 添加更多字段
    }
    return record
```

### Q4: 如何查看详细的API调用日志？

**A:** 运行测试时添加 `check_fields=True`：

```python
# 在 test_bitable.py 中
save_articles_to_feishu_bitable(
    articles=articles,
    app_id=config.FEISHU_APP_ID,
    app_secret=config.FEISHU_APP_SECRET,
    app_token=config.FEISHU_BITABLE_APP_TOKEN,
    table_id=config.FEISHU_BITABLE_TABLE_ID,
    check_fields=True  # 显示表格字段信息
)
```

### Q5: 数据太多，插入很慢怎么办？

**A:** 飞书API限制每次最多插入500条记录。如果数据量很大：
1. 代码已自动分批处理
2. 可以调整 `MIN_WORD_COUNT` 减少文章数量
3. 可以在 `feishu_bitable.py` 中调整批次大小

---

## 📚 参考文档

- [飞书多维表格API文档](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/batch_create)
- [飞书开放平台](https://open.feishu.cn/)
- [如何获取多维表格权限](https://open.feishu.cn/document/server-docs/docs/bitable-v1/notification)

---

## 💡 使用建议

1. **先测试，再正式运行**
   - 使用 `test_bitable.py` 验证配置
   - 检查表格字段是否匹配
   
2. **定期清理数据**
   - 多维表格容量有限
   - 可以定期导出历史数据
   
3. **善用筛选和视图**
   - 创建不同的视图来组织数据
   - 使用筛选器找到高质量文章
   
4. **配合AI分析使用**
   - 设置 `FEISHU_PUSH_MODE = "both"`
   - 既有原始数据，又有AI分析报告

---

## 🎉 完成！

现在你可以每天自动收集和管理公众号文章了！

有问题？查看 [USAGE_GUIDE.md](./USAGE_GUIDE.md) 或者告诉我！ 🚀

