import aiosqlite
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
from config import config


class UserManager:
    """用户权限管理器"""
    
    def __init__(self, db_path: str = "data/bot.db"):
        self.db_path = db_path
    
    async def init_database(self):
        """初始化数据库"""
        async with aiosqlite.connect(self.db_path) as db:
            # 创建用户表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    usage_count INTEGER DEFAULT 0
                )
            """)
            
            # 创建操作日志表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS operation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id BIGINT NOT NULL,
                    operation TEXT NOT NULL,
                    parameters TEXT,
                    result TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(telegram_id)
                )
            """)
            
            await db.commit()
            logger.info("数据库初始化完成")
    
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE telegram_id = ?", 
                (telegram_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def create_user(
        self, 
        telegram_id: int, 
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> bool:
        """创建新用户"""
        try:
            # 检查是否为管理员
            role = 'admin' if telegram_id in config.ADMIN_USER_IDS else 'user'
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO users 
                    (telegram_id, username, first_name, last_name, role, created_at, last_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    telegram_id, username, first_name, last_name, 
                    role, datetime.now(), datetime.now()
                ))
                await db.commit()
                
            logger.info(f"用户创建成功: {telegram_id} ({username}) - {role}")
            return True
        except Exception as e:
            logger.error(f"用户创建失败: {e}")
            return False
    
    async def update_user_activity(self, telegram_id: int):
        """更新用户活跃时间和使用次数"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users 
                SET last_active = ?, usage_count = usage_count + 1
                WHERE telegram_id = ?
            """, (datetime.now(), telegram_id))
            await db.commit()
    
    async def is_admin(self, telegram_id: int) -> bool:
        """检查用户是否为管理员"""
        user = await self.get_user(telegram_id)
        return user and user['role'] == 'admin'
    
    async def is_user_active(self, telegram_id: int) -> bool:
        """检查用户是否处于活跃状态"""
        user = await self.get_user(telegram_id)
        return user and user['is_active']
    
    async def set_user_status(self, telegram_id: int, is_active: bool) -> bool:
        """设置用户状态"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE users SET is_active = ? WHERE telegram_id = ?",
                    (is_active, telegram_id)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"设置用户状态失败: {e}")
            return False
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users ORDER BY created_at DESC"
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        async with aiosqlite.connect(self.db_path) as db:
            # 总用户数
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                total_users = (await cursor.fetchone())[0]
            
            # 活跃用户数
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE is_active = TRUE"
            ) as cursor:
                active_users = (await cursor.fetchone())[0]
            
            # 管理员数
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE role = 'admin'"
            ) as cursor:
                admin_users = (await cursor.fetchone())[0]
            
            # 今日活跃用户
            async with db.execute("""
                SELECT COUNT(*) FROM users 
                WHERE date(last_active) = date('now')
            """) as cursor:
                today_active = (await cursor.fetchone())[0]
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'admin_users': admin_users,
                'today_active': today_active
            }
    
    async def log_operation(
        self, 
        user_id: int, 
        operation: str, 
        parameters: Optional[str] = None,
        result: Optional[str] = None
    ):
        """记录用户操作日志"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO operation_logs 
                    (user_id, operation, parameters, result, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, operation, parameters, result, datetime.now()))
                await db.commit()
        except Exception as e:
            logger.error(f"记录操作日志失败: {e}")
    
    async def get_user_logs(
        self, 
        user_id: Optional[int] = None, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取用户操作日志"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if user_id:
                query = """
                    SELECT ol.*, u.username, u.first_name 
                    FROM operation_logs ol
                    JOIN users u ON ol.user_id = u.telegram_id
                    WHERE ol.user_id = ?
                    ORDER BY ol.timestamp DESC
                    LIMIT ?
                """
                params = (user_id, limit)
            else:
                query = """
                    SELECT ol.*, u.username, u.first_name 
                    FROM operation_logs ol
                    JOIN users u ON ol.user_id = u.telegram_id
                    ORDER BY ol.timestamp DESC
                    LIMIT ?
                """
                params = (limit,)
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def register_or_update_user(self, user) -> Dict[str, Any]:
        """注册或更新用户信息"""
        telegram_id = user.id
        username = user.username
        first_name = user.first_name
        last_name = user.last_name
        
        # 检查用户是否存在
        existing_user = await self.get_user(telegram_id)
        
        if existing_user:
            # 更新用户信息
            try:
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute("""
                        UPDATE users 
                        SET username = ?, first_name = ?, last_name = ?, last_active = ?
                        WHERE telegram_id = ?
                    """, (username, first_name, last_name, datetime.now(), telegram_id))
                    await db.commit()
                
                await self.update_user_activity(telegram_id)
                
                return {
                    'success': True,
                    'is_new': False,
                    'user': await self.get_user(telegram_id),
                    'message': '用户信息已更新'
                }
            except Exception as e:
                logger.error(f"更新用户信息失败: {e}")
                return {
                    'success': False,
                    'is_new': False,
                    'user': None,
                    'message': f'更新用户信息失败: {str(e)}'
                }
        else:
            # 创建新用户
            success = await self.create_user(telegram_id, username, first_name, last_name)
            if success:
                return {
                    'success': True,
                    'is_new': True,
                    'user': await self.get_user(telegram_id),
                    'message': '用户注册成功'
                }
            else:
                return {
                    'success': False,
                    'is_new': True,
                    'user': None,
                    'message': '用户注册失败'
                }


# 全局用户管理器实例
user_manager = UserManager()