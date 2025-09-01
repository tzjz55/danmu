import os
from typing import List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # Telegram Bot 配置
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # 弹幕 API 配置
    DANMAKU_API_KEY = os.getenv('DANMAKU_API_KEY')
    DANMAKU_BASE_URL = os.getenv('DANMAKU_BASE_URL', 'http://154.12.85.19:7768')
    
    # TMDB API 配置
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    TMDB_BASE_URL = os.getenv('TMDB_BASE_URL', 'https://api.themoviedb.org/3')
    TMDB_IMAGE_URL = os.getenv('TMDB_IMAGE_URL', 'https://image.tmdb.org')
    
    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/bot.db')
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 管理员配置
    ADMIN_USER_IDS: List[int] = [
        int(uid.strip()) for uid in os.getenv('ADMIN_USER_IDS', '').split(',') 
        if uid.strip().isdigit()
    ]
    
    # 应用信息
    APP_NAME = os.getenv('APP_NAME', 'Danmaku Telegram Bot')
    VERSION = os.getenv('VERSION', '1.0.0')
    
    @classmethod
    def validate(cls) -> bool:
        """验证必要的配置项是否存在"""
        required_configs = [
            'BOT_TOKEN',
            'DANMAKU_API_KEY',
            'TMDB_API_KEY'
        ]
        
        missing_configs = []
        for config in required_configs:
            if not getattr(cls, config):
                missing_configs.append(config)
        
        if missing_configs:
            raise ValueError(f"缺少必要的配置项: {', '.join(missing_configs)}")
        
        return True

# 创建配置实例
config = Config()