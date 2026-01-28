#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import config

async def test_slack():
    """Test Slack connection"""
    
    print("\n" + "="*60)
    print("Slack 连接诊断")
    print("="*60 + "\n")
    
    # 检查 Token
    if not config.SLACK_BOT_TOKEN or config.SLACK_BOT_TOKEN.startswith("xoxb-你的"):
        print("❌ 错误: SLACK_BOT_TOKEN 未配置或仍为占位符")
        return False
    
    print("✅ SLACK_BOT_TOKEN 已配置")
    print(f"   {config.SLACK_BOT_TOKEN[:20]}...")
    
    # 测试连接
    try:
        client = WebClient(token=config.SLACK_BOT_TOKEN)
        
        # 获取机器人信息
        print("\n[1] 测试机器人身份...")
        auth_test = client.auth_test()
        print(f"✅ 机器人用户: {auth_test['user_id']}")
        print(f"✅ 工作区: {auth_test['team_id']}")
        
        # 列出所有频道
        print("\n[2] 获取可用频道...")
        conversations = client.conversations_list(types="public_channel,private_channel,im")
        
        if conversations['channels']:
            print(f"✅ 找到 {len(conversations['channels'])} 个频道/对话:")
            for channel in conversations['channels'][:5]:
                name = channel.get('name', f"DM (ID: {channel['id']})")
                print(f"   - {name}")
        else:
            print("⚠️  没有找到频道")
        
        # 获取机器人可以访问的频道
        print("\n[3] 获取机器人成员的频道...")
        bot_channels = client.users_conversations(user=auth_test['user_id'], types="public_channel,private_channel,im")
        
        if bot_channels['channels']:
            print(f"✅ 机器人是这些频道的成员:")
            for channel in bot_channels['channels'][:5]:
                name = channel.get('name', f"DM (ID: {channel['id']})")
                print(f"   - {name} (ID: {channel['id']})")
        else:
            print("❌ 机器人不是任何频道的成员！")
            print("   解决方案: 在 Slack 中邀请机器人加入频道")
        
        # 测试发送消息
        print("\n[4] 测试发送消息...")
        if bot_channels['channels']:
            test_channel = bot_channels['channels'][0]['id']
            test_channel_name = bot_channels['channels'][0].get('name', "DM")
            
            try:
                response = client.chat_postMessage(
                    channel=test_channel,
                    text="🤖 AgentBot 连接测试 - 如果你看到这条消息，说明机器人工作正常！"
                )
                print(f"✅ 消息已发送到 #{test_channel_name}")
                print(f"   消息 ID: {response['ts']}")
            except SlackApiError as e:
                print(f"❌ 发送消息失败: {e.response['error']}")
                print(f"   错误详情: {e}")
        
        print("\n" + "="*60)
        print("✅ 诊断完成！")
        print("="*60 + "\n")
        
        return True
        
    except SlackApiError as e:
        print(f"\n❌ Slack API 错误: {e.response['error']}")
        print(f"   详情: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 连接错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_slack())