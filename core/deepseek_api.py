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
        
        # 检查 API 密钥
        if not self.api_key or self.api_key == "":
            logger.warning("WARNING: DEEPSEEK_API_KEY is empty!")
        else:
            logger.info(f"DeepSeek API Key configured: {self.api_key[:20]}...")
        
        logger.info(f"DeepSeek API URL: {self.api_url}")
        logger.info(f"DeepSeek Model: {self.model}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Send message to DeepSeek and get response"""
        try:
            if not self.api_key:
                logger.error("ERROR: DEEPSEEK_API_KEY is not set in .env file")
                return "错误：未配置 DeepSeek API 密钥。请在 .env 文件中设置 DEEPSEEK_API_KEY。"
            
            logger.info(f"Calling DeepSeek API with {len(messages)} messages...")
            
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
            
            logger.debug(f"API URL: {self.api_url}/chat/completions")
            logger.debug(f"Payload: {json.dumps(payload, ensure_ascii=False)}")
            
            response = await self.client.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            logger.info(f"DeepSeek API response status: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = response.text
                logger.error(f"DeepSeek API error {response.status_code}: {error_msg}")
                return f"API 错误 ({response.status_code}): {error_msg[:100]}"
            
            data = response.json()
            logger.debug(f"API Response: {json.dumps(data, ensure_ascii=False)[:200]}")
            
            if 'choices' not in data or len(data['choices']) == 0:
                logger.error(f"Invalid API response: {data}")
                return "API 返回了无效的响应"
            
            result = data['choices'][0]['message']['content']
            logger.info(f"DeepSeek response: {result[:100]}...")
            return result
            
        except httpx.ConnectError as e:
            logger.error(f"Network connection error: {e}")
            return "网络连接错误，请检查网络和 API 地址"
        except httpx.TimeoutException as e:
            logger.error(f"API timeout: {e}")
            return "API 请求超时，请重试"
        except Exception as e:
            logger.error(f"DeepSeek API error: {type(e).__name__}: {e}")
            return f"发生错误: {str(e)}"
    
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