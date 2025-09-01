#!/usr/bin/env python3
"""
Telegram 弹幕控制机器人
主应用程序入口
"""

import asyncio
import logging
import sys
from pathlib import Path

from loguru import logger
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from config import config
from managers.user_manager import user_manager
from handlers.commands import (
    start_command, help_command, status_command, admin_command, 
    unknown_command, handle_text_message
)
from handlers.callbacks import button_callback_handler


class DanmakuBot:
    """弹幕控制机器人主类"""
    
    def __init__(self):
        self.application = None
        
    async def setup_logging(self):
        """设置日志系统"""
        # 移除默认日志处理器
        logger.remove()
        
        # 添加控制台输出
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            level=config.LOG_LEVEL,
            colorize=True
        )
        
        # 添加文件输出
        log_file = Path("logs/bot.log")
        log_file.parent.mkdir(exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )
        
        logger.info("日志系统初始化完成")
    
    async def initialize_database(self):
        """初始化数据库"""
        try:
            # 确保数据目录存在
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # 初始化用户管理器数据库
            await user_manager.init_database()
            logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def setup_handlers(self):
        """设置处理器"""
        app = self.application
        
        # 命令处理器
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(CommandHandler("admin", admin_command))
        
        # 回调查询处理器
        app.add_handler(CallbackQueryHandler(button_callback_handler))
        
        # 文本消息处理器
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        
        # 未知命令处理器
        app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
        
        logger.info("处理器设置完成")
    
    async def error_handler(self, update, context):
        """全局错误处理器"""
        logger.error(f"更新处理出错: {context.error}")
        
        # 尝试通知用户
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ 系统出现错误，请稍后重试或联系管理员。"
                )
        except Exception as e:
            logger.error(f"发送错误消息失败: {e}")
    
    async def setup_application(self):
        """设置应用程序"""
        try:
            # 验证配置
            config.validate()
            
            # 创建应用程序
            self.application = Application.builder().token(config.BOT_TOKEN).build()
            
            # 设置错误处理器
            self.application.add_error_handler(self.error_handler)
            
            # 设置命令和回调处理器
            self.setup_handlers()
            
            logger.info("应用程序设置完成")
            
        except Exception as e:
            logger.error(f"应用程序设置失败: {e}")
            raise
    
    async def start_bot(self):
        """启动机器人"""
        try:
            logger.info("正在启动 Telegram 弹幕控制机器人...")
            
            # 设置日志
            await self.setup_logging()
            
            # 初始化数据库
            await self.initialize_database()
            
            # 设置应用程序
            await self.setup_application()
            
            # 启动机器人
            logger.info("机器人启动成功！等待用户消息...")
            await self.application.run_polling(
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True
            )
            
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭机器人...")
        except Exception as e:
            logger.error(f"机器人启动失败: {e}")
            raise
        finally:
            if self.application:
                await self.application.shutdown()
            logger.info("机器人已停止")
    
    async def stop_bot(self):
        """停止机器人"""
        if self.application:
            logger.info("正在停止机器人...")
            await self.application.stop()
            await self.application.shutdown()
            logger.info("机器人已停止")


async def main():
    """主函数"""
    bot = DanmakuBot()
    
    try:
        await bot.start_bot()
    except KeyboardInterrupt:
        logger.info("用户中断，程序退出")
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 设置事件循环策略（Windows 兼容性）
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 运行主程序
    asyncio.run(main())