from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from typing import Dict, Any

from managers.user_manager import user_manager
from utils.keyboards import keyboards
from clients.danmaku_client import danmaku_client
from clients.tmdb_client import tmdb_client


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /start 命令"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # 注册或更新用户
    result = await user_manager.register_or_update_user(user)
    
    if result['success']:
        # 记录操作日志
        await user_manager.log_operation(
            user.id, 
            'start_command', 
            None, 
            'success'
        )
        
        welcome_text = f"""
🎮 欢迎使用弹幕控制中心！

👋 你好 {user.first_name}！

这个机器人可以帮助你：
• 📊 监控弹幕服务器状态
• 🎯 管理弹幕内容和设置
• 🎬 搜索电影信息
• 📋 查看操作日志

请选择你要使用的功能：
        """
        
        if result['is_new']:
            if result['user']['role'] == 'admin':
                welcome_text += "\n🔑 你拥有管理员权限！"
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=keyboards.main_menu()
        )
    else:
        await update.message.reply_text(
            "❌ 初始化失败，请稍后重试或联系管理员。",
            reply_markup=keyboards.back_to_menu()
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /help 命令"""
    user = update.effective_user
    
    help_text = """
📖 **帮助信息**

**主要功能：**
• `/start` - 启动机器人，显示主菜单
• `/status` - 快速查看服务器状态
• `/help` - 显示帮助信息

**按钮功能说明：**

🏠 **主菜单**
├─ 📊 服务器状态 - 查看弹幕服务器运行状态
├─ 🎬 电影搜索 - 搜索TMDB电影数据库
├─ 🎯 弹幕管理 - 控制弹幕显示和设置
├─ ⚙️ 设置 - 个人偏好设置
├─ 📋 操作日志 - 查看操作历史
└─ ❓ 帮助 - 显示此帮助信息

🎯 **弹幕管理**
├─ ⏸️ 暂停/▶️ 恢复 - 控制弹幕播放
├─ 🚫 清空弹幕 - 清除当前所有弹幕
├─ 💬 发送弹幕 - 手动发送弹幕内容
├─ ⚙️ 显示设置 - 调整速度和透明度
└─ 🎨 样式设置 - 自定义弹幕样式

🎬 **电影搜索**
├─ 🔍 搜索电影 - 按名称搜索
├─ 📄 电影详情 - 查看详细信息
├─ 👥 演职员表 - 查看参与人员
└─ 💬 发送弹幕 - 发送电影相关弹幕

**使用提示：**
• 大部分操作都会有确认步骤
• 操作结果会实时显示
• 所有操作都会记录在日志中
• 如遇问题请联系管理员
    """
    
    # 管理员额外帮助
    is_admin = await user_manager.is_admin(user.id)
    if is_admin:
        help_text += """
        
🔑 **管理员功能：**
• `/admin` - 进入管理员面板
• 用户权限管理
• 系统状态监控
• 全局设置调整
• 紧急操作功能
        """
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=keyboards.back_to_menu()
    )
    
    # 记录操作
    await user_manager.log_operation(user.id, 'help_command', None, 'success')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /status 命令"""
    user = update.effective_user
    
    # 检查用户权限
    if not await user_manager.is_user_active(user.id):
        await update.message.reply_text("❌ 您的账户已被禁用，请联系管理员。")
        return
    
    await update.message.reply_text("📊 正在获取服务器状态...")
    
    # 获取服务器状态
    async with danmaku_client as client:
        status_result = await client.get_status()
    
    if status_result['success']:
        data = status_result['data']
        
        # 格式化状态信息
        status_text = f"""
📊 **服务器状态**

🟢 **在线状态**: {"✅ 运行中" if data.get('online', False) else "❌ 离线"}
💻 **CPU使用率**: {data.get('cpu_usage', 'N/A')}%
🧠 **内存使用**: {data.get('memory_usage', 'N/A')}MB
👥 **连接数**: {data.get('connections', 'N/A')}
💬 **弹幕总数**: {data.get('total_danmaku', 'N/A')}
⏰ **运行时间**: {data.get('uptime', 'N/A')}

最后更新: {data.get('last_update', 'N/A')}
        """
        
        await update.message.edit_text(
            status_text,
            parse_mode='Markdown',
            reply_markup=keyboards.server_status()
        )
        
        # 记录操作
        await user_manager.log_operation(
            user.id, 
            'status_command', 
            None, 
            'success'
        )
    else:
        await update.message.edit_text(
            f"❌ 获取服务器状态失败：{status_result['message']}",
            reply_markup=keyboards.back_to_menu()
        )
        
        # 记录操作
        await user_manager.log_operation(
            user.id, 
            'status_command', 
            None, 
            f"failed: {status_result['message']}"
        )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /admin 命令"""
    user = update.effective_user
    
    # 检查管理员权限
    if not await user_manager.is_admin(user.id):
        await update.message.reply_text("❌ 您没有管理员权限。")
        return
    
    # 获取系统统计
    stats = await user_manager.get_user_stats()
    
    admin_text = f"""
🔑 **管理员控制面板**

📊 **系统统计**
👥 总用户数: {stats['total_users']}
✅ 活跃用户: {stats['active_users']}
🔑 管理员数: {stats['admin_users']}
📅 今日活跃: {stats['today_active']}

请选择管理功能：
    """
    
    await update.message.reply_text(
        admin_text,
        parse_mode='Markdown',
        reply_markup=keyboards.admin_panel()
    )
    
    # 记录操作
    await user_manager.log_operation(user.id, 'admin_command', None, 'success')


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理未知命令"""
    user = update.effective_user
    
    await update.message.reply_text(
        "❓ 未知命令。请使用 /help 查看可用命令。",
        reply_markup=keyboards.back_to_menu()
    )
    
    # 记录操作
    await user_manager.log_operation(
        user.id, 
        'unknown_command', 
        update.message.text, 
        'unknown'
    )


# 权限检查装饰器
def require_permission(permission: str = 'user'):
    """权限检查装饰器"""
    def decorator(func):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user = update.effective_user
            
            if permission == 'admin':
                if not await user_manager.is_admin(user.id):
                    await update.message.reply_text("❌ 您没有管理员权限。")
                    return
            
            if not await user_manager.is_user_active(user.id):
                await update.message.reply_text("❌ 您的账户已被禁用，请联系管理员。")
                return
            
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator


# 消息处理器
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理文本消息"""
    user = update.effective_user
    message_text = update.message.text
    
    # 检查是否在等待用户输入
    user_data = context.user_data
    
    if user_data.get('waiting_for_movie_search'):
        # 处理电影搜索
        user_data['waiting_for_movie_search'] = False
        
        await update.message.reply_text("🔍 正在搜索电影...")
        
        async with tmdb_client as client:
            search_result = await client.search_movies(message_text)
        
        if search_result['success'] and search_result['data']['movies']:
            movies = search_result['data']['movies']
            total_pages = search_result['data']['total_pages']
            
            # 保存搜索结果到上下文
            context.user_data['search_results'] = movies
            context.user_data['search_query'] = message_text
            context.user_data['current_page'] = 1
            context.user_data['total_pages'] = total_pages
            
            result_text = f"🎬 搜索结果：找到 {len(movies)} 部电影\n\n"
            for i, movie in enumerate(movies[:3], 1):
                title = movie.get('title', 'Unknown')
                year = movie.get('release_date', '')[:4] if movie.get('release_date') else ''
                rating = movie.get('vote_average', 0)
                result_text += f"{i}. **{title}**"
                if year:
                    result_text += f" ({year})"
                result_text += f" ⭐ {rating}/10\n"
            
            if len(movies) > 3:
                result_text += f"\n还有 {len(movies) - 3} 部电影..."
            
            await update.message.reply_text(
                result_text,
                parse_mode='Markdown',
                reply_markup=keyboards.movie_search_results(movies, 1, total_pages)
            )
        else:
            await update.message.reply_text(
                f"😔 未找到相关电影，请尝试其他关键词。",
                reply_markup=keyboards.back_to_menu()
            )
        
        # 记录操作
        await user_manager.log_operation(
            user.id, 
            'movie_search', 
            message_text, 
            'success' if search_result['success'] else 'failed'
        )
    
    elif user_data.get('waiting_for_danmaku_text'):
        # 处理弹幕发送
        user_data['waiting_for_danmaku_text'] = False
        
        await update.message.reply_text("💬 正在发送弹幕...")
        
        async with danmaku_client as client:
            send_result = await client.send_danmaku(message_text)
        
        if send_result['success']:
            await update.message.reply_text(
                f"✅ 弹幕发送成功！\n内容：{message_text}",
                reply_markup=keyboards.danmaku_control()
            )
        else:
            await update.message.reply_text(
                f"❌ 弹幕发送失败：{send_result['message']}",
                reply_markup=keyboards.danmaku_control()
            )
        
        # 记录操作
        await user_manager.log_operation(
            user.id, 
            'send_danmaku', 
            message_text, 
            'success' if send_result['success'] else f"failed: {send_result['message']}"
        )
    
    else:
        # 默认回复
        await update.message.reply_text(
            "请使用菜单按钮进行操作，或发送 /help 查看帮助。",
            reply_markup=keyboards.main_menu()
        )