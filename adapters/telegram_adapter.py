from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import config
from core.agent import Agent
from utils.logger import logger

class TelegramAdapter:
    """Telegram bot adapter"""
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.app = Application.builder().token(config.TELEGRAM_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "👋 欢迎使用AgentBot!\n\n"
            "我是您的AI助手，可以帮您控制Windows电脑。\n"
            "使用 /help 查看可用命令。"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
可用命令:
/start - 开始
/help - 帮助
/shutdown - 关闭电脑
/restart - 重启电脑
/sysinfo - 系统信息

或者直接发送消息与我聊天！
"""
        await update.message.reply_text(help_text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user messages"""
        try:
            user_id = str(update.effective_user.id)
            user_message = update.message.text
            
            # Show typing indicator
            await update.message.chat.send_action("typing")
            
            # Get response from agent
            response = await self.agent.process_message(user_id, user_message)
            
            # Send response (split if too long)
            if len(response) > 4096:
                for i in range(0, len(response), 4096):
                    await update.message.reply_text(response[i:i+4096])
            else:
                await update.message.reply_text(response)
                
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            await update.message.reply_text("抱歉，处理您的请求时出错了。")
    
    async def run(self):
        """Run Telegram bot"""
        logger.info("Starting Telegram adapter...")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()