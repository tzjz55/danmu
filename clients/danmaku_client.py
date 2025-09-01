import aiohttp
import asyncio
<<<<<<< HEAD
import time
from typing import Dict, Any, Optional, Union
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import config
import json
from datetime import datetime, timedelta


class DanmakuAPIClient:
    """优化的弹幕API客户端"""
    
    _instance = None
    _session_pool: Optional[aiohttp.ClientSession] = None
    _last_activity = None
    _session_timeout = 300  # 5分钟无活动后关闭连接
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self.base_url = config.DANMAKU_BASE_URL
        self.api_key = config.DANMAKU_API_KEY
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'last_error': None,
            'last_success': None
        }
        self._rate_limiter = {
            'requests_per_second': 10,
            'last_request_time': 0,
            'request_count': 0,
            'window_start': time.time()
        }
        self._cache = {}
        self._cache_ttl = 60  # 缓存1分钟
        self._initialized = True
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._ensure_session()
=======
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
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
<<<<<<< HEAD
        # 不在这里关闭 session，由连接池管理
        self._last_activity = time.time()
    
    async def _ensure_session(self):
        """确保 session 存在且有效"""
        current_time = time.time()
        
        # 检查是否需要创建新的 session
        if (self._session_pool is None or 
            self._session_pool.closed or
            (self._last_activity and current_time - self._last_activity > self._session_timeout)):
            
            await self._create_session_pool()
        
        self.session = self._session_pool
        self._last_activity = current_time
    
    async def _create_session_pool(self):
        """创建优化的 session 连接池"""
        # 关闭旧的 session
        if self._session_pool and not self._session_pool.closed:
            await self._session_pool.close()
        
        # 创建新的 session 连接池
        connector = aiohttp.TCPConnector(
            limit=20,  # 总连接数限制
            limit_per_host=10,  # 单个主机连接数限制
            ttl_dns_cache=300,  # DNS 缓存时间
            use_dns_cache=True,
            keepalive_timeout=30,  # 保持连接时间
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(
            total=30,
            connect=10,
            sock_read=20
        )
        
        headers = {
            'User-Agent': 'DanmakuBot/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        self._session_pool = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers,
            json_serialize=json.dumps
        )
        
        logger.info("创建新的 API 连接池")
=======
        if self.session:
            await self.session.close()
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
    
    def _build_url(self, endpoint: str) -> str:
        """构建完整的API URL"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        if '?' in url:
            url += f"&api_key={self.api_key}"
        else:
            url += f"?api_key={self.api_key}"
        return url
    
<<<<<<< HEAD
    async def _rate_limit_check(self):
        """检查速率限制"""
        current_time = time.time()
        
        # 重置窗口计数
        if current_time - self._rate_limiter['window_start'] >= 1.0:
            self._rate_limiter['request_count'] = 0
            self._rate_limiter['window_start'] = current_time
        
        # 检查是否超过限制
        if self._rate_limiter['request_count'] >= self._rate_limiter['requests_per_second']:
            sleep_time = 1.0 - (current_time - self._rate_limiter['window_start'])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                self._rate_limiter['request_count'] = 0
                self._rate_limiter['window_start'] = time.time()
        
        self._rate_limiter['request_count'] += 1
        self._rate_limiter['last_request_time'] = current_time
    
    def _get_cache_key(self, method: str, endpoint: str, **kwargs) -> str:
        """生成缓存键"""
        cache_data = {
            'method': method,
            'endpoint': endpoint,
            'params': kwargs.get('params', {}),
            'json': kwargs.get('json', {})
        }
        return f"{method}:{endpoint}:{hash(str(sorted(cache_data.items())))}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从缓存获取数据"""
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_data
            else:
                del self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data: Dict[str, Any]):
        """设置缓存数据"""
        self._cache[cache_key] = (data, time.time())
        
        # 限制缓存大小
        if len(self._cache) > 100:
            # 删除最旧的缓存
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
    
    def _update_stats(self, success: bool, response_time: float, error: Optional[str] = None):
        """更新请求统计"""
        self._request_stats['total_requests'] += 1
        
        if success:
            self._request_stats['successful_requests'] += 1
            self._request_stats['last_success'] = datetime.now()
        else:
            self._request_stats['failed_requests'] += 1
            self._request_stats['last_error'] = error
        
        # 更新平均响应时间
        total_requests = self._request_stats['total_requests']
        current_avg = self._request_stats['avg_response_time']
        self._request_stats['avg_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
=======
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
    )
    async def _make_request(
        self, 
        method: str, 
<<<<<<< HEAD
        endpoint: str,
        use_cache: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """发送HTTP请求（优化版）"""
        start_time = time.time()
        
        try:
            # 速率限制检查
            await self._rate_limit_check()
            
            # 缓存检查（仅对 GET 请求）
            cache_key = None
            if use_cache and method.upper() == 'GET':
                cache_key = self._get_cache_key(method, endpoint, **kwargs)
                cached_data = self._get_from_cache(cache_key)
                if cached_data:
                    logger.debug(f"命中缓存: {method} {endpoint}")
                    return cached_data
            
            # 确保 session 存在
            await self._ensure_session()
            if not self.session:
                raise RuntimeError("Session not initialized.")
            
            url = self._build_url(endpoint)
            
            # 发送请求
            async with self.session.request(method, url, **kwargs) as response:
                response_time = time.time() - start_time
                
                # 检查响应状态
                if response.status == 200:
                    try:
                        data = await response.json()
                        
                        # 更新统计
                        self._update_stats(True, response_time)
                        
                        # 设置缓存
                        if cache_key:
                            self._set_cache(cache_key, data)
                        
                        logger.debug(f"API请求成功: {method} {endpoint} ({response_time:.3f}s)")
                        return data
                        
                    except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
                        error_text = await response.text()
                        logger.warning(f"JSON解析失败: {e}, 响应内容: {error_text[:200]}")
                        # 如果不是 JSON 响应，尝试返回文本
                        return {'success': True, 'data': error_text, 'raw_response': True}
                        
                elif response.status == 429:  # Rate Limited
                    retry_after = int(response.headers.get('Retry-After', 5))
                    logger.warning(f"被速率限制，{retry_after}秒后重试")
                    await asyncio.sleep(retry_after)
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message="Rate limited"
                    )
                    
                elif response.status >= 500:  # Server Error
                    error_text = await response.text()
                    logger.error(f"服务器错误: {response.status} - {error_text}")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"Server error: {error_text}"
                    )
                    
                else:  # Client Error
                    error_text = await response.text()
                    logger.error(f"API请求失败: {response.status} - {error_text}")
                    self._update_stats(False, response_time, f"{response.status}: {error_text}")
=======
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
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=error_text
                    )
<<<<<<< HEAD
                    
        except aiohttp.ClientError as e:
            response_time = time.time() - start_time
            error_msg = f"网络请求错误: {e}"
            logger.error(error_msg)
            self._update_stats(False, response_time, error_msg)
            raise
            
        except asyncio.TimeoutError as e:
            response_time = time.time() - start_time
            error_msg = f"请求超时: {e}"
            logger.error(error_msg)
            self._update_stats(False, response_time, error_msg)
            raise
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"未知错误: {e}"
            logger.error(error_msg)
            self._update_stats(False, response_time, error_msg)
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """获取请求统计信息"""
        stats = self._request_stats.copy()
        stats['cache_size'] = len(self._cache)
        stats['rate_limit_status'] = {
            'requests_per_second': self._rate_limiter['requests_per_second'],
            'current_window_requests': self._rate_limiter['request_count'],
            'last_request_time': self._rate_limiter['last_request_time']
        }
        if stats['last_success']:
            stats['last_success'] = stats['last_success'].isoformat()
        return stats
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        logger.info("已清空 API 缓存")
    
    def reset_stats(self):
        """重置统计信息"""
        self._request_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'last_error': None,
            'last_success': None
        }
        logger.info("已重置 API 统计信息")
    
    async def cleanup(self):
        """清理资源"""
        if self._session_pool and not self._session_pool.closed:
            await self._session_pool.close()
            self._session_pool = None
        self.clear_cache()
        logger.info("已清理 API 客户端资源")
    
    async def get_status(self) -> Dict[str, Any]:
        """获取服务器状态（支持缓存）"""
        try:
            data = await self._make_request('GET', '/api/control/status', use_cache=True)
=======
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
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
            return {
                'success': True,
                'data': data,
                'message': '状态获取成功'
            }
<<<<<<< HEAD
        except aiohttp.ClientResponseError as e:
            error_msg = f'API错误 [{e.status}]: {e.message}'
            logger.error(f"获取状态失败: {error_msg}")
            return {
                'success': False,
                'data': None,
                'message': error_msg,
                'error_code': e.status
            }
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            error_msg = f'网络错误: {str(e)}'
            logger.error(f"获取状态失败: {error_msg}")
            return {
                'success': False,
                'data': None,
                'message': error_msg,
                'error_type': 'network_error'
            }
        except Exception as e:
            error_msg = f'未知错误: {str(e)}'
            logger.error(f"获取状态失败: {error_msg}")
            return {
                'success': False,
                'data': None,
                'message': error_msg,
                'error_type': 'unknown_error'
=======
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return {
                'success': False,
                'data': None,
                'message': f'获取状态失败: {str(e)}'
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
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
    
<<<<<<< HEAD
    async def send_danmaku(
        self, 
        text: str, 
        color: str = "#FFFFFF",
        position: str = "scroll",
        font_size: int = 24,
        duration: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
=======
    async def send_danmaku(self, text: str, **kwargs) -> Dict[str, Any]:
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
        """发送弹幕
        
        Args:
            text: 弹幕内容
<<<<<<< HEAD
            color: 弹幕颜色 (十六进制，如 #FF0000)
            position: 弹幕位置 (scroll/top/bottom)
            font_size: 字体大小 (12-48)
            duration: 显示时长 (秒)
            **kwargs: 其他弹幕参数
=======
            **kwargs: 其他弹幕参数（颜色、位置等）
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
        """
        payload = {
            'action': 'send',
            'text': text,
<<<<<<< HEAD
            'color': color,
            'position': position,
            'font_size': max(12, min(48, font_size)),  # 限制字体大小范围
            'duration': max(1, min(30, duration)),     # 限制显示时长范围
=======
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
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
<<<<<<< HEAD
    
    async def send_styled_danmaku(
        self,
        text: str,
        style_preset: str = "normal"
    ) -> Dict[str, Any]:
        """发送预设样式弹幕
        
        Args:
            text: 弹幕内容
            style_preset: 样式预设 (normal/highlight/warning/success/error)
        """
        style_configs = {
            "normal": {
                "color": "#FFFFFF",
                "position": "scroll",
                "font_size": 24,
                "duration": 5
            },
            "highlight": {
                "color": "#FFD700",
                "position": "top",
                "font_size": 28,
                "duration": 8
            },
            "warning": {
                "color": "#FF8C00",
                "position": "scroll",
                "font_size": 26,
                "duration": 6
            },
            "success": {
                "color": "#00FF00",
                "position": "bottom",
                "font_size": 24,
                "duration": 5
            },
            "error": {
                "color": "#FF0000",
                "position": "top",
                "font_size": 26,
                "duration": 8
            }
        }
        
        config = style_configs.get(style_preset, style_configs["normal"])
        return await self.send_danmaku(text, **config)
    
    async def send_bulk_danmaku(
        self,
        messages: list,
        interval: float = 1.0
    ) -> Dict[str, Any]:
        """批量发送弹幕
        
        Args:
            messages: 弹幕消息列表 [{'text': str, 'color': str, ...}, ...]
            interval: 发送间隔 (秒)
        """
        results = []
        success_count = 0
        
        try:
            for i, message in enumerate(messages):
                if isinstance(message, str):
                    message = {'text': message}
                
                result = await self.send_danmaku(**message)
                results.append(result)
                
                if result['success']:
                    success_count += 1
                
                # 最后一条消息不需要等待
                if i < len(messages) - 1:
                    await asyncio.sleep(interval)
            
            return {
                'success': success_count > 0,
                'data': {
                    'total': len(messages),
                    'success': success_count,
                    'failed': len(messages) - success_count,
                    'results': results
                },
                'message': f'批量发送完成: {success_count}/{len(messages)} 成功'
            }
            
        except Exception as e:
            logger.error(f"批量发送弹幕失败: {e}")
            return {
                'success': False,
                'data': None,
                'message': f'批量发送失败: {str(e)}'
            }
=======
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103


# 全局客户端实例
danmaku_client = DanmakuAPIClient()