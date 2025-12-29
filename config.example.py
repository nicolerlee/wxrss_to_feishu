"""
配置文件示例
复制此文件为 config.py 并填入你的实际配置
"""

# ==================== RSS配置 ====================
RSS_DOMAIN = "http://192.168.0.121:8081"
OPML_FILE = "wechat2rss_subscriptions.opml"

# ==================== AI配置 ====================
# 选择使用的AI: "deepseek", "claude", "openai"
AI_PROVIDER = "deepseek"

# DeepSeek API配置（推荐：便宜好用）
DEEPSEEK_API_KEY = "sk-xxx"  # 从 https://platform.deepseek.com/ 获取
DEEPSEEK_MODEL = "deepseek-chat"  # 最新最好的模型
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# Claude API配置
CLAUDE_API_KEY = "sk-ant-xxx"  # 从 https://console.anthropic.com/ 获取
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"

# OpenAI API配置（如果使用OpenAI）
OPENAI_API_KEY = "sk-xxx"  # 从 https://platform.openai.com/ 获取
OPENAI_MODEL = "gpt-4o-mini"  # 推荐使用mini版本，便宜
# 如果使用国内代理
OPENAI_BASE_URL = "https://api.openai.com/v1"  # 或其他代理地址

# ==================== 飞书群推送配置 ====================
# 需要在飞书开放平台创建企业应用
FEISHU_APP_ID = "cli_xxx" # https://open.feishu.cn/app/
FEISHU_APP_SECRET = "xxx"
FEISHU_CHAT_ID = "oc_xxx" # 如何获取群ID: https://go.feishu.cn/s/64KYvl2N802

# 推送方式: "group" 推送到群聊, "bitable" 保存到多维表格, "both" 两者都要
FEISHU_PUSH_MODE = "bitable"  # 默认只保存到多维表格

# ===== 多维表格配置（保存清洗后的文章数据）=====
# 从多维表格URL中获取: https://xxx.feishu.cn/base/{app_token}?table={table_id}
FEISHU_BITABLE_APP_TOKEN = "xxx"  # 多维表格的app_token (如: BBYpbAWEbawNUgsmcI9cOlYqnSc)
FEISHU_BITABLE_TABLE_ID = "xxx"  # 数据表的table_id (如: tbldmogzEjRdaqeH)

# ==================== 定时任务配置 ====================
# 每天几点执行（24小时制）
SCHEDULE_TIME = "12:00"

# 是否立即执行一次（测试用）
RUN_IMMEDIATELY = True

# ==================== 数据过滤配置 ====================
# 自动过滤24小时内的文章（在 rss_fetcher.py 中设置）

# 文章最小字数（过滤太短的文章）
MIN_WORD_COUNT = 500

# 注：广告过滤和图片保留已在 data_cleaner.py 中自动处理

# ==================== 输出配置 ====================
# 是否保存本地HTML报告
SAVE_LOCAL_HTML = True
LOCAL_OUTPUT_DIR = "output"

# 是否保存原始数据JSON（调试用）
SAVE_RAW_DATA = False

# ==================== 日志配置 ====================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "wechatrss.log"

