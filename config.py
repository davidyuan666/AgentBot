from pydantic_settings import BaseSettings
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
    TELEGRAM_ENABLED: bool = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    
    # Slack
    SLACK_ENABLED: bool = os.getenv("SLACK_ENABLED", "false").lower() == "true"
    SLACK_BOT_TOKEN: Optional[str] = os.getenv("SLACK_BOT_TOKEN")
    SLACK_SIGNING_SECRET: Optional[str] = os.getenv("SLACK_SIGNING_SECRET")
    SLACK_APP_TOKEN: Optional[str] = os.getenv("SLACK_APP_TOKEN")
    
    # Slack 代理配置
    SLACK_PROXY_HOST: Optional[str] = os.getenv("SLACK_PROXY_HOST")
    SLACK_PROXY_PORT: Optional[int] = int(os.getenv("SLACK_PROXY_PORT", "0")) if os.getenv("SLACK_PROXY_PORT") else None
    SLACK_PROXY_TYPE: str = os.getenv("SLACK_PROXY_TYPE", "http")
    
    @property
    def SLACK_PROXY_URL(self) -> Optional[str]:
        """生成代理 URL"""
        if self.SLACK_PROXY_HOST and self.SLACK_PROXY_PORT:
            return f"{self.SLACK_PROXY_TYPE}://{self.SLACK_PROXY_HOST}:{self.SLACK_PROXY_PORT}"
        return None
    
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