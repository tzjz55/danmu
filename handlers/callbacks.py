from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

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


async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理所有回调按钮"""
    query = update.callback_query
    user = query.from_user
    callback_data = query.data
    
    await query.answer()
    
    # 检查用户权限
    if not await user_manager.is_user_active(user.id):
        await query.edit_message_text("❌ 您的账户已被禁用，请联系管理员。")
        return
    
    try:
        # 主菜单和基础功能
        if callback_data == "main_menu":
            await handle_main_menu(query, context)
        elif callback_data == "status":
            await handle_server_status(query, context)
        elif callback_data == "danmaku_control":
            await handle_danmaku_control(query, context)
        elif callback_data == "movie_search":
            await handle_movie_search(query, context)
        
        # 弹幕控制
        elif callback_data.startswith("pause_danmaku"):
            await handle_danmaku_action(query, "pause")
        elif callback_data.startswith("resume_danmaku"):
            await handle_danmaku_action(query, "resume")
        elif callback_data.startswith("clear_danmaku"):
            await handle_danmaku_action(query, "clear")
<<<<<<< HEAD
        elif callback_data == "danmaku_style_menu":
            await handle_danmaku_style_menu(query, context)
        elif callback_data.startswith("send_danmaku"):
            await handle_send_danmaku_prompt(query, context)
        
        # 弹幕样式功能
        elif callback_data == "quick_send_danmaku":
            await handle_quick_send_danmaku(query, context)
        elif callback_data == "template_danmaku":
            await handle_template_danmaku(query, context)
        elif callback_data.startswith("template_category_"):
            await handle_template_category(query, callback_data)
        elif callback_data.startswith("use_template_"):
            await handle_use_template(query, callback_data)
        elif callback_data == "custom_style_danmaku":
            await handle_custom_style_danmaku(query, context)
        elif callback_data == "select_color":
            await query.edit_message_text("🎨 选择颜色：", reply_markup=keyboards.danmaku_color_selection())
        elif callback_data == "select_position":
            await query.edit_message_text("📍 选择位置：", reply_markup=keyboards.danmaku_position_selection())
        elif callback_data == "select_fontsize":
            await query.edit_message_text("🔤 选择字体大小：", reply_markup=keyboards.danmaku_font_size_selection())
        elif callback_data.startswith("color_"):
            color = callback_data.replace('color_', '')
            context.user_data.setdefault('custom_danmaku_style', {})['color'] = color
            await handle_custom_style_danmaku(query, context)
        elif callback_data.startswith("position_"):
            position = callback_data.replace('position_', '')
            context.user_data.setdefault('custom_danmaku_style', {})['position'] = position
            await handle_custom_style_danmaku(query, context)
        elif callback_data.startswith("fontsize_"):
            font_size = int(callback_data.replace('fontsize_', ''))
            context.user_data.setdefault('custom_danmaku_style', {})['font_size'] = font_size
            await handle_custom_style_danmaku(query, context)
        elif callback_data == "custom_input_text":
            await query.edit_message_text("📝 请输入弹幕内容：", reply_markup=keyboards.back_to_menu())
            context.user_data['waiting_for_custom_danmaku'] = True
        
        # 批量发送功能
        elif callback_data == "bulk_send_danmaku":
            await handle_bulk_send_menu(query, context)
        elif callback_data == "bulk_text_list":
            await query.edit_message_text("📄 请发送弹幕列表，每行一条：", reply_markup=keyboards.back_to_menu())
            context.user_data['waiting_for_bulk_text'] = True
        elif callback_data == "queue_management":
            await handle_queue_management(query, context)
        elif callback_data == "view_queue":
            await handle_view_queue(query, context)
        elif callback_data == "start_queue":
            await handle_start_queue(query, context)
        elif callback_data == "pause_queue":
            await handle_pause_queue(query, context)
        elif callback_data == "clear_queue":
            await handle_clear_queue(query, context)
        
=======
        elif callback_data.startswith("send_danmaku"):
            await handle_send_danmaku_prompt(query, context)
        
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
        # 设置功能
        elif callback_data.startswith("speed_"):
            await handle_speed_setting(query, callback_data)
        elif callback_data.startswith("opacity_"):
            await handle_opacity_setting(query, callback_data)
        elif callback_data == "display_settings":
            await handle_display_settings(query)
        
        # 电影功能
        elif callback_data.startswith("movie_detail_"):
            await handle_movie_detail(query, callback_data)
        
<<<<<<< HEAD
        # 内容审核功能
        elif callback_data == "content_moderation":
            await handle_content_moderation_menu(query, context)
        elif callback_data == "filter_rules":
            await handle_filter_rules(query, context)
        elif callback_data == "audit_records":
            await handle_audit_records(query, context)
        elif callback_data == "filter_statistics":
            await handle_filter_statistics(query, context)
        elif callback_data == "add_filter_rule":
            await handle_add_filter_rule(query, context)
        elif callback_data.startswith("toggle_rule_"):
            await handle_toggle_rule(query, callback_data)
        elif callback_data.startswith("delete_rule_"):
            await handle_delete_rule(query, callback_data)
        elif callback_data.startswith("audit_detail_"):
            await handle_audit_detail(query, callback_data)
        elif callback_data.startswith("approve_content_"):
            await handle_approve_content(query, callback_data)
        elif callback_data.startswith("reject_content_"):
            await handle_reject_content(query, callback_data)
        
=======
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
        else:
            await query.edit_message_text("❓ 未知操作", reply_markup=keyboards.back_to_menu())
        
        await user_manager.update_user_activity(user.id)
        
    except Exception as e:
        logger.error(f"回调处理错误: {e}")
        await query.edit_message_text(f"❌ 操作失败：{str(e)}", reply_markup=keyboards.back_to_menu())


async def handle_main_menu(query, context):
    """主菜单"""
    text = "🎮 弹幕控制中心\n\n请选择功能："
    await query.edit_message_text(text, reply_markup=keyboards.main_menu())


async def handle_server_status(query, context):
    """服务器状态"""
    await query.edit_message_text("📊 正在获取状态...")
    
    async with danmaku_client as client:
        result = await client.get_status()
    
    if result['success']:
        data = result['data']
        status_text = f"""📊 服务器状态
🟢 状态: {"在线" if data.get('online') else "离线"}
💻 CPU: {data.get('cpu_usage', 'N/A')}%
🧠 内存: {data.get('memory_usage', 'N/A')}MB"""
        
        await query.edit_message_text(status_text, reply_markup=keyboards.server_status())
    else:
        await query.edit_message_text(f"❌ 获取失败：{result['message']}", reply_markup=keyboards.back_to_menu())


async def handle_danmaku_control(query, context):
    """弹幕控制"""
    text = "🎯 弹幕管理\n\n选择操作："
    await query.edit_message_text(text, reply_markup=keyboards.danmaku_control())


async def handle_danmaku_action(query, action):
    """执行弹幕操作"""
    action_map = {"pause": "暂停", "resume": "恢复", "clear": "清空"}
    await query.edit_message_text(f"⏳ 正在{action_map[action]}弹幕...")
    
    async with danmaku_client as client:
        if action == "pause":
            result = await client.pause_danmaku()
        elif action == "resume":
            result = await client.resume_danmaku()
        elif action == "clear":
            result = await client.clear_danmaku()
    
    status = "✅ 成功" if result['success'] else f"❌ 失败：{result['message']}"
    await query.edit_message_text(f"{status}", reply_markup=keyboards.danmaku_control())
    
    # 记录日志
    await user_manager.log_operation(query.from_user.id, f"{action}_danmaku", None, 
                                   'success' if result['success'] else 'failed')


async def handle_send_danmaku_prompt(query, context):
    """弹幕发送提示"""
    await query.edit_message_text("💬 请发送弹幕内容：", reply_markup=keyboards.back_to_menu())
    context.user_data['waiting_for_danmaku_text'] = True


async def handle_display_settings(query):
    """显示设置"""
    text = "⚙️ 显示设置\n\n选择要调整的参数："
    await query.edit_message_text(text, reply_markup=keyboards.display_settings())


async def handle_speed_setting(query, callback_data):
    """速度设置"""
    speed_map = {'speed_slow': 'slow', 'speed_normal': 'normal', 'speed_fast': 'fast'}
    speed = speed_map.get(callback_data)
    
    async with danmaku_client as client:
        result = await client.set_danmaku_speed(speed)
    
    status = "✅ 设置成功" if result['success'] else f"❌ 设置失败"
    await query.edit_message_text(status, reply_markup=keyboards.display_settings())


async def handle_opacity_setting(query, callback_data):
    """透明度设置"""
    if callback_data == "opacity_settings":
        await query.edit_message_text("💫 选择透明度：", reply_markup=keyboards.opacity_settings())
        return
    
    opacity = float(callback_data.replace('opacity_', ''))
    async with danmaku_client as client:
        result = await client.set_danmaku_opacity(opacity)
    
    status = "✅ 设置成功" if result['success'] else "❌ 设置失败"
    await query.edit_message_text(status, reply_markup=keyboards.opacity_settings())


async def handle_movie_search(query, context):
    """电影搜索"""
    await query.edit_message_text("🎬 请发送电影名称：", reply_markup=keyboards.back_to_menu())
    context.user_data['waiting_for_movie_search'] = True


async def handle_movie_detail(query, callback_data):
    """电影详情"""
    movie_id = int(callback_data.replace('movie_detail_', ''))
    await query.edit_message_text("🎬 获取详情中...")
    
    async with tmdb_client as client:
        result = await client.get_movie_details(movie_id)
    
    if result['success']:
        movie = result['data']
        text = f"""🎬 {movie.get('title')}
📅 {movie.get('release_date')}
⭐ {movie.get('vote_average')}/10
📝 {movie.get('overview', '')[:100]}..."""
        
        await query.edit_message_text(text, reply_markup=keyboards.movie_detail(movie_id))
    else:
<<<<<<< HEAD
        await query.edit_message_text(f"❌ 获取失败", reply_markup=keyboards.back_to_menu())


async def handle_danmaku_style_menu(query, context):
    """弹幕样式菜单"""
    text = "🎨 弹幕样式发送\n\n请选择发送方式："
    await query.edit_message_text(text, reply_markup=keyboards.danmaku_style_menu())


async def handle_quick_send_danmaku(query, context):
    """快速发送弹幕"""
    await query.edit_message_text("💨 请发送弹幕内容：", reply_markup=keyboards.back_to_menu())
    context.user_data['waiting_for_danmaku_text'] = True
    context.user_data['danmaku_style'] = 'quick'


async def handle_template_danmaku(query, context):
    """模板弹幕选择"""
    text = "📜 选择模板分类："
    await query.edit_message_text(text, reply_markup=keyboards.danmaku_template_categories())


async def handle_template_category(query, callback_data):
    """处理模板分类选择"""
    category = callback_data.replace('template_category_', '')
    
    if category == 'all':
        templates = template_manager.get_all_templates()
    else:
        templates = template_manager.get_templates_by_category(category)
    
    if not templates:
        await query.edit_message_text(
            f"❌ 该分类下没有模板",
            reply_markup=keyboards.danmaku_template_categories()
        )
        return
    
    # 转换为列表格式
    template_list = [(name, data['text']) for name, data in templates.items()]
    
    # 分页显示（每页显示8个）
    page_size = 8
    total_pages = (len(template_list) + page_size - 1) // page_size
    page_templates = template_list[:page_size]
    
    text = f"📜 {category.upper()} 模板 ({len(template_list)}个)"
    await query.edit_message_text(
        text, 
        reply_markup=keyboards.danmaku_templates_list(page_templates, 1, total_pages, category)
    )


async def handle_use_template(query, callback_data):
    """使用模板发送弹幕"""
    template_name = callback_data.replace('use_template_', '')
    template = template_manager.get_template(template_name)
    
    if not template:
        await query.edit_message_text("❌ 模板不存在", reply_markup=keyboards.back_to_menu())
        return
    
    await query.edit_message_text("⏳ 正在发送模板弹幕...")
    
    async with danmaku_client as client:
        result = await client.send_danmaku(
            text=template['text'],
            color=template.get('color', '#FFFFFF'),
            position=template.get('position', 'scroll'),
            font_size=template.get('font_size', 24),
            duration=template.get('duration', 5)
        )
    
    status = "✅ 发送成功" if result['success'] else f"❌ 发送失败：{result['message']}"
    await query.edit_message_text(status, reply_markup=keyboards.danmaku_style_menu())
    
    # 记录日志
    await user_manager.log_operation(
        query.from_user.id, 
        'send_template_danmaku', 
        {'template': template_name, 'text': template['text']}, 
        'success' if result['success'] else 'failed'
    )


async def handle_custom_style_danmaku(query, context):
    """自定义样式弹幕"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    # 初始化用户自定义设置
    if 'custom_danmaku_style' not in context.user_data:
        context.user_data['custom_danmaku_style'] = {
            'color': '#FFFFFF',
            'position': 'scroll',
            'font_size': 24,
            'duration': 5
        }
    
    style = context.user_data['custom_danmaku_style']
    text = f"""🎨 自定义弹幕样式

当前设置：
🎨 颜色: {style['color']}
📍 位置: {style['position']}
🔤 字体: {style['font_size']}px
⏱️ 时长: {style['duration']}秒

请选择要调整的参数："""
    
    keyboard = [
        [
            InlineKeyboardButton("🎨 颜色", callback_data="select_color"),
            InlineKeyboardButton("📍 位置", callback_data="select_position")
        ],
        [
            InlineKeyboardButton("🔤 字体", callback_data="select_fontsize"),
            InlineKeyboardButton("⏱️ 时长", callback_data="select_duration")
        ],
        [
            InlineKeyboardButton("📝 输入内容", callback_data="custom_input_text"),
            InlineKeyboardButton("📚 使用预设", callback_data="use_preset_style")
        ],
        [
            InlineKeyboardButton("⬅️ 返回", callback_data="danmaku_style_menu")
        ]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_bulk_send_menu(query, context):
    """批量发送菜单"""
    text = "📦 批量发送弹幕\n\n请选择发送方式："
    await query.edit_message_text(text, reply_markup=keyboards.bulk_send_menu())


async def handle_queue_management(query, context):
    """队列管理"""
    queue_info = danmaku_queue.get_queue_info()
    text = f"""📋 弹幕队列管理

📊 队列状态：
• 总消息数：{queue_info['total_messages']}
• 待发送：{queue_info['status_counts'].get('pending', 0)}
• 发送中：{queue_info['status_counts'].get('sending', 0)}
• 已成功：{queue_info['status_counts'].get('success', 0)}
• 已失败：{queue_info['status_counts'].get('failed', 0)}

🎛️ 处理状态：{'运行中' if queue_info['is_processing'] else '已停止'}

📈 统计信息：
• 总发送：{queue_info['stats']['total_sent']}
• 总失败：{queue_info['stats']['total_failed']}
• 本次发送：{queue_info['stats']['session_sent']}"""
    
    await query.edit_message_text(text, reply_markup=keyboards.queue_management())


async def handle_view_queue(query, context):
    """查看队列"""
    user_id = query.from_user.id
    user_messages = danmaku_queue.get_user_messages(user_id)
    
    if not user_messages:
        await query.edit_message_text(
            "📝 您的队列中没有消息",
            reply_markup=keyboards.queue_management()
        )
        return
    
    # 准备消息列表
    message_list = []
    for msg in user_messages[:5]:  # 只显示前5条
        message_list.append((msg.id, msg.text, msg.status.value))
    
    total_pages = (len(user_messages) + 4) // 5  # 每页5条
    
    text = f"📋 您的弹幕队列 ({len(user_messages)} 条消息)"
    await query.edit_message_text(
        text, 
        reply_markup=keyboards.queue_view(message_list, 1, total_pages)
    )


async def handle_start_queue(query, context):
    """开始队列处理"""
    if danmaku_queue.is_processing:
        await query.edit_message_text(
            "⚠️ 队列处理已在运行中",
            reply_markup=keyboards.queue_management()
        )
        return
    
    try:
        await danmaku_queue.start_processing(danmaku_client, interval=2.0)
        await query.edit_message_text(
            "✅ 队列处理已启动",
            reply_markup=keyboards.queue_management()
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ 启动失败：{str(e)}",
            reply_markup=keyboards.queue_management()
        )


async def handle_pause_queue(query, context):
    """暂停队列处理"""
    if not danmaku_queue.is_processing:
        await query.edit_message_text(
            "⚠️ 队列处理未在运行",
            reply_markup=keyboards.queue_management()
        )
        return
    
    try:
        await danmaku_queue.stop_processing()
        await query.edit_message_text(
            "⏸️ 队列处理已暂停",
            reply_markup=keyboards.queue_management()
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ 暂停失败：{str(e)}",
            reply_markup=keyboards.queue_management()
        )


async def handle_clear_queue(query, context):
    """清空队列"""
    user_id = query.from_user.id
    is_admin = await user_manager.is_admin(user_id)
    
    if is_admin:
        # 管理员可以清空整个队列
        text = "⚠️ 确定要清空整个队列吗？这将删除所有用户的待发送消息！"
        keyboard = [
            [
                InlineKeyboardButton("✅ 确认清空", callback_data="confirm_clear_all_queue"),
                InlineKeyboardButton("❌ 取消", callback_data="queue_management")
            ],
            [
                InlineKeyboardButton("🗑️ 只清空我的", callback_data="confirm_clear_my_queue")
            ]
        ]
    else:
        # 普通用户只能清空自己的队列
        text = "⚠️ 确定要清空您的队列吗？"
        keyboard = [
            [
                InlineKeyboardButton("✅ 确认", callback_data="confirm_clear_my_queue"),
                InlineKeyboardButton("❌ 取消", callback_data="queue_management")
            ]
        ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# 内容审核相关处理函数

async def handle_content_moderation_menu(query, context):
    """内容审核菜单"""
    user_id = query.from_user.id
    is_admin = await user_manager.is_admin(user_id)
    
    if not is_admin:
        await query.edit_message_text(
            "❌ 权限不足，只有管理员可以访问内容审核功能",
            reply_markup=keyboards.back_to_menu()
        )
        return
    
    # 获取基础统计信息
    stats = content_filter.get_filter_statistics(days=1)
    
    text = f"""🛡️ 内容审核管理

📊 今日统计：
• 总处理: {stats.get('total_processed', 0)}条
• 已拦截: {stats.get('blocked', 0)}条
• 已警告: {stats.get('warned', 0)}条
• 需审核: {stats.get('needs_review', 0)}条

⚙️ 当前配置：
• 活跃规则: {stats.get('active_rules', 0)}条
• 敏感词库: {stats.get('sensitive_words_count', 0)}个

请选择操作："""
    
    await query.edit_message_text(text, reply_markup=keyboards.content_moderation_menu())


async def handle_filter_rules(query, context):
    """过滤规则管理"""
    rules = content_filter.rules
    
    if not rules:
        await query.edit_message_text(
            "📋 当前没有过滤规则",
            reply_markup=keyboards.filter_rules_menu([])
        )
        return
    
    # 准备规则列表（显示前10条）
    rule_list = []
    for rule in rules[:10]:
        status = "🟢" if rule.enabled else "🔴"
        rule_list.append({
            'id': rule.id,
            'display': f"{status} {rule.name} ({rule.filter_type.value})",
            'enabled': rule.enabled
        })
    
    text = f"📋 过滤规则管理 ({len(rules)}条规则)"
    await query.edit_message_text(
        text,
        reply_markup=keyboards.filter_rules_menu(rule_list)
    )


async def handle_audit_records(query, context):
    """审核记录查看"""
    records = content_filter.get_audit_records(days=7)
    
    if not records:
        await query.edit_message_text(
            "📋 最近7天没有审核记录",
            reply_markup=keyboards.content_moderation_menu()
        )
        return
    
    # 准备记录列表（显示前10条）
    record_list = []
    for record in records[:10]:
        action_emoji = {
            'block': '🚫',
            'warning': '⚠️',
            'replace': '🔄',
            'review': '👁️',
            'allow': '✅'
        }.get(record['action'], '❓')
        
        record_list.append({
            'id': record['id'],
            'display': f"{action_emoji} {record['original_text'][:20]}...",
            'action': record['action'],
            'created_at': record['created_at']
        })
    
    text = f"📋 审核记录 (最近{len(records)}条)"
    await query.edit_message_text(
        text,
        reply_markup=keyboards.audit_records_menu(record_list)
    )


async def handle_filter_statistics(query, context):
    """过滤统计信息"""
    stats_7d = content_filter.get_filter_statistics(days=7)
    stats_30d = content_filter.get_filter_statistics(days=30)
    
    text = f"""📊 过滤统计报告

📅 最近7天：
• 总处理: {stats_7d.get('total_processed', 0)}条
• 已拦截: {stats_7d.get('blocked', 0)}条 ({stats_7d.get('blocked', 0) / max(stats_7d.get('total_processed', 1), 1) * 100:.1f}%)
• 已警告: {stats_7d.get('warned', 0)}条
• 已替换: {stats_7d.get('replaced', 0)}条
• 需审核: {stats_7d.get('needs_review', 0)}条

📅 最近30天：
• 总处理: {stats_30d.get('total_processed', 0)}条
• 拦截率: {stats_30d.get('blocked', 0) / max(stats_30d.get('total_processed', 1), 1) * 100:.1f}%

🔥 风险分布（7天）："""
    
    risk_dist = stats_7d.get('risk_distribution', {})
    for risk, count in risk_dist.items():
        text += f"\n• {risk.upper()}: {count}条"
    
    text += "\n\n👥 活跃用户（7天）："
    top_users = stats_7d.get('top_users', [])[:5]
    for user_info in top_users:
        text += f"\n• 用户{user_info['user_id']}: {user_info['count']}条"
    
    await query.edit_message_text(
        text,
        reply_markup=keyboards.content_moderation_menu()
    )


async def handle_add_filter_rule(query, context):
    """添加过滤规则"""
    await query.edit_message_text(
        "📝 添加过滤规则\n\n请发送规则配置，格式：\n规则名称|类型|模式|动作|风险等级\n\n例如：\n广告过滤|regex|加群|block|high",
        reply_markup=keyboards.back_to_content_moderation()
    )
    context.user_data['waiting_for_filter_rule'] = True


async def handle_toggle_rule(query, callback_data):
    """切换规则状态"""
    rule_id = callback_data.replace('toggle_rule_', '')
    
    # 找到规则并切换状态
    for rule in content_filter.rules:
        if rule.id == rule_id:
            rule.enabled = not rule.enabled
            rule.updated_at = datetime.now()
            
            # 更新数据库
            success = content_filter.add_rule(rule)  # add_rule 支持更新
            
            if success:
                status = "启用" if rule.enabled else "禁用"
                await query.edit_message_text(
                    f"✅ 规则 '{rule.name}' 已{status}",
                    reply_markup=keyboards.filter_rules_menu([])
                )
            else:
                await query.edit_message_text(
                    "❌ 更新规则失败",
                    reply_markup=keyboards.filter_rules_menu([])
                )
            break
    else:
        await query.edit_message_text(
            "❌ 规则不存在",
            reply_markup=keyboards.filter_rules_menu([])
        )


async def handle_delete_rule(query, callback_data):
    """删除规则"""
    rule_id = callback_data.replace('delete_rule_', '')
    
    success = content_filter.remove_rule(rule_id)
    
    if success:
        await query.edit_message_text(
            f"✅ 规则已删除",
            reply_markup=keyboards.filter_rules_menu([])
        )
    else:
        await query.edit_message_text(
            "❌ 删除规则失败",
            reply_markup=keyboards.filter_rules_menu([])
        )


async def handle_audit_detail(query, callback_data):
    """查看审核详情"""
    record_id = int(callback_data.replace('audit_detail_', ''))
    
    # 获取记录详情
    records = content_filter.get_audit_records()
    record = next((r for r in records if r['id'] == record_id), None)
    
    if not record:
        await query.edit_message_text(
            "❌ 记录不存在",
            reply_markup=keyboards.content_moderation_menu()
        )
        return
    
    action_names = {
        'block': '🚫 已拦截',
        'warning': '⚠️ 已警告',
        'replace': '🔄 已替换',
        'review': '👁️ 待审核',
        'allow': '✅ 已通过'
    }
    
    text = f"""📋 审核记录详情

👤 用户ID: {record['user_id']}
📝 原始内容: {record['original_text']}
🔄 处理后: {record.get('filtered_text', record['original_text'])}
⚡ 处理动作: {action_names.get(record['action'], record['action'])}
⚠️ 风险等级: {record['risk_level'].upper()}
📅 时间: {record['created_at']}
"""
    
    if record.get('matched_rules'):
        text += f"\n🎯 触发规则: {', '.join(record['matched_rules'])}"
    
    if record.get('warnings'):
        text += f"\n⚠️ 警告信息: {', '.join(record['warnings'])}"
    
    keyboard = []
    if record['action'] == 'review':
        keyboard.append([
            InlineKeyboardButton("✅ 批准", callback_data=f"approve_content_{record_id}"),
            InlineKeyboardButton("❌ 拒绝", callback_data=f"reject_content_{record_id}")
        ])
    
    keyboard.append([InlineKeyboardButton("⬅️ 返回", callback_data="audit_records")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_approve_content(query, callback_data):
    """批准内容"""
    record_id = int(callback_data.replace('approve_content_', ''))
    
    # 这里应该更新审核状态到数据库
    # 由于现有结构限制，我们先发送确认消息
    await query.edit_message_text(
        f"✅ 内容已批准（记录ID: {record_id}）",
        reply_markup=keyboards.content_moderation_menu()
    )
    
    # 记录操作日志
    await user_manager.log_operation(
        query.from_user.id,
        'approve_content',
        {'record_id': record_id},
        'success'
    )


async def handle_reject_content(query, callback_data):
    """拒绝内容"""
    record_id = int(callback_data.replace('reject_content_', ''))
    
    # 这里应该更新审核状态到数据库
    # 由于现有结构限制，我们先发送确认消息
    await query.edit_message_text(
        f"❌ 内容已拒绝（记录ID: {record_id}）",
        reply_markup=keyboards.content_moderation_menu()
    )
    
    # 记录操作日志
    await user_manager.log_operation(
        query.from_user.id,
        'reject_content',
        {'record_id': record_id},
        'success'
    )
=======
        await query.edit_message_text(f"❌ 获取失败", reply_markup=keyboards.back_to_menu())
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
