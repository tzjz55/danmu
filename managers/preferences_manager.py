import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, Union
from pathlib import Path
from loguru import logger
from dataclasses import dataclass, asdict
from enum import Enum


class NotificationLevel(Enum):
    """通知级别"""
    ALL = "all"          # 所有通知
    IMPORTANT = "important"  # 重要通知
    ERROR_ONLY = "error_only"  # 仅错误通知
    NONE = "none"        # 无通知


class Theme(Enum):
    """主题样式"""
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    COLORFUL = "colorful"


@dataclass
class UserPreferences:
    """用户偏好设置数据类"""
    user_id: int
    
    # 弹幕偏好设置
    default_color: str = "#FFFFFF"
    default_position: str = "scroll"
    default_font_size: int = 24
    default_duration: int = 5
    favorite_templates: list = None
    
    # 界面偏好设置
    theme: str = Theme.DEFAULT.value
    language: str = "zh-CN"
    notification_level: str = NotificationLevel.IMPORTANT.value
    auto_refresh_status: bool = True
    show_statistics: bool = True
    
    # 功能偏好设置
    auto_start_queue: bool = False
    default_priority: int = 3
    batch_send_interval: float = 1.0
    max_queue_size: int = 100
    enable_cache: bool = True
    
    # 安全和隐私设置
    log_operations: bool = True
    share_statistics: bool = False
    auto_backup: bool = True
    session_timeout: int = 3600  # 秒
    
    # 高级设置
    api_timeout: int = 30
    retry_attempts: int = 3
    rate_limit: int = 10  # 每秒请求数
    debug_mode: bool = False
    
    # 时间戳
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.favorite_templates is None:
            self.favorite_templates = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        """从字典创建"""
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class UserPreferencesManager:
    """用户偏好设置管理器"""
    
    def __init__(self, db_file: str = "data/user_preferences.db"):
        self.db_file = Path(db_file)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._cache = {}  # 内存缓存
        self._cache_timeout = 300  # 5分钟缓存
    
    def _init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        user_id INTEGER PRIMARY KEY,
                        default_color TEXT DEFAULT '#FFFFFF',
                        default_position TEXT DEFAULT 'scroll',
                        default_font_size INTEGER DEFAULT 24,
                        default_duration INTEGER DEFAULT 5,
                        favorite_templates TEXT DEFAULT '[]',
                        theme TEXT DEFAULT 'default',
                        language TEXT DEFAULT 'zh-CN',
                        notification_level TEXT DEFAULT 'important',
                        auto_refresh_status BOOLEAN DEFAULT 1,
                        show_statistics BOOLEAN DEFAULT 1,
                        auto_start_queue BOOLEAN DEFAULT 0,
                        default_priority INTEGER DEFAULT 3,
                        batch_send_interval REAL DEFAULT 1.0,
                        max_queue_size INTEGER DEFAULT 100,
                        enable_cache BOOLEAN DEFAULT 1,
                        log_operations BOOLEAN DEFAULT 1,
                        share_statistics BOOLEAN DEFAULT 0,
                        auto_backup BOOLEAN DEFAULT 1,
                        session_timeout INTEGER DEFAULT 3600,
                        api_timeout INTEGER DEFAULT 30,
                        retry_attempts INTEGER DEFAULT 3,
                        rate_limit INTEGER DEFAULT 10,
                        debug_mode BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建索引
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id)')
                
                conn.commit()
                logger.info("用户偏好设置数据库初始化完成")
                
        except Exception as e:
            logger.error(f"初始化用户偏好设置数据库失败: {e}")
            raise
    
    def _get_cache_key(self, user_id: int) -> str:
        """获取缓存键"""
        return f"user_prefs_{user_id}"
    
    def _set_cache(self, user_id: int, preferences: UserPreferences):
        """设置缓存"""
        cache_key = self._get_cache_key(user_id)
        self._cache[cache_key] = {
            'data': preferences,
            'timestamp': datetime.now()
        }
    
    def _get_from_cache(self, user_id: int) -> Optional[UserPreferences]:
        """从缓存获取数据"""
        cache_key = self._get_cache_key(user_id)
        if cache_key in self._cache:\n            cached_item = self._cache[cache_key]\n            if (datetime.now() - cached_item['timestamp']).seconds < self._cache_timeout:\n                return cached_item['data']\n            else:\n                del self._cache[cache_key]\n        return None\n    \n    def _clear_cache(self, user_id: Optional[int] = None):\n        \"\"\"清理缓存\"\"\"\n        if user_id:\n            cache_key = self._get_cache_key(user_id)\n            self._cache.pop(cache_key, None)\n        else:\n            self._cache.clear()\n    \n    def get_user_preferences(self, user_id: int) -> UserPreferences:\n        \"\"\"获取用户偏好设置\"\"\"\n        # 首先检查缓存\n        cached_prefs = self._get_from_cache(user_id)\n        if cached_prefs:\n            return cached_prefs\n        \n        try:\n            with sqlite3.connect(self.db_file) as conn:\n                cursor = conn.cursor()\n                \n                cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))\n                row = cursor.fetchone()\n                \n                if row:\n                    # 将数据库行转换为字典\n                    columns = [desc[0] for desc in cursor.description]\n                    data = dict(zip(columns, row))\n                    \n                    # 特殊处理 JSON 字段\n                    if 'favorite_templates' in data:\n                        data['favorite_templates'] = json.loads(data['favorite_templates'])\n                    \n                    preferences = UserPreferences.from_dict(data)\n                else:\n                    # 如果用户不存在，创建默认偏好设置\n                    preferences = UserPreferences(user_id=user_id)\n                    self.save_user_preferences(preferences)\n                \n                # 设置缓存\n                self._set_cache(user_id, preferences)\n                return preferences\n                \n        except Exception as e:\n            logger.error(f\"获取用户偏好设置失败: {e}\")\n            # 返回默认设置\n            return UserPreferences(user_id=user_id)\n    \n    def save_user_preferences(self, preferences: UserPreferences) -> bool:\n        \"\"\"保存用户偏好设置\"\"\"\n        try:\n            preferences.updated_at = datetime.now()\n            \n            with sqlite3.connect(self.db_file) as conn:\n                cursor = conn.cursor()\n                \n                # 准备数据\n                favorite_templates_json = json.dumps(preferences.favorite_templates)\n                \n                cursor.execute('''\n                    INSERT OR REPLACE INTO user_preferences (\n                        user_id, default_color, default_position, default_font_size,\n                        default_duration, favorite_templates, theme, language,\n                        notification_level, auto_refresh_status, show_statistics,\n                        auto_start_queue, default_priority, batch_send_interval,\n                        max_queue_size, enable_cache, log_operations, share_statistics,\n                        auto_backup, session_timeout, api_timeout, retry_attempts,\n                        rate_limit, debug_mode, created_at, updated_at\n                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\n                ''', (\n                    preferences.user_id, preferences.default_color, preferences.default_position,\n                    preferences.default_font_size, preferences.default_duration, favorite_templates_json,\n                    preferences.theme, preferences.language, preferences.notification_level,\n                    preferences.auto_refresh_status, preferences.show_statistics,\n                    preferences.auto_start_queue, preferences.default_priority,\n                    preferences.batch_send_interval, preferences.max_queue_size,\n                    preferences.enable_cache, preferences.log_operations,\n                    preferences.share_statistics, preferences.auto_backup,\n                    preferences.session_timeout, preferences.api_timeout,\n                    preferences.retry_attempts, preferences.rate_limit,\n                    preferences.debug_mode, preferences.created_at, preferences.updated_at\n                ))\n                \n                conn.commit()\n                \n                # 更新缓存\n                self._set_cache(preferences.user_id, preferences)\n                \n                logger.debug(f\"保存用户 {preferences.user_id} 的偏好设置成功\")\n                return True\n                \n        except Exception as e:\n            logger.error(f\"保存用户偏好设置失败: {e}\")\n            return False\n    \n    def update_preference(self, user_id: int, key: str, value: Any) -> bool:\n        \"\"\"更新单个偏好设置\"\"\"\n        try:\n            preferences = self.get_user_preferences(user_id)\n            \n            if hasattr(preferences, key):\n                setattr(preferences, key, value)\n                return self.save_user_preferences(preferences)\n            else:\n                logger.warning(f\"未知的偏好设置键: {key}\")\n                return False\n                \n        except Exception as e:\n            logger.error(f\"更新偏好设置失败: {e}\")\n            return False\n    \n    def add_favorite_template(self, user_id: int, template_name: str) -> bool:\n        \"\"\"添加收藏模板\"\"\"\n        try:\n            preferences = self.get_user_preferences(user_id)\n            \n            if template_name not in preferences.favorite_templates:\n                preferences.favorite_templates.append(template_name)\n                return self.save_user_preferences(preferences)\n            \n            return True  # 已存在，认为成功\n            \n        except Exception as e:\n            logger.error(f\"添加收藏模板失败: {e}\")\n            return False\n    \n    def remove_favorite_template(self, user_id: int, template_name: str) -> bool:\n        \"\"\"移除收藏模板\"\"\"\n        try:\n            preferences = self.get_user_preferences(user_id)\n            \n            if template_name in preferences.favorite_templates:\n                preferences.favorite_templates.remove(template_name)\n                return self.save_user_preferences(preferences)\n            \n            return True  # 不存在，认为成功\n            \n        except Exception as e:\n            logger.error(f\"移除收藏模板失败: {e}\")\n            return False\n    \n    def reset_user_preferences(self, user_id: int) -> bool:\n        \"\"\"重置用户偏好设置为默认值\"\"\"\n        try:\n            default_prefs = UserPreferences(user_id=user_id)\n            result = self.save_user_preferences(default_prefs)\n            \n            if result:\n                self._clear_cache(user_id)\n                logger.info(f\"重置用户 {user_id} 的偏好设置为默认值\")\n            \n            return result\n            \n        except Exception as e:\n            logger.error(f\"重置用户偏好设置失败: {e}\")\n            return False\n    \n    def export_preferences(self, user_id: int, file_path: str) -> bool:\n        \"\"\"导出用户偏好设置\"\"\"\n        try:\n            preferences = self.get_user_preferences(user_id)\n            data = preferences.to_dict()\n            \n            with open(file_path, 'w', encoding='utf-8') as f:\n                json.dump(data, f, ensure_ascii=False, indent=2)\n            \n            logger.info(f\"导出用户 {user_id} 的偏好设置到 {file_path}\")\n            return True\n            \n        except Exception as e:\n            logger.error(f\"导出偏好设置失败: {e}\")\n            return False\n    \n    def import_preferences(self, user_id: int, file_path: str) -> bool:\n        \"\"\"导入用户偏好设置\"\"\"\n        try:\n            with open(file_path, 'r', encoding='utf-8') as f:\n                data = json.load(f)\n            \n            # 确保 user_id 正确\n            data['user_id'] = user_id\n            \n            preferences = UserPreferences.from_dict(data)\n            result = self.save_user_preferences(preferences)\n            \n            if result:\n                logger.info(f\"导入用户 {user_id} 的偏好设置从 {file_path}\")\n            \n            return result\n            \n        except Exception as e:\n            logger.error(f\"导入偏好设置失败: {e}\")\n            return False\n    \n    def get_statistics(self) -> Dict[str, Any]:\n        \"\"\"获取偏好设置统计信息\"\"\"\n        try:\n            with sqlite3.connect(self.db_file) as conn:\n                cursor = conn.cursor()\n                \n                # 基础统计\n                cursor.execute('SELECT COUNT(*) FROM user_preferences')\n                total_users = cursor.fetchone()[0]\n                \n                # 主题分布\n                cursor.execute('SELECT theme, COUNT(*) FROM user_preferences GROUP BY theme')\n                theme_distribution = dict(cursor.fetchall())\n                \n                # 语言分布\n                cursor.execute('SELECT language, COUNT(*) FROM user_preferences GROUP BY language')\n                language_distribution = dict(cursor.fetchall())\n                \n                # 通知级别分布\n                cursor.execute('SELECT notification_level, COUNT(*) FROM user_preferences GROUP BY notification_level')\n                notification_distribution = dict(cursor.fetchall())\n                \n                return {\n                    'total_users': total_users,\n                    'theme_distribution': theme_distribution,\n                    'language_distribution': language_distribution,\n                    'notification_distribution': notification_distribution,\n                    'cache_size': len(self._cache)\n                }\n                \n        except Exception as e:\n            logger.error(f\"获取偏好设置统计失败: {e}\")\n            return {}\n    \n    def cleanup_cache(self):\n        \"\"\"清理过期缓存\"\"\"\n        current_time = datetime.now()\n        expired_keys = []\n        \n        for key, cached_item in self._cache.items():\n            if (current_time - cached_item['timestamp']).seconds >= self._cache_timeout:\n                expired_keys.append(key)\n        \n        for key in expired_keys:\n            del self._cache[key]\n        \n        if expired_keys:\n            logger.debug(f\"清理了 {len(expired_keys)} 个过期缓存项\")\n\n\n# 全局偏好设置管理器实例\nuser_prefs_manager = UserPreferencesManager()