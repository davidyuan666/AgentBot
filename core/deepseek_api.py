import httpx
import json
from typing import Optional, List, Dict, AsyncGenerator
from config import config
from utils.logger import logger

class DeepSeekAPI:
    """DeepSeek API client for Chinese LLM"""
    
    def __init__(self):
        self.api_key = config.DEEPSEEK_API_KEY
        self.api_url = config.DEEPSEEK_API_URL
        self.model = config.DEEPSEEK_MODEL
        self.client = httpx.AsyncClient(timeout=60)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Send message to DeepSeek and get response"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return "抱歉，API调用失败，请重试。"
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            return f"出错了: {str(e)}"
    
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """Stream response from DeepSeek"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": True
            }
            
            async with self.client.stream(
                "POST",
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"DeepSeek stream error: {e}")
            yield f"出错了: {str(e)}"
    
    async def close(self):
        """Close client connection"""
        await self.client.aclose()