from pydantic import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Config(BaseSettings):
    # DeepSeek API
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_URL: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # Telegram
    TELEGRAM_TOKEN: Optional[str] = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_ENABLED: bool = bool(TELEGRAM_TOKEN)
    
    # QQ (CQHTTP)
    QQ_ENABLED: bool = os.getenv("QQ_ENABLED", "false").lower() == "true"
    QQ_ACCESS_TOKEN: Optional[str] = os.getenv("QQ_ACCESS_TOKEN")
    CQHTTP_HOST: str = os.getenv("CQHTTP_HOST", "127.0.0.1")
    CQHTTP_PORT: int = int(os.getenv("CQHTTP_PORT", "5700"))
    
    # WeChat
    WECHAT_ENABLED: bool = os.getenv("WECHAT_ENABLED", "false").lower() == "true"
    
    # PC Control
    PC_CONTROL_ENABLED: bool = True
    COMMAND_TIMEOUT: int = 30
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        case_sensitive = True

config = Config()