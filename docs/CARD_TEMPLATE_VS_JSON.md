# 飞书消息卡片：JSON方式 vs 模板方式

## 两种方式对比

| 特性 | JSON方式（当前） | 模板方式 |
|------|----------------|---------|
| **是否需要卡片ID** | ❌ 不需要 | ✅ 需要（template_id） |
| **灵活性** | ⭐⭐⭐⭐⭐ 完全自由 | ⭐⭐⭐ 受模板限制 |
| **维护成本** | 在代码中维护 | 在飞书后台维护 |
| **数据传输量** | 每次发送完整JSON | 只传递变量值 |
| **样式修改** | 修改代码 | 在后台修改模板 |
| **适用场景** | 动态内容、复杂逻辑 | 固定格式、频繁使用 |

## 方式1：JSON方式（当前实现）

### 发送内容

```json
{
  "receive_id": "oc_xxx",
  "msg_type": "interactive",
  "content": "{\"config\":{...},\"header\":{...},\"elements\":[...]}"
}
```

### 返回数据

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "message_id": "om_x100b5a115797f0a8c2b8fd5acb42da4",
    "create_time": "1767002517999"
  }
}
```

**可用的ID**：
- `message_id`：消息ID，可用于更新或删除消息

### 代码实现

```python
def format_ai_report_to_feishu_card(report):
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "标题"},
            "template": "blue"
        },
        "elements": [...]
    }
    return json.dumps(card, ensure_ascii=False)

# 发送
content = format_ai_report_to_feishu_card(report)
send_message_to_group(token, chat_id, "interactive", content)
```

## 方式2：模板方式（需要卡片ID）

### 第1步：创建卡片模板

在飞书开放平台创建卡片模板，获得 `template_id`（即卡片ID）：

1. 进入[飞书开放平台](https://open.feishu.cn)
2. 选择你的应用 → 消息卡片 → 创建卡片
3. 使用可视化编辑器设计卡片
4. 保存后获得 `template_id`（例如：`ctp_AAq1Xqwrlqmk`）

### 第2步：发送时使用模板ID

```python
def send_card_with_template(token, chat_id, template_id, variables):
    """使用卡片模板发送消息"""
    card = {
        "type": "template",
        "data": {
            "template_id": template_id,
            "template_variable": variables  # 只传变量值
        }
    }
    
    payload = {
        "receive_id": chat_id,
        "msg_type": "interactive",
        "content": json.dumps(card, ensure_ascii=False)
    }
    
    # 发送...
```

### 使用示例

```python
# 变量值
variables = {
    "date": "2025-12-29",
    "total_articles": "15",
    "accounts_count": "8",
    "inspiration_title_1": "AI副业实战",
    "inspiration_angle_1": "从技术到变现的路径",
    # ... 更多变量
}

# 发送
send_card_with_template(
    token=token,
    chat_id=chat_id,
    template_id="ctp_AAq1Xqwrlqmk",  # 卡片模板ID
    variables=variables
)
```

## 如何选择？

### 选择 JSON方式（当前方式）如果：

1. ✅ 内容是动态的，结构不固定
2. ✅ 需要根据数据灵活调整卡片结构
3. ✅ 开发人员掌控所有样式
4. ✅ 不需要在飞书后台管理卡片

**我们的场景**：
- 每天的文章数量不同
- 选题灵感、深度阅读数量不固定
- 需要根据内容动态生成
- **✅ 适合用JSON方式**

### 选择模板方式如果：

1. ✅ 卡片格式相对固定
2. ✅ 需要在飞书后台统一管理样式
3. ✅ 非技术人员也需要修改样式
4. ✅ 同一个模板在多个地方使用
5. ✅ 需要减少发送的数据量

**适合的场景**：
- 日报、周报等固定格式的报告
- 审批流程卡片
- 通知提醒卡片
- 问卷调查卡片

## 实现模板方式的代码示例

如果你想切换到模板方式，可以这样实现：

```python
# feishu_pusher.py 新增

def send_card_with_template(tenant_access_token, chat_id, template_id, template_variables):
    """
    使用卡片模板发送消息
    
    参数:
        tenant_access_token: 访问令牌
        chat_id: 群ID
        template_id: 卡片模板ID（在飞书后台创建卡片后获得）
        template_variables: 模板变量字典
    """
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    
    # 构建卡片内容
    card_content = {
        "type": "template",
        "data": {
            "template_id": template_id,
            "template_variable": template_variables
        }
    }
    
    payload = {
        "receive_id": chat_id,
        "msg_type": "interactive",
        "content": json.dumps(card_content, ensure_ascii=False)
    }
    
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def format_report_to_template_variables(report):
    """
    将报告转换为模板变量
    
    参数:
        report: AI分析报告
    
    返回:
        模板变量字典
    """
    variables = {
        "date": report.get("date", ""),
        "total_articles": str(report.get("statistics", {}).get("total_articles", 0)),
        "accounts_count": str(report.get("statistics", {}).get("accounts_count", 0)),
    }
    
    # 选题灵感（假设模板支持3个选题）
    inspirations = report.get("inspirations", [])
    for i, topic in enumerate(inspirations[:3], 1):
        variables[f"inspiration_title_{i}"] = topic.get("title", "")
        variables[f"inspiration_angle_{i}"] = topic.get("angle", "")
        variables[f"inspiration_target_{i}"] = topic.get("target", "")
        variables[f"inspiration_value_{i}"] = topic.get("value", "")
    
    # 深度阅读（假设模板支持3篇）
    deep_reading = report.get("deep_reading", [])
    for i, article in enumerate(deep_reading[:3], 1):
        variables[f"article_title_{i}"] = article.get("article_title", "")
        variables[f"article_url_{i}"] = article.get("article_url", "")
        variables[f"article_source_{i}"] = article.get("source", "")
        variables[f"article_score_{i}"] = str(article.get("score", 0))
        variables[f"article_recommendation_{i}"] = article.get("recommendation", "")
    
    return variables


def push_report_with_template(report, app_id, app_secret, chat_id, template_id):
    """
    使用模板方式推送报告
    
    参数:
        report: AI分析报告
        app_id: 飞书应用ID
        app_secret: 飞书应用Secret
        chat_id: 飞书群ID
        template_id: 卡片模板ID
    """
    # 获取token
    token = get_tenant_access_token(app_id, app_secret)
    
    # 转换为模板变量
    variables = format_report_to_template_variables(report)
    
    # 发送
    result = send_card_with_template(token, chat_id, template_id, variables)
    
    return result
```

## 更新已发送的消息

无论使用哪种方式，都可以使用 `message_id` 更新消息：

```python
def update_message_card(tenant_access_token, message_id, new_card_json):
    """更新已发送的消息卡片"""
    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}"
    
    payload = {
        "content": new_card_json
    }
    
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    response = requests.patch(url, json=payload, headers=headers)
    return response.json()
```

## 推荐方案

**对于我们的项目，建议继续使用JSON方式**，原因：

1. ✅ 内容结构动态变化（文章数量不固定）
2. ✅ 完全的代码控制，便于版本管理
3. ✅ 不需要额外创建和维护模板
4. ✅ 已经实现得很好，代码清晰

**如果未来需要**：
- 多个不同的报告样式（日报、周报、月报）
- 非技术人员修改样式
- 在多个项目中复用同一套卡片

那时候再考虑切换到模板方式。

## 参考资料

- [发送消息API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create)
- [消息卡片搭建指南](https://open.feishu.cn/document/ukTMukTMukTM/uYjNwUjL2YDM14iN2ATN)
- [卡片模板使用指南](https://open.feishu.cn/document/ukTMukTMukTM/uEjNwUjLxYDM14SM2ATN)

---

**结论**：我们当前不需要卡片ID，使用的是JSON直接发送方式，发送后获得的是消息ID（message_id）。

