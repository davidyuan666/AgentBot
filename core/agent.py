import asyncio
from typing import List, Dict, Optional
from core.deepseek_api import DeepSeekAPI
from core.pc_control import PCControl
from utils.logger import logger
import json

class Agent:
    """Main Agent orchestrating AI and PC control"""
    
    def __init__(self):
        self.deepseek = DeepSeekAPI()
        self.pc_control = PCControl()
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.system_prompt = """你是一个智能助手机器人，可以帮助用户控制Windows电脑。
你可以执行以下操作：
1. execute_command: 执行Windows命令
2. open_application: 打开应用程序
3. mouse_move: 移动鼠标
4. mouse_click: 点击鼠标
5. keyboard_type: 输入文本
6. get_system_info: 获取系统信息
7. take_screenshot: 截图
8. shutdown: 关闭系统
9. restart: 重启系统

用户会通过Telegram、QQ或WeChat与你聊天。请用中文回复，友好且有帮助。
当用户要求执行操作时，提供清晰的结果信息。"""
    
    def get_user_history(self, user_id: str) -> List[Dict]:
        """Get conversation history for user"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = [
                {"role": "system", "content": self.system_prompt}
            ]
        return self.conversation_history[user_id]
    
    async def process_message(self, user_id: str, message: str) -> str:
        """Process user message and return response"""
        try:
            history = self.get_user_history(user_id)
            
            # Add user message
            history.append({"role": "user", "content": message})
            
            # Get response from DeepSeek
            response = await self.deepseek.chat(history)
            
            # Add assistant response
            history.append({"role": "assistant", "content": response})
            
            # Keep history manageable (last 10 exchanges)
            if len(history) > 20:
                history = [history[0]] + history[-19:]
                self.conversation_history[user_id] = history
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "抱歉，处理您的请求时出错了。"
    
    async def close(self):
        """Cleanup resources"""
        await self.deepseek.close()