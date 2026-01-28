import asyncio
import sys
from config import config
from core.agent import Agent
from adapters.telegram_adapter import TelegramAdapter
from adapters.qq_adapter import QQAdapter
from adapters.wechat_adapter import WeChatAdapter
from utils.logger import logger

async def main():
    """Main entry point"""
    logger.info("=== AgentBot Starting ===")
    logger.info(f"DeepSeek API URL: {config.DEEPSEEK_API_URL}")
    
    # Initialize agent
    agent = Agent()
    logger.info("Agent initialized")
    
    # Start enabled adapters
    tasks = []
    
    # Telegram
    if config.TELEGRAM_ENABLED:
        logger.info("Telegram enabled")
        telegram = TelegramAdapter(agent)
        tasks.append(telegram.run())
    else:
        logger.info("Telegram disabled")
    
    # QQ
    if config.QQ_ENABLED:
        logger.info("QQ enabled")
        qq = QQAdapter(agent)
        tasks.append(qq.run())
    else:
        logger.info("QQ disabled")
    
    # WeChat
    if config.WECHAT_ENABLED:
        logger.info("WeChat enabled")
        wechat = WeChatAdapter(agent)
        tasks.append(asyncio.get_event_loop().run_in_executor(None, wechat.run))
    else:
        logger.info("WeChat disabled")
    
    if not tasks:
        logger.error("No adapters enabled! Please configure at least one in .env")
        return
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await agent.close()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await agent.close()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())