import asyncio
import sys
import os
from config import config
from core.agent import Agent
from adapters.telegram_adapter import TelegramAdapter
from adapters.qq_adapter import QQAdapter
from adapters.wechat_adapter import WeChatAdapter
from adapters.slack_adapter import SlackAdapter
from utils.logger import logger

async def main():
    """Main entry point"""
    logger.info("=== AgentBot Starting ===")
    logger.info(f"DeepSeek API URL: {config.DEEPSEEK_API_URL}")
    
    # 检测和配置代理
    if config.SLACK_PROXY_HOST and config.SLACK_PROXY_PORT:
        proxy_url = f"{config.SLACK_PROXY_TYPE}://{config.SLACK_PROXY_HOST}:{config.SLACK_PROXY_PORT}"
        logger.info(f"Proxy configured: {proxy_url}")
        print(f"\n✅ 代理已配置: {proxy_url}\n")
        
        # 设置环境变量
        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
    else:
        logger.info("No proxy configured")
        print("\nℹ️  未配置代理\n")
    
    # Initialize agent
    agent = Agent()
    logger.info("Agent initialized")
    
    # Start enabled adapters
    tasks = []
    
    # Telegram
    if config.TELEGRAM_ENABLED:
        logger.info("Telegram enabled")
        print("✅ Telegram 已启用")
        telegram = TelegramAdapter(agent)
        tasks.append(telegram.run())
    else:
        logger.info("Telegram disabled")
        print("❌ Telegram 已禁用")
    
    # Slack
    if config.SLACK_ENABLED:
        logger.info("Slack enabled")
        print("✅ Slack 已启用")
        slack = SlackAdapter(agent)
        # Optional: run local task.md on startup and post to Slack
        if config.TASK_MD_RUN_ON_STARTUP:
            try:
                print("⏳ 启动时执行 task.md 并发送到 Slack...")
                await slack.run_task_md_and_post()
                print("✅ task.md 结果已发送（或已跳过）")
            except Exception as e:
                logger.error(f"Startup task.md failed: {type(e).__name__}: {e}")
                print(f"⚠️ 启动时执行 task.md 失败: {e}")
        tasks.append(slack.run())
    else:
        logger.info("Slack disabled")
        print("❌ Slack 已禁用")
    
    # QQ
    if config.QQ_ENABLED:
        logger.info("QQ enabled")
        print("✅ QQ 已启用")
        qq = QQAdapter(agent)
        tasks.append(qq.run())
    else:
        logger.info("QQ disabled")
        print("❌ QQ 已禁用")
    
    # WeChat
    if config.WECHAT_ENABLED:
        logger.info("WeChat enabled")
        print("✅ WeChat 已启用")
        wechat = WeChatAdapter(agent)
        tasks.append(asyncio.get_event_loop().run_in_executor(None, wechat.run))
    else:
        logger.info("WeChat disabled")
        print("❌ WeChat 已禁用")
    
    print()  # 空行
    
    if not tasks:
        logger.error("No adapters enabled! Please configure at least one in .env")
        print("❌ 错误: 没有启用任何适配器！请在 .env 中至少启用一个")
        return
    
    print(f"✅ 已启用 {len(tasks)} 个适配器\n")
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        print("\n⏹️  正在关闭...")
        await agent.close()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ 致命错误: {e}")
        await agent.close()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())