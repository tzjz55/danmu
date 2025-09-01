from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from typing import Dict, Any

from managers.user_manager import user_manager
<<<<<<< HEAD
from managers.template_manager import template_manager
from managers.queue_manager import danmaku_queue
from managers.content_filter import content_filter
=======
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
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
<<<<<<< HEAD
        # 处理普通弹幕发送
        user_data['waiting_for_danmaku_text'] = False
        style = user_data.get('danmaku_style', 'normal')
        
        # 内容过滤检查
        filter_result = await content_filter.filter_content(message_text, user.id)
        
        if filter_result.is_blocked:
            await update.message.reply_text(
                f"🚫 弹幕被过滤系统拦截\n\n"
                f"原因: {', '.join(filter_result.warnings) if filter_result.warnings else '触发安全规则'}\n"
                f"风险等级: {filter_result.risk_level.value.upper()}\n\n"
                f"请修改内容后重试。",
                reply_markup=keyboards.danmaku_control()
            )
            return
        
        # 如果需要人工审核
        if filter_result.action.value == 'review':
            await update.message.reply_text(
                f"⏳ 弹幕内容需要人工审核\n\n"
                f"内容: {message_text}\n"
                f"状态: 已提交审核，请等待管理员处理\n\n"
                f"审核通过后将自动发送。",
                reply_markup=keyboards.danmaku_control()
            )
            # 这里可以通知管理员进行审核
            return
        
        # 检查是否有警告
        warning_text = ""
        if filter_result.warnings:
            warning_text = f"\n⚠️ 警告: {', '.join(filter_result.warnings)}"
        
        # 使用过滤后的文本
        final_text = filter_result.filtered_text
        
        await update.message.reply_text(f"💬 正在发送弹幕...{warning_text}")
        
        async with danmaku_client as client:
            if style == 'quick':
                send_result = await client.send_danmaku(final_text)
            else:
                send_result = await client.send_danmaku(final_text)
        
        if send_result['success']:
            success_msg = f"✅ 弹幕发送成功！\n内容：{final_text}"
            if final_text != message_text:
                success_msg += f"\n\n📝 原始内容: {message_text}\n🔄 过滤后: {final_text}"
            if warning_text:
                success_msg += warning_text
            
            await update.message.reply_text(
                success_msg,
=======
        # 处理弹幕发送
        user_data['waiting_for_danmaku_text'] = False
        
        await update.message.reply_text("💬 正在发送弹幕...")
        
        async with danmaku_client as client:
            send_result = await client.send_danmaku(message_text)
        
        if send_result['success']:
            await update.message.reply_text(
                f"✅ 弹幕发送成功！\n内容：{message_text}",
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
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
<<<<<<< HEAD
            {'original': message_text, 'filtered': final_text, 'filter_action': filter_result.action.value}, 
            'success' if send_result['success'] else f"failed: {send_result['message']}"
        )
        
        # 清理用户数据
        user_data.pop('danmaku_style', None)
    
    elif user_data.get('waiting_for_custom_danmaku'):
        # 处理自定义样式弹幕发送
        user_data['waiting_for_custom_danmaku'] = False
        custom_style = user_data.get('custom_danmaku_style', {})
        
        await update.message.reply_text("🎨 正在发送自定义样式弹幕...")
        
        async with danmaku_client as client:
            send_result = await client.send_danmaku(
                text=message_text,
                color=custom_style.get('color', '#FFFFFF'),
                position=custom_style.get('position', 'scroll'),
                font_size=custom_style.get('font_size', 24),
                duration=custom_style.get('duration', 5)
            )
        
        if send_result['success']:
            style_info = f"颜色: {custom_style.get('color', '#FFFFFF')}, 位置: {custom_style.get('position', 'scroll')}, 字体: {custom_style.get('font_size', 24)}px"
            await update.message.reply_text(
                f"✅ 自定义弹幕发送成功！\n内容：{message_text}\n样式：{style_info}",
                reply_markup=keyboards.danmaku_style_menu()
            )
        else:
            await update.message.reply_text(
                f"❌ 弹幕发送失败：{send_result['message']}",
                reply_markup=keyboards.danmaku_style_menu()
            )
        
        # 记录操作
        await user_manager.log_operation(
            user.id, 
            'send_custom_danmaku', 
            {'text': message_text, 'style': custom_style}, 
            'success' if send_result['success'] else f"failed: {send_result['message']}"
        )
    
    elif user_data.get('waiting_for_bulk_text'):
        # 处理批量文本发送
        user_data['waiting_for_bulk_text'] = False
        
        # 解析文本列表
        lines = [line.strip() for line in message_text.split('\n') if line.strip()]
        if not lines:
            await update.message.reply_text(
                "❌ 没有有效的弹幕内容",
                reply_markup=keyboards.bulk_send_menu()
            )
            return
        
        if len(lines) > 50:
            await update.message.reply_text(
                "❌ 一次最多只能批量发遑50条弹幕",
                reply_markup=keyboards.bulk_send_menu()
            )
            return
        
        await update.message.reply_text(f"📦 正在添加 {len(lines)} 条弹幕到队列...")
        
        # 添加到队列
        success_count = 0
        failed_count = 0
        
        for i, text in enumerate(lines):
            try:
                message_id = danmaku_queue.add_message(
                    text=text,
                    user_id=user.id,
                    priority=2,  # 批量消息使用低优先级
                    delay=i * 1.0  # 每条消息间隔1秒
                )
                success_count += 1
            except Exception as e:
                logger.error(f"添加批量弹幕失败: {e}")
                failed_count += 1
        
        result_text = f"📦 批量添加完成\n✅ 成功: {success_count} 条\n❌ 失败: {failed_count} 条"
        
        if success_count > 0:
            result_text += "\n\n📄 消息已添加到队列，开始处理后将自动发送"
        
        await update.message.reply_text(
            result_text,
            reply_markup=keyboards.queue_management()
        )
        
        # 记录操作
        await user_manager.log_operation(
            user.id, 
            'bulk_send_danmaku', 
            f'{len(lines)} messages', 
            f'success: {success_count}, failed: {failed_count}'
        )
    
    elif user_data.get('waiting_for_filter_rule'):
        # 处理添加过滤规则
        user_data['waiting_for_filter_rule'] = False
        
        # 解析规则配置（格式：规则名称|类型|模式|动作|风险等级）
        try:
            parts = message_text.split('|')
            if len(parts) != 5:
                await update.message.reply_text(
                    "❌ 格式错误，请按照以下格式输入：\n规则名称|类型|模式|动作|风险等级\n\n示例：\n广告过滤|regex|加群|block|high",
                    reply_markup=keyboards.back_to_content_moderation()
                )
                return
            
            name, filter_type, pattern, action, risk_level = [p.strip() for p in parts]
            
            # 验证参数
            from managers.content_filter import FilterType, FilterAction, RiskLevel, FilterRule
            import uuid
            
            # 检查枚举值是否有效
            try:
                filter_type_enum = FilterType(filter_type.lower())
                action_enum = FilterAction(action.lower())
                risk_level_enum = RiskLevel(risk_level.lower())
            except ValueError as e:
                await update.message.reply_text(
                    f"❌ 参数错误: {e}\n\n有效值：\n"
                    f"类型: keyword, regex, length, rate_limit\n"
                    f"动作: allow, block, warning, replace, review\n"
                    f"风险: low, medium, high, critical",
                    reply_markup=keyboards.back_to_content_moderation()
                )
                return
            
            # 创建规则
            rule = FilterRule(
                id=str(uuid.uuid4())[:8],
                name=name,
                filter_type=filter_type_enum,
                pattern=pattern,
                action=action_enum,
                risk_level=risk_level_enum,
                created_by=user.id
            )
            
            # 添加规则
            success = content_filter.add_rule(rule)
            
            if success:
                await update.message.reply_text(
                    f"✅ 过滤规则添加成功！\n\n"
                    f"规则名称: {name}\n"
                    f"类型: {filter_type}\n"
                    f"模式: {pattern}\n"
                    f"动作: {action}\n"
                    f"风险等级: {risk_level}",
                    reply_markup=keyboards.content_moderation_menu()
                )
            else:
                await update.message.reply_text(
                    "❌ 添加规则失败，请检查规则配置",
                    reply_markup=keyboards.content_moderation_menu()
                )
            
            # 记录操作
            await user_manager.log_operation(
                user.id,
                'add_filter_rule',
                {'name': name, 'type': filter_type, 'pattern': pattern},
                'success' if success else 'failed'
            )
            
        except Exception as e:
            logger.error(f"添加过滤规则错误: {e}")
            await update.message.reply_text(
                f"❌ 处理规则时发生错误: {str(e)}",
                reply_markup=keyboards.back_to_content_moderation()
            )
=======
            message_text, 
            'success' if send_result['success'] else f"failed: {send_result['message']}"
        )
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
    
    else:
        # 默认回复
        await update.message.reply_text(
            "请使用菜单按钮进行操作，或发送 /help 查看帮助。",
            reply_markup=keyboards.main_menu()
        )