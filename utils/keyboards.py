from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Tuple, Optional


class KeyboardBuilder:
    """键盘布局构建器"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """主菜单键盘"""
        keyboard = [
            [
                InlineKeyboardButton("📊 服务器状态", callback_data="status"),
                InlineKeyboardButton("🎬 电影搜索", callback_data="movie_search")
            ],
            [
                InlineKeyboardButton("🎯 弹幕管理", callback_data="danmaku_control"),
                InlineKeyboardButton("⚙️ 设置", callback_data="settings")
            ],
            [
                InlineKeyboardButton("📋 操作日志", callback_data="logs"),
                InlineKeyboardButton("❓ 帮助", callback_data="help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def server_status() -> InlineKeyboardMarkup:
        """服务器状态键盘"""
        keyboard = [
            [
                InlineKeyboardButton("🔄 刷新", callback_data="refresh_status"),
                InlineKeyboardButton("📈 详细信息", callback_data="detailed_status")
            ],
            [
                InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def danmaku_control() -> InlineKeyboardMarkup:
        """弹幕控制键盘"""
        keyboard = [
            [
                InlineKeyboardButton("⏸️ 暂停弹幕", callback_data="pause_danmaku"),
                InlineKeyboardButton("▶️ 恢复弹幕", callback_data="resume_danmaku")
            ],
            [
                InlineKeyboardButton("🚫 清空弹幕", callback_data="clear_danmaku"),
                InlineKeyboardButton("💬 发送弹幕", callback_data="send_danmaku")
            ],
            [
                InlineKeyboardButton("⚙️ 显示设置", callback_data="display_settings"),
                InlineKeyboardButton("🎨 样式设置", callback_data="style_settings")
            ],
            [
                InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def display_settings() -> InlineKeyboardMarkup:
        """显示设置键盘"""
        keyboard = [
            [
                InlineKeyboardButton("🐌 慢速", callback_data="speed_slow"),
                InlineKeyboardButton("🚗 普通", callback_data="speed_normal"),
                InlineKeyboardButton("🚀 快速", callback_data="speed_fast")
            ],
            [
                InlineKeyboardButton("💫 透明度", callback_data="opacity_settings")
            ],
            [
                InlineKeyboardButton("↩️ 返回弹幕控制", callback_data="danmaku_control"),
                InlineKeyboardButton("🏠 主菜单", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def opacity_settings() -> InlineKeyboardMarkup:
        """透明度设置键盘"""
        keyboard = [
            [
                InlineKeyboardButton("20%", callback_data="opacity_0.2"),
                InlineKeyboardButton("40%", callback_data="opacity_0.4"),
                InlineKeyboardButton("60%", callback_data="opacity_0.6")
            ],
            [
                InlineKeyboardButton("80%", callback_data="opacity_0.8"),
                InlineKeyboardButton("100%", callback_data="opacity_1.0")
            ],
            [
                InlineKeyboardButton("↩️ 返回显示设置", callback_data="display_settings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def movie_search_results(movies: List, page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
        """电影搜索结果键盘"""
        keyboard = []
        
        # 电影结果按钮（每行一个）
        for movie in movies[:5]:  # 只显示前5个结果
            title = movie.get('title', 'Unknown')
            year = movie.get('release_date', '')[:4] if movie.get('release_date') else ''
            display_text = f"🎬 {title}"
            if year:
                display_text += f" ({year})"
            
            keyboard.append([
                InlineKeyboardButton(
                    display_text[:50] + "..." if len(display_text) > 50 else display_text,
                    callback_data=f"movie_detail_{movie.get('id')}"
                )
            ])
        
        # 分页按钮
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"movie_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️ 下一页", callback_data=f"movie_page_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # 返回按钮
        keyboard.append([
            InlineKeyboardButton("🔍 新搜索", callback_data="movie_search"),
            InlineKeyboardButton("🏠 主菜单", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def movie_detail(movie_id: int) -> InlineKeyboardMarkup:
        """电影详情键盘"""
        keyboard = [
            [
                InlineKeyboardButton("💬 发送弹幕", callback_data=f"send_movie_danmaku_{movie_id}"),
                InlineKeyboardButton("👥 演职员表", callback_data=f"movie_credits_{movie_id}")
            ],
            [
                InlineKeyboardButton("🔍 搜索其他", callback_data="movie_search"),
                InlineKeyboardButton("🏠 主菜单", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_panel() -> InlineKeyboardMarkup:
        """管理员面板键盘"""
        keyboard = [
            [
                InlineKeyboardButton("👥 用户管理", callback_data="admin_users"),
                InlineKeyboardButton("📊 统计信息", callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton("📋 系统日志", callback_data="admin_logs"),
                InlineKeyboardButton("⚙️ 系统设置", callback_data="admin_settings")
            ],
            [
                InlineKeyboardButton("🚨 紧急停止", callback_data="emergency_stop"),
                InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def user_management() -> InlineKeyboardMarkup:
        """用户管理键盘"""
        keyboard = [
            [
                InlineKeyboardButton("👥 用户列表", callback_data="admin_user_list"),
                InlineKeyboardButton("🔍 搜索用户", callback_data="admin_search_user")
            ],
            [
                InlineKeyboardButton("🚫 禁用用户", callback_data="admin_ban_user"),
                InlineKeyboardButton("✅ 启用用户", callback_data="admin_unban_user")
            ],
            [
                InlineKeyboardButton("↩️ 返回管理面板", callback_data="admin_panel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirmation(action: str, target: str = "") -> InlineKeyboardMarkup:
        """确认操作键盘"""
        keyboard = [
            [
                InlineKeyboardButton("✅ 确认", callback_data=f"confirm_{action}_{target}"),
                InlineKeyboardButton("❌ 取消", callback_data="cancel_action")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def pagination(
        current_page: int, 
        total_pages: int, 
        callback_prefix: str
    ) -> InlineKeyboardMarkup:
        """分页键盘"""
        keyboard = []
        nav_buttons = []
        
        # 上一页按钮
        if current_page > 1:
            nav_buttons.append(
                InlineKeyboardButton("⬅️ 上一页", callback_data=f"{callback_prefix}_{current_page-1}")
            )
        
        # 页码信息
        nav_buttons.append(
            InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop")
        )
        
        # 下一页按钮
        if current_page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton("➡️ 下一页", callback_data=f"{callback_prefix}_{current_page+1}")
            )
        
        keyboard.append(nav_buttons)
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """返回主菜单键盘"""
        keyboard = [
            [InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def logs_menu() -> InlineKeyboardMarkup:
        """日志菜单键盘"""
        keyboard = [
            [
                InlineKeyboardButton("📋 我的操作", callback_data="logs_my"),
                InlineKeyboardButton("📊 全部操作", callback_data="logs_all")
            ],
            [
                InlineKeyboardButton("🔄 刷新", callback_data="logs_refresh"),
                InlineKeyboardButton("🏠 主菜单", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)


# 创建全局键盘构建器实例
keyboards = KeyboardBuilder()