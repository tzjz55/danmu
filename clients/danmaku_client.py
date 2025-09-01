import aiohttp
import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from config import config


class DanmakuAPIClient:
    """弹幕API客户端"""
    
    def __init__(self):
        self.base_url = config.DANMAKU_BASE_URL
        self.api_key = config.DANMAKU_API_KEY
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    def _build_url(self, endpoint: str) -> str:
        """构建完整的API URL"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        if '?' in url:
            url += f"&api_key={self.api_key}"
        else:
            url += f"?api_key={self.api_key}"
        return url
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """发送HTTP请求"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        url = self._build_url(endpoint)
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"API请求成功: {method} {endpoint}")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"API请求失败: {response.status} - {error_text}")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=error_text
                    )
        except aiohttp.ClientError as e:
            logger.error(f"网络请求错误: {e}")
            raise
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """获取服务器状态"""
        try:
            data = await self._make_request('GET', '/api/control/status')
            return {
                'success': True,
                'data': data,
                'message': '状态获取成功'
            }
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return {
                'success': False,
                'data': None,
                'message': f'获取状态失败: {str(e)}'
            }
    
    async def control_danmaku(
        self, 
        action: str, 
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """控制弹幕"""
        payload = {
            'action': action
        }
        
        if settings:
            payload['settings'] = settings
        
        try:
            data = await self._make_request(
                'POST', 
                '/api/control/danmaku',
                json=payload
            )
            return {
                'success': True,
                'data': data,
                'message': f'弹幕控制成功: {action}'
            }
        except Exception as e:
            logger.error(f"弹幕控制失败: {e}")
            return {
                'success': False,
                'data': None,
                'message': f'弹幕控制失败: {str(e)}'
            }
    
    async def pause_danmaku(self) -> Dict[str, Any]:
        """暂停弹幕"""
        return await self.control_danmaku('pause')
    
    async def resume_danmaku(self) -> Dict[str, Any]:
        """恢复弹幕"""
        return await self.control_danmaku('resume')
    
    async def clear_danmaku(self) -> Dict[str, Any]:
        """清空弹幕"""
        return await self.control_danmaku('clear')
    
    async def set_danmaku_speed(self, speed: str) -> Dict[str, Any]:
        """设置弹幕速度
        
        Args:
            speed: slow, normal, fast
        """
        return await self.control_danmaku('set_speed', {'speed': speed})
    
    async def set_danmaku_opacity(self, opacity: float) -> Dict[str, Any]:
        """设置弹幕透明度
        
        Args:
            opacity: 0.0 - 1.0
        """
        return await self.control_danmaku('set_opacity', {'opacity': opacity})
    
    async def send_danmaku(self, text: str, **kwargs) -> Dict[str, Any]:
        """发送弹幕
        
        Args:
            text: 弹幕内容
            **kwargs: 其他弹幕参数（颜色、位置等）
        """
        payload = {
            'action': 'send',
            'text': text,
            **kwargs
        }
        
        try:
            data = await self._make_request(
                'POST',
                '/api/control/danmaku',
                json=payload
            )
            return {
                'success': True,
                'data': data,
                'message': '弹幕发送成功'
            }
        except Exception as e:
            logger.error(f"弹幕发送失败: {e}")
            return {
                'success': False,
                'data': None,
                'message': f'弹幕发送失败: {str(e)}'
            }


# 全局客户端实例
danmaku_client = DanmakuAPIClient()