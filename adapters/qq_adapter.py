from aiocqhttp import CQHttp
from config import config
from core.agent import Agent
from utils.logger import logger

class QQAdapter:
    """QQ bot adapter using CQHTTP"""
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.bot = CQHttp(
            api_root=f'http://{config.CQHTTP_HOST}:{config.CQHTTP_PORT}/api/',
            access_token=config.QQ_ACCESS_TOKEN
        )
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup message handlers"""
        @self.bot.on_message('private')
        async def handle_private_message(event):
            await self.handle_message(event, 'private')
        
        @self.bot.on_message('group')
        async def handle_group_message(event):
            await self.handle_message(event, 'group')
    
    async def handle_message(self, event, msg_type):
        """Handle QQ messages"""
        try:
            user_id = str(event['user_id'])
            message = event['message']
            
            logger.info(f"QQ message from {user_id}: {message}")
            
            # Get response from agent
            response = await self.agent.process_message(user_id, message)
            
            # Send response
            if msg_type == 'private':
                await self.bot.send_private_msg(
                    user_id=event['user_id'],
                    message=response
                )
            else:
                await self.bot.send_group_msg(
                    group_id=event['group_id'],
                    message=f"[CQ:at,qq={event['user_id']}] {response}"
                )
                
        except Exception as e:
            logger.error(f"QQ error: {e}")
    
    async def run(self):
        """Run QQ bot"""
        logger.info("Starting QQ adapter...")
        await self.bot.run(
            host=config.CQHTTP_HOST,
            port=config.CQHTTP_PORT
        )