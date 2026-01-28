import os
import urllib3
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config import config
from core.agent import Agent
from core.pc_control import PCControl
from utils.logger import logger

class SlackAdapter:
    """Slack bot adapter for PC control"""
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.pc_control = PCControl()
        
        logger.info("Initializing Slack adapter...")
        
        # 设置代理
        if config.SLACK_PROXY_HOST and config.SLACK_PROXY_PORT:
            proxy_url = config.SLACK_PROXY_URL
            logger.info(f"Setting proxy: {proxy_url}")
            print(f"\n✅ 代理已配置: {proxy_url}\n")
            
            # 设置环境变量
            os.environ['http_proxy'] = proxy_url
            os.environ['https_proxy'] = proxy_url
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
            
            # 禁用 SSL 警告
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        logger.info(f"Bot Token: {config.SLACK_BOT_TOKEN[:20]}...")
        logger.info(f"App Token: {config.SLACK_APP_TOKEN[:20]}...")
        
        # Initialize Slack app
        self.app = App(
            token=config.SLACK_BOT_TOKEN,
            signing_secret=config.SLACK_SIGNING_SECRET
        )
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup message handlers"""
        logger.info("Setting up Slack handlers...")
        
        @self.app.message()
        def handle_all_messages(message, say):
            """Handle all messages"""
            try:
                # 跳过 bot 自己的消息
                if message.get("bot_id"):
                    return
                
                user_id = message.get("user")
                text = message.get("text", "").strip()
                
                if not text:
                    return
                
                logger.info(f"[Slack] Received: {text}")
                print(f"\n{'='*60}")
                print(f"🔔 收到消息: {text}")
                print(f"{'='*60}\n")
                
                # 处理消息
                response = self._process_command(text)
                say(response)
                
            except Exception as e:
                logger.error(f"Error: {e}")
                say(f"❌ 错误: {str(e)}")
        
        logger.info("Slack handlers setup complete")
    
    # ... 其他方法保持不变 ...
    
    async def run(self):
        """Run Slack bot using Socket Mode"""
        logger.info("="*60)
        logger.info("Starting Slack adapter...")
        logger.info("="*60)
        
        print("\n" + "="*60)
        print("🤖 Slack 机器人启动")
        print("="*60)
        print(f"\n代理配置: {config.SLACK_PROXY_URL}")
        print("\n在手机 Slack App 中发送消息来控制电脑!")
        print("发送 '帮助' 查看所有可用命令\n")
        
        try:
            handler = SocketModeHandler(self.app, config.SLACK_APP_TOKEN)
            logger.info("Slack bot is running with Socket Mode")
            handler.start()
            
        except Exception as e:
            logger.error(f"[Slack] Error: {e}")
            print(f"\n❌ Slack 启动失败: {e}\n")
            raise