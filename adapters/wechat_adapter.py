import itchat
from itchat.content import TEXT
from config import config
from core.agent import Agent
from utils.logger import logger
import asyncio

class WeChatAdapter:
    """WeChat bot adapter"""
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.loop = asyncio.new_event_loop()
        itchat.config(storage='wchat.pkl')
    
    def setup_handlers(self):
        """Setup message handlers"""
        @itchat.msg_register(TEXT, isFriendChat=True)
        def handle_friend_message(msg):
            asyncio.run(self._handle_message(msg))
        
        @itchat.msg_register(TEXT, isGroupChat=True)
        def handle_group_message(msg):
            asyncio.run(self._handle_message(msg))
    
    async def _handle_message(self, msg):
        """Handle WeChat messages"""
        try:
            user_id = msg['FromUserName']
            message = msg['Content']
            
            logger.info(f"WeChat message from {user_id}: {message}")
            
            # Get response from agent
            response = await self.agent.process_message(user_id, message)
            
            # Send response
            itchat.send(response, toUserName=user_id)
            
        except Exception as e:
            logger.error(f"WeChat error: {e}")
    
    def run(self):
        """Run WeChat bot"""
        logger.info("Starting WeChat adapter...")
        self.setup_handlers()
        itchat.auto_login(hotReload=True)
        itchat.run(blockThread=False)