#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config import config
import time

print("\n" + "="*60)
print("Socket Mode 连接测试")
print("="*60 + "\n")

# 检查 Token
if not config.SLACK_APP_TOKEN:
    print("❌ SLACK_APP_TOKEN 未配置")
    exit(1)

print(f"✅ SLACK_APP_TOKEN: {config.SLACK_APP_TOKEN[:30]}...")
print(f"✅ SLACK_BOT_TOKEN: {config.SLACK_BOT_TOKEN[:30]}...")

# 创建应用
app = App(
    token=config.SLACK_BOT_TOKEN,
    signing_secret=config.SLACK_SIGNING_SECRET
)

# 添加消息处理器 - 最简单的版本
message_count = 0

@app.message()
def handle_message(message, say, logger):
    """处理所有消息"""
    global message_count
    message_count += 1
    
    text = message.get("text", "")
    user = message.get("user", "unknown")
    
    print(f"\n{'='*60}")
    print(f"✅ 第 {message_count} 条消息")
    print(f"{'='*60}")
    print(f"用户: {user}")
    print(f"内容: {text}")
    print(f"{'='*60}\n")
    
    # 回复
    say(f"机器人收到: {text}")

# 启动
print("\n正在启动 Socket Mode...\n")

try:
    handler = SocketModeHandler(app, config.SLACK_APP_TOKEN)
    print("✅ Socket Mode 已连接！\n")
    print("请在 Slack 中发送消息...\n")
    handler.start()
except Exception as e:
    print(f"❌ 连接失败: {e}")
    import traceback
    traceback.print_exc()