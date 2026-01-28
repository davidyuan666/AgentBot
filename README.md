# AgentBot - Python版

一个支持多平台接入（Telegram、QQ、微信）的AI助手机器人，集成DeepSeek中文大语言模型，支持Windows电脑控制。

## 功能特性

✨ **多平台支持**
- Telegram 机器人
- QQ 机器人 (CQHTTP)
- 微信 机器人

🤖 **AI能力**
- 集成 DeepSeek 中文LLM
- 自然语言对话
- 会话历史管理

🖥️ **Windows电脑控制**
- 执行系统命令
- 应用程序启动
- 鼠标键盘控制
- 系统信息查询
- 截图功能
- 系统关闭/重启

## 安装

1. **克隆仓库**
```bash
cd AgentBot
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Slack:
Bot Token权限
chat:write
app_mentions:read
channels:history
im:history
groups:history
mpim:history