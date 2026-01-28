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

## task.md 自动任务（DeepSeek）

你可以让机器人读取本地 `task.md`，调用 DeepSeek 完成任务，然后把结果发送到 Slack。

- **手动触发**：在 Slack 里发送 `task`（或“执行任务”）即可运行 `TASK_MD_PATH` 指向的文件。
- **启动时自动执行**：设置 `TASK_MD_RUN_ON_STARTUP=true`，并配置 `SLACK_TASK_CHANNEL`。

需要在 `.env` 中配置：

- **`TASK_MD_PATH`**：task 文件路径（默认 `task.md`）。
- **`TASK_MD_RUN_ON_STARTUP`**：是否启动时自动执行一次（默认 `false`）。
- **`SLACK_TASK_CHANNEL`**：把结果发到哪个 channel（例如 `#general` 或 channel id `C0123456789`）。