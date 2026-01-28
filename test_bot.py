#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
from config import config
from utils.logger import logger

async def test_config():
    """Test configuration"""
    print("\n" + "="*50)
    print("1. 配置检查")
    print("="*50)
    
    print(f"Telegram Token: {config.TELEGRAM_TOKEN[:20]}... (长度: {len(config.TELEGRAM_TOKEN)})")
    print(f"Telegram Enabled: {config.TELEGRAM_ENABLED}")
    print(f"DeepSeek API Key: {config.DEEPSEEK_API_KEY[:20]}... (长度: {len(config.DEEPSEEK_API_KEY)})")
    print(f"DeepSeek API URL: {config.DEEPSEEK_API_URL}")
    
    if not config.TELEGRAM_TOKEN:
        print("[ERROR] Telegram Token is empty!")
        return False
    if not config.DEEPSEEK_API_KEY:
        print("[ERROR] DeepSeek API Key is empty!")
        return False
    
    print("[OK] 配置检查通过\n")
    return True

async def test_deepseek_api():
    """Test DeepSeek API connection"""
    print("="*50)
    print("2. DeepSeek API 测试")
    print("="*50)
    
    from core.deepseek_api import DeepSeekAPI
    
    api = DeepSeekAPI()
    
    try:
        print("Testing DeepSeek API...")
        response = await api.chat([
            {"role": "system", "content": "你是一个有帮助的助手"},
            {"role": "user", "content": "你好，请说一句简短的问候"}
        ])
        
        print(f"[OK] API Response: {response}")
        await api.close()
        print("[OK] DeepSeek API 测试通过\n")
        return True
        
    except Exception as e:
        print(f"[ERROR] DeepSeek API 测试失败: {type(e).__name__}: {e}")
        await api.close()
        return False

async def test_telegram_connection():
    """Test Telegram bot connection"""
    print("="*50)
    print("3. Telegram 连接测试")
    print("="*50)
    
    try:
        from telegram import Bot
        
        bot = Bot(token=config.TELEGRAM_TOKEN)
        
        print("Testing Telegram bot...")
        me = await bot.get_me()
        
        print(f"[OK] Bot Username: @{me.username}")
        print(f"[OK] Bot Name: {me.first_name}")
        print(f"[OK] Bot ID: {me.id}")
        print("[OK] Telegram 连接测试通过\n")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Telegram 连接测试失败: {type(e).__name__}: {e}")
        return False

async def test_agent():
    """Test Agent"""
    print("="*50)
    print("4. Agent 测试")
    print("="*50)
    
    try:
        from core.agent import Agent
        
        agent = Agent()
        print("[OK] Agent 初始化成功")
        
        print("Testing agent message processing...")
        response = await agent.process_message("test_user", "你好")
        
        print(f"[OK] Agent Response: {response}")
        await agent.close()
        print("[OK] Agent 测试通过\n")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Agent 测试失败: {type(e).__name__}: {e}")
        return False

async def main():
    print("\n" + "="*50)
    print("AgentBot 诊断测试")
    print("="*50 + "\n")
    
    results = []
    
    # Test 1: Config
    result = await test_config()
    results.append(("配置检查", result))
    if not result:
        print("配置有问题，无法继续测试")
        return
    
    # Test 2: DeepSeek API
    result = await test_deepseek_api()
    results.append(("DeepSeek API", result))
    
    # Test 3: Telegram Connection
    result = await test_telegram_connection()
    results.append(("Telegram 连接", result))
    
    # Test 4: Agent
    result = await test_agent()
    results.append(("Agent", result))
    
    # Summary
    print("="*50)
    print("测试总结")
    print("="*50)
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n✅ 所有测试通过！机器人应该能正常工作。")
        print("\n现在运行: python main.py")
    else:
        print("\n❌ 有测试失败。请检查上面的错误信息。")

if __name__ == "__main__":
    asyncio.run(main())