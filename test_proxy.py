#!/usr/bin/env python3

import os
from config import config
from slack_sdk import WebClient

print(f"代理: {config.SLACK_PROXY_URL}")

# 设置代理
os.environ['http_proxy'] = config.SLACK_PROXY_URL
os.environ['https_proxy'] = config.SLACK_PROXY_URL

client = WebClient(token=config.SLACK_BOT_TOKEN)

try:
    result = client.auth_test()
    print(f"✅ 代理工作正常！")
    print(f"✅ 机器人: {result['user_id']}")
except Exception as e:
    print(f"❌ 代理连接失败: {e}")