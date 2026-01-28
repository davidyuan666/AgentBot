import asyncio
import re
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
        logger.info(f"Bot Token: {config.SLACK_BOT_TOKEN[:20] if config.SLACK_BOT_TOKEN else 'Not set'}...")
        logger.info(f"App Token: {config.SLACK_APP_TOKEN[:20] if config.SLACK_APP_TOKEN else 'Not set'}...")
        
        # Initialize Slack app
        self.app = App(
            token=config.SLACK_BOT_TOKEN,
            signing_secret=config.SLACK_SIGNING_SECRET
        )
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup message handlers"""
        logger.info("Setting up Slack handlers...")
        
        @self.app.message(lambda msg: "text" in msg)
        def handle_message(message, say, logger_):
            """Handle all messages"""
            try:
                user_id = message.get("user")
                user_message = message.get("text", "").strip()
                channel = message.get("channel")
                
                logger.info(f"[Slack] Message from {user_id}: {user_message}")
                
                print(f"\n{'='*60}")
                print(f"🔔 收到 Slack 消息")
                print(f"{'='*60}")
                print(f"用户: {user_id}")
                print(f"频道: {channel}")
                print(f"消息: {user_message}")
                print(f"{'='*60}\n")
                
                # Skip empty messages and bot messages
                if not user_message or message.get("subtype") == "bot_message":
                    return
                
                # Process message
                try:
                    response = self._process_command(user_message)
                    
                    if response:
                        print(f"\n✅ 已发送回复\n")
                        say(response)
                    
                except Exception as e:
                    logger.error(f"[Slack] Error: {e}")
                    say(f"❌ 处理消息时出错: {str(e)}")
                
            except Exception as e:
                logger.error(f"[Slack] Handler error: {e}")
        
        logger.info("Slack handlers setup complete")
    
    def _process_command(self, message: str) -> str:
        """Process command and return response"""
        
        # 识别命令
        if "打开" in message or "open" in message.lower():
            # 打开应用
            app_name = message.replace("打开", "").replace("open", "").strip()
            result = self.pc_control.open_application(app_name)
            return self._format_response(result)
        
        elif "截图" in message or "screenshot" in message.lower():
            # 截图
            result = self.pc_control.take_screenshot()
            return self._format_response(result)
        
        elif "系统信息" in message or "sysinfo" in message.lower():
            # 系统信息
            result = self.pc_control.get_system_info()
            if result.get("success"):
                info = result
                return f"""系统信息:
CPU: {info.get('cpu_percent', 'N/A')}
内存: {info.get('memory_percent', 'N/A')}
磁盘: {info.get('disk_usage', 'N/A')}
进程数: {info.get('running_processes', 'N/A')}"""
            return self._format_response(result)
        
        elif "关闭电脑" in message or "shutdown" in message.lower():
            # 关闭电脑
            result = self.pc_control.shutdown()
            return self._format_response(result)
        
        elif "重启" in message or "restart" in message.lower():
            # 重启
            result = self.pc_control.restart()
            return self._format_response(result)
        
        elif "锁定" in message or "lock" in message.lower():
            # 锁定屏幕
            result = self.pc_control.lock_screen()
            return self._format_response(result)
        
        elif "睡眠" in message or "sleep" in message.lower():
            # 睡眠
            result = self.pc_control.sleep()
            return self._format_response(result)
        
        elif "执行" in message:
            # 执行命令
            cmd = message.replace("执行", "").strip()
            result = self.pc_control.execute_command(cmd)
            return self._format_response(result)
        
        elif "鼠标" in message:
            # 鼠标控制
            if "移动到" in message:
                match = re.search(r'(\d+)\s*,\s*(\d+)', message)
                if match:
                    x, y = int(match.group(1)), int(match.group(2))
                    result = self.pc_control.mouse_move(x, y)
                    return self._format_response(result)
            elif "点击" in message:
                result = self.pc_control.mouse_click()
                return self._format_response(result)
        
        elif "键盘" in message:
            # 键盘输入
            if "输入" in message:
                text = message.replace("键盘", "").replace("输入", "").strip()
                result = self.pc_control.keyboard_type(text)
                return self._format_response(result)
        
        elif "进程" in message or "process" in message.lower():
            # 列出进程
            result = self.pc_control.list_processes()
            if result.get("success"):
                processes = result.get("processes", [])[:10]
                process_list = "\n".join(processes)
                return f"运行中的进程:\n{process_list}"
            return self._format_response(result)
        
        elif "帮助" in message or "help" in message.lower():
            # 显示帮助
            return self._get_help_text()
        
        else:
            # 调用 AI 处理
            try:
                response = asyncio.run(
                    self.agent.process_message(message, message)
                )
                return response
            except Exception as e:
                logger.error(f"AI processing error: {e}")
                return f"AI 处理失败: {str(e)}"
    
    def _format_response(self, result: dict) -> str:
        """Format command result as response"""
        if result.get("success"):
            message = result.get("message", "成功")
            output = result.get("output", "")
            if output:
                return f"✅ {message}\n\n输出:\n{output[:200]}"
            return f"✅ {message}"
        else:
            error = result.get("error", "未知错误")
            return f"❌ 错误: {error}"
    
    def _get_help_text(self) -> str:
        """Get help text with available commands"""
        return """
🤖 AgentBot 命令帮助

【应用控制】
• 打开记事本 / 打开计算器 / 打开文件管理器
• 支持的应用: 记事本, 计算器, 画图, 任务管理器, 文件管理器, 浏览器, cmd, powershell

【系统信息】
• 系统信息 - 查看 CPU、内存、磁盘使用情况
• 进程 - 列出运行中的进程

【屏幕截图】
• 截图 - 保存屏幕截图

【系统控制】
• 关闭电脑 - 关闭 Windows 系统
• 重启 - 重启系统
• 锁定 - 锁定屏幕
• 睡眠 - 系统进入睡眠

【设备控制】
• 鼠标移动到 100,200 - 移动鼠标
• 鼠标点击 - 点击鼠标
• 键盘输入 你好 - 输入文本

【其他】
• 执行 ipconfig - 执行任意 Windows 命令
• 帮助 - 显示此帮助信息

【AI 功能】
直接发送任何其他消息，AI 会用 DeepSeek 处理
"""
    
    async def run(self):
        """Run Slack bot using Socket Mode"""
        logger.info("="*60)
        logger.info("Starting Slack adapter...")
        logger.info("="*60)
        
        print("\n" + "="*60)
        print("🤖 Slack 机器人启动")
        print("="*60)
        print("\n在手机 Slack App 中发送消息来控制电脑!")
        print("发送 '帮助' 查看所有可用命令\n")
        
        try:
            # Use Socket Mode for local/remote deployment
            handler = SocketModeHandler(self.app, config.SLACK_APP_TOKEN)
            logger.info("Slack bot is running with Socket Mode")
            handler.start()
            
        except Exception as e:
            logger.error(f"[Slack] Error: {e}")
            print(f"\n❌ Slack 启动失败: {e}\n")
            raise