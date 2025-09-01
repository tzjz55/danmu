import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from loguru import logger
from dataclasses import dataclass, asdict
from enum import Enum

# 导入内容过滤器
try:
    from .content_filter import content_filter, FilterAction
except ImportError:
    content_filter = None
    FilterAction = None


class DanmakuStatus(Enum):
    """弹幕状态枚举"""
    PENDING = "pending"      # 待发送
    SENDING = "sending"      # 发送中
    SUCCESS = "success"      # 发送成功
    FAILED = "failed"        # 发送失败
    CANCELLED = "cancelled"  # 已取消


@dataclass
class DanmakuMessage:
    """弹幕消息数据类"""
    id: str
    text: str
    user_id: int
    color: str = "#FFFFFF"
    position: str = "scroll"
    font_size: int = 24
    duration: int = 5
    priority: int = 1  # 优先级 1-5，5最高
    delay: float = 0.0  # 延迟发送时间（秒）
    status: DanmakuStatus = DanmakuStatus.PENDING
    created_at: datetime = None
    sent_at: datetime = None
    error_message: str = ""
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['sent_at'] = self.sent_at.isoformat() if self.sent_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DanmakuMessage':
        """从字典创建"""
        if 'status' in data:
            data['status'] = DanmakuStatus(data['status'])
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'sent_at' in data and data['sent_at']:
            data['sent_at'] = datetime.fromisoformat(data['sent_at'])
        return cls(**data)


class DanmakuQueue:
    """弹幕队列管理器"""
    
    def __init__(self, max_queue_size: int = 1000, queue_file: str = "data/danmaku_queue.json"):
        self.max_queue_size = max_queue_size
        self.queue_file = Path(queue_file)
        self.queue: List[DanmakuMessage] = []
        self.is_processing = False
        self.processing_task = None
        self.stats = {
            'total_sent': 0,
            'total_failed': 0,
            'total_cancelled': 0,
            'session_sent': 0,
            'session_failed': 0
        }
        self._load_queue()
    
    def _load_queue(self):
        """加载队列数据"""
        try:
            if self.queue_file.exists():
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.queue = [DanmakuMessage.from_dict(item) for item in data.get('queue', [])]
                    self.stats.update(data.get('stats', {}))
                logger.info(f"加载弹幕队列: {len(self.queue)} 条待处理")
        except Exception as e:
            logger.error(f"加载弹幕队列失败: {e}")
            self.queue = []
    
    def _save_queue(self):
        """保存队列数据"""
        try:
            self.queue_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'queue': [msg.to_dict() for msg in self.queue],
                'stats': self.stats,
                'updated_at': datetime.now().isoformat()
            }
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存弹幕队列失败: {e}")
    
    async def add_message(
        self, 
        text: str, 
        user_id: int,
        priority: int = 1,
        delay: float = 0.0,
        skip_filter: bool = False,
        **style_kwargs
    ) -> str:
        """添加弹幕消息到队列（带内容过滤）"""
        if len(self.queue) >= self.max_queue_size:
            # 移除最旧的低优先级消息
            self._cleanup_queue()
            if len(self.queue) >= self.max_queue_size:
                raise ValueError("队列已满，无法添加新消息")
        
        # 内容过滤检查
        if not skip_filter and content_filter:
            try:
                filter_result = await content_filter.filter_content(text, user_id)
                
                if filter_result.is_blocked:
                    logger.warning(f"用户 {user_id} 的弹幕被阻止: {text[:20]}...")
                    raise ValueError(f"弹幕内容被过滤器阻止: {、'.join(filter_result.warnings)}")
                
                if filter_result.action == FilterAction.REVIEW:
                    logger.info(f"用户 {user_id} 的弹幕需要人工审核: {text[:20]}...")
                    raise ValueError("弹幕内容需要人工审核，请等待审核结果")
                
                # 使用过滤后的文本
                if filter_result.action == FilterAction.REPLACE:
                    text = filter_result.filtered_text
                    logger.info(f"用户 {user_id} 的弹幕内容被替换")
                
                # 记录警告
                if filter_result.warnings:
                    logger.warning(f"用户 {user_id} 的弹幕触发警告: {、'.join(filter_result.warnings)}")
                
            except Exception as e:
                if "被过滤器阻止" in str(e) or "需要人工审核" in str(e):
                    raise
                logger.error(f"内容过滤失败: {e}")
                # 过滤器失败时继续处理，但记录日志
        
        # 生成唯一ID
        message_id = f"dm_{user_id}_{int(datetime.now().timestamp() * 1000)}"
        
        # 创建消息对象
        message = DanmakuMessage(
            id=message_id,
            text=text,
            user_id=user_id,
            priority=priority,
            delay=delay,
            **style_kwargs
        )
        
        # 按优先级插入队列
        self._insert_by_priority(message)
        self._save_queue()
        
        logger.info(f"添加弹幕到队列: {text[:20]}... (优先级: {priority})")
        return message_id
    
    def _insert_by_priority(self, message: DanmakuMessage):
        """按优先级插入消息"""
        # 找到合适的插入位置（高优先级在前）
        for i, existing_msg in enumerate(self.queue):
            if existing_msg.priority < message.priority:
                self.queue.insert(i, message)
                return
        # 如果没有找到合适位置，添加到末尾
        self.queue.append(message)
    
    def _cleanup_queue(self):
        """清理队列中的低优先级消息"""
        # 移除已发送成功或失败的消息
        self.queue = [msg for msg in self.queue if msg.status in [DanmakuStatus.PENDING, DanmakuStatus.SENDING]]
        
        # 如果还是太多，移除最旧的低优先级消息
        if len(self.queue) >= self.max_queue_size:
            self.queue.sort(key=lambda x: (x.priority, x.created_at), reverse=True)
            removed_count = len(self.queue) - self.max_queue_size + 100  # 留出一些空间
            for _ in range(removed_count):
                if self.queue:
                    removed_msg = self.queue.pop()
                    logger.warning(f"队列已满，移除消息: {removed_msg.text[:20]}...")
    
    def remove_message(self, message_id: str) -> bool:
        """从队列中移除消息"""
        for i, msg in enumerate(self.queue):
            if msg.id == message_id:
                if msg.status == DanmakuStatus.SENDING:
                    msg.status = DanmakuStatus.CANCELLED
                else:
                    self.queue.pop(i)
                    self.stats['total_cancelled'] += 1
                self._save_queue()
                return True
        return False
    
    def get_queue_info(self) -> Dict[str, Any]:
        """获取队列信息"""
        status_counts = {}
        for status in DanmakuStatus:
            status_counts[status.value] = sum(1 for msg in self.queue if msg.status == status)
        
        return {
            'total_messages': len(self.queue),
            'status_counts': status_counts,
            'stats': self.stats.copy(),
            'is_processing': self.is_processing,
            'queue_size_limit': self.max_queue_size
        }
    
    def get_user_messages(self, user_id: int, status_filter: Optional[DanmakuStatus] = None) -> List[DanmakuMessage]:
        """获取用户的消息"""
        messages = [msg for msg in self.queue if msg.user_id == user_id]
        if status_filter:
            messages = [msg for msg in messages if msg.status == status_filter]
        return messages
    
    def clear_queue(self, user_id: Optional[int] = None, status_filter: Optional[DanmakuStatus] = None):
        """清空队列"""
        if user_id is None and status_filter is None:
            # 清空整个队列
            cancelled_count = len([msg for msg in self.queue if msg.status == DanmakuStatus.PENDING])
            self.queue.clear()
            self.stats['total_cancelled'] += cancelled_count
        else:
            # 按条件清空
            new_queue = []
            cancelled_count = 0
            for msg in self.queue:
                should_remove = True
                if user_id is not None and msg.user_id != user_id:
                    should_remove = False
                if status_filter is not None and msg.status != status_filter:
                    should_remove = False
                
                if should_remove and msg.status == DanmakuStatus.PENDING:
                    cancelled_count += 1
                elif not should_remove:
                    new_queue.append(msg)
            
            self.queue = new_queue
            self.stats['total_cancelled'] += cancelled_count
        
        self._save_queue()
        logger.info(f"清空队列完成")
    
    async def start_processing(self, danmaku_client, interval: float = 1.0):
        """开始处理队列"""
        if self.is_processing:
            logger.warning("队列处理已在运行中")
            return
        
        self.is_processing = True
        self.processing_task = asyncio.create_task(self._process_queue(danmaku_client, interval))
        logger.info("开始处理弹幕队列")
    
    async def stop_processing(self):
        """停止处理队列"""
        self.is_processing = False
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        logger.info("停止处理弹幕队列")
    
    async def _process_queue(self, danmaku_client, interval: float):
        """处理队列的主循环"""
        try:
            while self.is_processing:
                if not self.queue:
                    await asyncio.sleep(interval)
                    continue
                
                # 找到下一个待发送的消息
                message = None
                for msg in self.queue:
                    if msg.status == DanmakuStatus.PENDING:
                        # 检查是否到了发送时间
                        if msg.delay > 0:
                            send_time = msg.created_at + timedelta(seconds=msg.delay)
                            if datetime.now() < send_time:
                                continue
                        message = msg
                        break
                
                if message is None:
                    await asyncio.sleep(interval)
                    continue
                
                # 发送消息
                await self._send_message(message, danmaku_client)
                
                # 等待间隔
                await asyncio.sleep(interval)
                
        except Exception as e:
            logger.error(f"队列处理出错: {e}")
        finally:
            self.is_processing = False
    
    async def _send_message(self, message: DanmakuMessage, danmaku_client):
        """发送单个消息"""
        message.status = DanmakuStatus.SENDING
        self._save_queue()
        
        try:
            async with danmaku_client as client:
                result = await client.send_danmaku(
                    text=message.text,
                    color=message.color,
                    position=message.position,
                    font_size=message.font_size,
                    duration=message.duration
                )
            
            if result['success']:
                message.status = DanmakuStatus.SUCCESS
                message.sent_at = datetime.now()
                self.stats['total_sent'] += 1
                self.stats['session_sent'] += 1
                logger.info(f"发送弹幕成功: {message.text[:20]}...")
            else:
                raise Exception(result['message'])
                
        except Exception as e:
            message.retry_count += 1
            message.error_message = str(e)
            
            if message.retry_count >= message.max_retries:
                message.status = DanmakuStatus.FAILED
                self.stats['total_failed'] += 1
                self.stats['session_failed'] += 1
                logger.error(f"发送弹幕失败（已达最大重试次数）: {message.text[:20]}... - {e}")
            else:
                message.status = DanmakuStatus.PENDING
                # 延迟重试
                message.delay = 5.0 * message.retry_count
                message.created_at = datetime.now()
                logger.warning(f"发送弹幕失败，将重试: {message.text[:20]}... - {e}")
        
        self._save_queue()


# 全局队列管理器实例
danmaku_queue = DanmakuQueue()