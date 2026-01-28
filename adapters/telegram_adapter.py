from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import config
from core.agent import Agent
from utils.logger import logger

class TelegramAdapter:
    """Telegram bot adapter"""
    
    def __init__(self, agent: Agent):
        self.agent = agent
        logger.info(f"Initializing Telegram adapter with token: {config.TELEGRAM_TOKEN[:20]}...")
        self.app = Application.builder().token(config.TELEGRAM_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        logger.info("Setting up Telegram handlers...")
        
        # 添加一个 pre_checkout 处理器用于调试
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("test", self.test_command))
        
        # 这个处理器会捕获所有文本消息（包括命令）用于调试
        self.app.add_handler(MessageHandler(filters.TEXT, self.debug_message))
        
        logger.info("Telegram handlers setup complete")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        logger.info(f"[/start] Received from user {update.effective_user.id} ({update.effective_user.first_name})")
        try:
            await update.message.reply_text(
                "👋 欢迎使用AgentBot!\n\n"
                "我是您的AI助手，可以帮您控制Windows电脑。\n"
                "使用 /help 查看可用命令。"
            )
            logger.info(f"[/start] Response sent to {update.effective_user.id}")
        except Exception as e:
            logger.error(f"[/start] Error: {e}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        logger.info(f"[/help] Received from user {update.effective_user.id}")
        try:
            help_text = """
可用命令:
/start - 开始
/help - 帮助
/test - 测试机器人连接
/shutdown - 关闭电脑
/restart - 重启电脑
/sysinfo - 系统信息

或者直接发送消息与我聊天！
"""
            await update.message.reply_text(help_text)
            logger.info(f"[/help] Response sent to {update.effective_user.id}")
        except Exception as e:
            logger.error(f"[/help] Error: {e}")
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /test command - test if bot is working"""
        logger.info(f"[/test] Received from user {update.effective_user.id}")
        try:
            await update.message.reply_text(
                "✅ 机器人正在运行！\n\n"
                "现在试试发送任何消息吧。"
            )
            logger.info(f"[/test] Response sent to {update.effective_user.id}")
        except Exception as e:
            logger.error(f"[/test] Error: {e}")
    
    async def debug_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Debug handler - logs ALL messages"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "Unknown"
        user_message = update.message.text
        
        # 打印到控制台（不只是日志文件）
        print("\n" + "="*60)
        print("🔔 收到 Telegram 消息！")
        print("="*60)
        print(f"用户ID: {user_id}")
        print(f"用户名: {user_name}")
        print(f"消息: {user_message}")
        print("="*60 + "\n")
        
        logger.info(f"[DEBUG] 收到消息 - 用户: {user_id} ({user_name}), 消息: {user_message}")
        
        # 检查是否是命令（由其他处理器处理）
        if user_message.startswith("/"):
            logger.info(f"[DEBUG] 这是一个命令，由命令处理器处理")
            return
        
        # 处理普通消息
        try:
            logger.info(f"[MESSAGE] Processing message from {user_id}...")
            
            # Show typing indicator
            await update.message.chat.send_action("typing")
            logger.info(f"[MESSAGE] Sending typing indicator...")
            
            # Get response from agent
            logger.info(f"[MESSAGE] Calling agent.process_message()...")
            response = await self.agent.process_message(str(user_id), user_message)
            
            logger.info(f"[MESSAGE] Agent response: {response[:100]}...")
            
            # Send response
            if len(response) > 4096:
                logger.info(f"[MESSAGE] Response is long, splitting...")
                for i in range(0, len(response), 4096):
                    part = response[i:i+4096]
                    await update.message.reply_text(part)
            else:
                await update.message.reply_text(response)
            
            print("\n✅ 消息已成功处理并回复！\n")
            logger.info(f"[MESSAGE] Response sent to {user_id}")
                
        except Exception as e:
            print(f"\n❌ 处理消息时出错: {type(e).__name__}: {e}\n")
            logger.error(f"[MESSAGE] Error: {type(e).__name__}: {e}", exc_info=True)
            try:
                await update.message.reply_text(f"❌ 发生错误: {str(e)}")
            except Exception as send_error:
                logger.error(f"[MESSAGE] Failed to send error message: {send_error}")
    
    async def run(self):
        """Run Telegram bot"""
        print("\n" + "="*60)
        print("🤖 启动 Telegram 机器人")
        print("="*60)
        print("\n等待消息... 请在 Telegram 中发送消息！\n")
        
        logger.info("="*60)
        logger.info("Starting Telegram adapter...")
        logger.info("="*60)
        
        try:
            await self.app.initialize()
            logger.info("Telegram app initialized")
            
            await self.app.start()
            logger.info("Telegram app started")
            
            logger.info("Starting polling... Waiting for messages...")
            await self.app.updater.start_polling(drop_pending_updates=True)
            logger.info("Telegram polling started")
            
        except Exception as e:
            print(f"\n❌ Telegram 启动失败: {type(e).__name__}: {e}\n")
            logger.error(f"Telegram adapter error: {type(e).__name__}: {e}", exc_info=True)
            raise