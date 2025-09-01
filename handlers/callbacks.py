from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from managers.user_manager import user_manager
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
        elif callback_data.startswith("send_danmaku"):
            await handle_send_danmaku_prompt(query, context)
        
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
        await query.edit_message_text(f"❌ 获取失败", reply_markup=keyboards.back_to_menu())