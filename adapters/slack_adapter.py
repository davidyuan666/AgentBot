import os
import urllib3
import asyncio
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config import config
from core.agent import Agent
from core.pc_control import PCControl
from core.task_md_runner import run_task_md
from core.task_executor import plan_steps_from_task, execute_plan, render_summary
from utils.logger import logger

class SlackAdapter:
    """Slack bot adapter for PC control"""
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.pc_control = PCControl()
        
        logger.info("Initializing Slack adapter...")
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
                
                # 处理消息（task 命令支持进度回传）
                response = self._process_command(
                    user_id=str(user_id),
                    text=text,
                    channel=message.get("channel"),
                    say=say,
                )
                if response:
                    say(response)
                
            except Exception as e:
                logger.error(f"Error: {e}")
                say(f"❌ 错误: {str(e)}")
        
        logger.info("Slack handlers setup complete")

    def _post_message(self, channel: str, text: str):
        """Post message to Slack channel (sync)."""
        return self.app.client.chat_postMessage(channel=channel, text=text)

    async def post_message(self, channel: str, text: str):
        """Post message to Slack channel (async wrapper)."""
        return await asyncio.to_thread(self._post_message, channel, text)

    def _process_command(self, user_id: str, text: str, channel: str | None = None, say=None) -> str:
        """
        Process Slack text and return response text.
        Note: Slack Bolt message handlers are sync; we bridge async work via asyncio.run.
        """
        t = (text or "").strip()
        lower = t.lower()

        # Task runner command
        if lower in {"task", "run task", "run_task", "执行任务", "执行task", "执行 task", "跑任务"}:
            try:
                # With progress: post updates to current channel
                if channel:
                    if say:
                        say("⏳ 开始执行本地 task.md（会持续回传进度）...")
                    asyncio.run(self._run_task_with_progress(channel))
                    return None

                result = asyncio.run(run_task_md())
                return result
            except Exception as e:
                logger.error(f"[Slack] task.md runner error: {type(e).__name__}: {e}")
                return f"❌ 执行 task.md 失败: {str(e)}"

        # Default: send to agent
        try:
            return asyncio.run(self.agent.process_message(user_id, t))
        except Exception as e:
            logger.error(f"[Slack] agent error: {type(e).__name__}: {e}")
            return f"❌ 处理失败: {str(e)}"

    async def _run_task_with_progress(self, channel: str):
        """Run task.md and post progress updates to channel."""
        from core.task_md_runner import _read_text_file  # local import to avoid export
        import os as _os

        path = _os.path.abspath(config.TASK_MD_PATH)
        await self.post_message(channel, f"📄 读取任务文件：{path}")
        task_text = _read_text_file(path)
        if not task_text.strip():
            await self.post_message(channel, "⚠️ task.md 为空，已停止。")
            return

        await self.post_message(channel, "🧠 正在生成可执行步骤（DeepSeek）...")
        steps = await plan_steps_from_task(task_text)
        await self.post_message(channel, f"🧩 已生成 {len(steps)} 步，开始执行...")

        def progress(msg: str):
            # fire-and-forget sync callback into async post via thread bridge
            asyncio.run(self.post_message(channel, msg))

        results = await execute_plan(steps, progress=progress)
        summary = render_summary(results)
        await self.post_message(channel, "🏁 执行结束，汇总如下：\n" + summary)

    async def run_task_md_and_post(self):
        """Run local task.md and post result to configured Slack channel."""
        channel = config.SLACK_TASK_CHANNEL
        if not channel:
            logger.warning("SLACK_TASK_CHANNEL is not set; skip posting task.md result")
            return

        result = await run_task_md()
        # Slack 4000 chars is a safe practical limit for plain text
        max_len = 3800
        if len(result) <= max_len:
            await self.post_message(channel, result)
            return

        for i in range(0, len(result), max_len):
            await self.post_message(channel, result[i:i + max_len])
    
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