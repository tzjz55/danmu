import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from loguru import logger
from dataclasses import dataclass
import asyncio


@dataclass
class DanmakuStatistics:
    """弹幕统计数据类"""
    user_id: int
    date: str  # YYYY-MM-DD 格式
    total_sent: int = 0
    total_failed: int = 0
    total_templates_used: int = 0
    total_custom_sent: int = 0
    avg_response_time: float = 0.0
    peak_hour: int = 0  # 最活跃小时
    most_used_color: str = "#FFFFFF"
    most_used_position: str = "scroll"


class StatisticsManager:
    """弹幕统计管理器"""
    
    def __init__(self, db_file: str = "data/statistics.db"):
        self.db_file = Path(db_file)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # 用户统计表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        total_sent INTEGER DEFAULT 0,
                        total_failed INTEGER DEFAULT 0,
                        total_templates_used INTEGER DEFAULT 0,
                        total_custom_sent INTEGER DEFAULT 0,
                        avg_response_time REAL DEFAULT 0.0,
                        peak_hour INTEGER DEFAULT 0,
                        most_used_color TEXT DEFAULT '#FFFFFF',
                        most_used_position TEXT DEFAULT 'scroll',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, date)
                    )
                ''')
                
                # 弹幕记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS danmaku_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        message_id TEXT,
                        text TEXT NOT NULL,
                        color TEXT DEFAULT '#FFFFFF',
                        position TEXT DEFAULT 'scroll',
                        font_size INTEGER DEFAULT 24,
                        duration INTEGER DEFAULT 5,
                        is_template BOOLEAN DEFAULT 0,
                        template_name TEXT,
                        priority INTEGER DEFAULT 1,
                        status TEXT NOT NULL,
                        response_time REAL DEFAULT 0.0,
                        error_message TEXT,
                        retry_count INTEGER DEFAULT 0,
                        sent_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 系统统计表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL UNIQUE,
                        total_users INTEGER DEFAULT 0,
                        total_messages INTEGER DEFAULT 0,
                        total_success INTEGER DEFAULT 0,
                        total_failed INTEGER DEFAULT 0,
                        avg_queue_size REAL DEFAULT 0.0,
                        peak_concurrent_users INTEGER DEFAULT 0,
                        most_active_hour INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建索引
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_date ON user_statistics(user_id, date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_danmaku_user ON danmaku_records(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_danmaku_date ON danmaku_records(sent_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_date ON system_statistics(date)')
                
                conn.commit()
                logger.info("统计数据库初始化完成")
                
        except Exception as e:
            logger.error(f"初始化统计数据库失败: {e}")
            raise
    
    async def record_danmaku_send(
        self,
        user_id: int,
        message_id: str,
        text: str,
        color: str = "#FFFFFF",
        position: str = "scroll",
        font_size: int = 24,
        duration: int = 5,
        is_template: bool = False,
        template_name: str = "",
        priority: int = 1,
        status: str = "success",
        response_time: float = 0.0,
        error_message: str = "",
        retry_count: int = 0
    ):
        """记录弹幕发送"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO danmaku_records (
                        user_id, message_id, text, color, position, font_size, duration,
                        is_template, template_name, priority, status, response_time,
                        error_message, retry_count, sent_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, message_id, text, color, position, font_size, duration,
                    is_template, template_name, priority, status, response_time,
                    error_message, retry_count, datetime.now()
                ))
                
                conn.commit()
                
                # 异步更新统计
                asyncio.create_task(self._update_user_statistics(user_id))
                asyncio.create_task(self._update_system_statistics())
                
        except Exception as e:
            logger.error(f"记录弹幕发送失败: {e}")
    
    async def _update_user_statistics(self, user_id: int):
        """更新用户统计"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # 获取今日用户数据
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_count,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
                        SUM(CASE WHEN is_template = 1 THEN 1 ELSE 0 END) as template_count,
                        SUM(CASE WHEN is_template = 0 THEN 1 ELSE 0 END) as custom_count,
                        AVG(response_time) as avg_response,
                        color as most_color,
                        position as most_position
                    FROM danmaku_records 
                    WHERE user_id = ? AND DATE(sent_at) = ?
                    GROUP BY color, position
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                ''', (user_id, today))\n                \n                result = cursor.fetchone()\n                \n                if result and result[0] > 0:\n                    # 获取最活跃小时\n                    cursor.execute('''\n                        SELECT strftime('%H', sent_at) as hour, COUNT(*) as count\n                        FROM danmaku_records \n                        WHERE user_id = ? AND DATE(sent_at) = ?\n                        GROUP BY hour\n                        ORDER BY count DESC\n                        LIMIT 1\n                    ''', (user_id, today))\n                    \n                    peak_hour_result = cursor.fetchone()\n                    peak_hour = int(peak_hour_result[0]) if peak_hour_result else 0\n                    \n                    # 更新或插入统计数据\n                    cursor.execute('''\n                        INSERT OR REPLACE INTO user_statistics (\n                            user_id, date, total_sent, total_failed, total_templates_used,\n                            total_custom_sent, avg_response_time, peak_hour, most_used_color,\n                            most_used_position, updated_at\n                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\n                    ''', (\n                        user_id, today, result[1] or 0, result[2] or 0, result[3] or 0,\n                        result[4] or 0, result[5] or 0.0, peak_hour, result[6] or '#FFFFFF',\n                        result[7] or 'scroll', datetime.now()\n                    ))\n                    \n                    conn.commit()\n                    \n        except Exception as e:\n            logger.error(f\"更新用户统计失败: {e}\")\n    \n    async def _update_system_statistics(self):\n        \"\"\"更新系统统计\"\"\"\n        try:\n            today = datetime.now().strftime('%Y-%m-%d')\n            \n            with sqlite3.connect(self.db_file) as conn:\n                cursor = conn.cursor()\n                \n                # 获取今日系统数据\n                cursor.execute('''\n                    SELECT \n                        COUNT(DISTINCT user_id) as total_users,\n                        COUNT(*) as total_messages,\n                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,\n                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count\n                    FROM danmaku_records \n                    WHERE DATE(sent_at) = ?\n                ''', (today,))\n                \n                result = cursor.fetchone()\n                \n                if result:\n                    # 获取最活跃小时\n                    cursor.execute('''\n                        SELECT strftime('%H', sent_at) as hour, COUNT(*) as count\n                        FROM danmaku_records \n                        WHERE DATE(sent_at) = ?\n                        GROUP BY hour\n                        ORDER BY count DESC\n                        LIMIT 1\n                    ''', (today,))\n                    \n                    peak_hour_result = cursor.fetchone()\n                    most_active_hour = int(peak_hour_result[0]) if peak_hour_result else 0\n                    \n                    # 更新或插入系统统计\n                    cursor.execute('''\n                        INSERT OR REPLACE INTO system_statistics (\n                            date, total_users, total_messages, total_success, total_failed,\n                            most_active_hour, updated_at\n                        ) VALUES (?, ?, ?, ?, ?, ?, ?)\n                    ''', (\n                        today, result[0] or 0, result[1] or 0, result[2] or 0,\n                        result[3] or 0, most_active_hour, datetime.now()\n                    ))\n                    \n                    conn.commit()\n                    \n        except Exception as e:\n            logger.error(f\"更新系统统计失败: {e}\")\n    \n    def get_user_statistics(self, user_id: int, days: int = 7) -> Dict[str, Any]:\n        \"\"\"获取用户统计数据\"\"\"\n        try:\n            end_date = datetime.now()\n            start_date = end_date - timedelta(days=days)\n            \n            with sqlite3.connect(self.db_file) as conn:\n                cursor = conn.cursor()\n                \n                # 获取时间段内的统计\n                cursor.execute('''\n                    SELECT \n                        SUM(total_sent) as total_sent,\n                        SUM(total_failed) as total_failed,\n                        SUM(total_templates_used) as templates_used,\n                        SUM(total_custom_sent) as custom_sent,\n                        AVG(avg_response_time) as avg_response\n                    FROM user_statistics\n                    WHERE user_id = ? AND date BETWEEN ? AND ?\n                ''', (user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))\n                \n                summary = cursor.fetchone()\n                \n                # 获取每日数据\n                cursor.execute('''\n                    SELECT date, total_sent, total_failed\n                    FROM user_statistics\n                    WHERE user_id = ? AND date BETWEEN ? AND ?\n                    ORDER BY date DESC\n                ''', (user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))\n                \n                daily_data = cursor.fetchall()\n                \n                # 计算成功率\n                total_sent = summary[0] or 0\n                total_failed = summary[1] or 0\n                total_attempts = total_sent + total_failed\n                success_rate = (total_sent / total_attempts * 100) if total_attempts > 0 else 0\n                \n                return {\n                    'user_id': user_id,\n                    'period_days': days,\n                    'total_sent': total_sent,\n                    'total_failed': total_failed,\n                    'success_rate': round(success_rate, 2),\n                    'templates_used': summary[2] or 0,\n                    'custom_sent': summary[3] or 0,\n                    'avg_response_time': round(summary[4] or 0.0, 3),\n                    'daily_data': [\n                        {'date': row[0], 'sent': row[1], 'failed': row[2]}\n                        for row in daily_data\n                    ]\n                }\n                \n        except Exception as e:\n            logger.error(f\"获取用户统计失败: {e}\")\n            return {}\n    \n    def get_system_statistics(self, days: int = 7) -> Dict[str, Any]:\n        \"\"\"获取系统统计数据\"\"\"\n        try:\n            end_date = datetime.now()\n            start_date = end_date - timedelta(days=days)\n            \n            with sqlite3.connect(self.db_file) as conn:\n                cursor = conn.cursor()\n                \n                # 获取时间段内的统计\n                cursor.execute('''\n                    SELECT \n                        SUM(total_users) as total_users,\n                        SUM(total_messages) as total_messages,\n                        SUM(total_success) as total_success,\n                        SUM(total_failed) as total_failed,\n                        AVG(peak_concurrent_users) as avg_concurrent\n                    FROM system_statistics\n                    WHERE date BETWEEN ? AND ?\n                ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))\n                \n                summary = cursor.fetchone()\n                \n                # 获取每日数据\n                cursor.execute('''\n                    SELECT date, total_users, total_messages, total_success, total_failed\n                    FROM system_statistics\n                    WHERE date BETWEEN ? AND ?\n                    ORDER BY date DESC\n                ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))\n                \n                daily_data = cursor.fetchall()\n                \n                # 获取活跃用户统计\n                cursor.execute('''\n                    SELECT COUNT(DISTINCT user_id) as active_users\n                    FROM danmaku_records\n                    WHERE DATE(sent_at) BETWEEN ? AND ?\n                ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))\n                \n                active_users = cursor.fetchone()[0] or 0\n                \n                # 计算成功率\n                total_success = summary[2] or 0\n                total_failed = summary[3] or 0\n                total_attempts = total_success + total_failed\n                success_rate = (total_success / total_attempts * 100) if total_attempts > 0 else 0\n                \n                return {\n                    'period_days': days,\n                    'total_users': summary[0] or 0,\n                    'active_users': active_users,\n                    'total_messages': summary[1] or 0,\n                    'total_success': total_success,\n                    'total_failed': total_failed,\n                    'success_rate': round(success_rate, 2),\n                    'daily_data': [\n                        {\n                            'date': row[0], \n                            'users': row[1], \n                            'messages': row[2],\n                            'success': row[3],\n                            'failed': row[4]\n                        }\n                        for row in daily_data\n                    ]\n                }\n                \n        except Exception as e:\n            logger.error(f\"获取系统统计失败: {e}\")\n            return {}\n    \n    def get_user_ranking(self, period_days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:\n        \"\"\"获取用户排行榜\"\"\"\n        try:\n            end_date = datetime.now()\n            start_date = end_date - timedelta(days=period_days)\n            \n            with sqlite3.connect(self.db_file) as conn:\n                cursor = conn.cursor()\n                \n                cursor.execute('''\n                    SELECT \n                        user_id,\n                        SUM(total_sent) as total_sent,\n                        SUM(total_failed) as total_failed,\n                        SUM(total_templates_used) as templates_used\n                    FROM user_statistics\n                    WHERE date BETWEEN ? AND ?\n                    GROUP BY user_id\n                    ORDER BY total_sent DESC\n                    LIMIT ?\n                ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), limit))\n                \n                ranking = []\n                for i, row in enumerate(cursor.fetchall(), 1):\n                    total_attempts = (row[1] or 0) + (row[2] or 0)\n                    success_rate = ((row[1] or 0) / total_attempts * 100) if total_attempts > 0 else 0\n                    \n                    ranking.append({\n                        'rank': i,\n                        'user_id': row[0],\n                        'total_sent': row[1] or 0,\n                        'total_failed': row[2] or 0,\n                        'success_rate': round(success_rate, 2),\n                        'templates_used': row[3] or 0\n                    })\n                \n                return ranking\n                \n        except Exception as e:\n            logger.error(f\"获取用户排行榜失败: {e}\")\n            return []\n    \n    def export_statistics(self, file_path: str, user_id: Optional[int] = None, days: int = 30) -> bool:\n        \"\"\"导出统计数据\"\"\"\n        try:\n            end_date = datetime.now()\n            start_date = end_date - timedelta(days=days)\n            \n            data = {\n                'exported_at': datetime.now().isoformat(),\n                'period_days': days,\n                'start_date': start_date.strftime('%Y-%m-%d'),\n                'end_date': end_date.strftime('%Y-%m-%d')\n            }\n            \n            if user_id:\n                data['user_statistics'] = self.get_user_statistics(user_id, days)\n            else:\n                data['system_statistics'] = self.get_system_statistics(days)\n                data['user_ranking'] = self.get_user_ranking(days)\n            \n            with open(file_path, 'w', encoding='utf-8') as f:\n                json.dump(data, f, ensure_ascii=False, indent=2)\n            \n            return True\n            \n        except Exception as e:\n            logger.error(f\"导出统计数据失败: {e}\")\n            return False\n\n\n# 全局统计管理器实例\nstats_manager = StatisticsManager()