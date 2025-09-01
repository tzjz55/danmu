from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Tuple, Optional


class KeyboardBuilder:
    """优化的键盘布局构建器"""
    
    # 常用图标常量
    ICONS = {
        'home': '🏠',
        'back': '⬅️',
        'refresh': '🔄',
        'settings': '⚙️',
        'send': '📤',
        'pause': '⏸️',
        'play': '▶️',
        'stop': '⏹️',
        'clear': '🚫',
        'template': '📜',
        'custom': '🎨',
        'queue': '📋',
        'stats': '📈',
        'help': '❓'
    }
    
    @staticmethod
    def _create_navigation_row(back_callback: str, home_callback: str = "main_menu") -> List[InlineKeyboardButton]:
        """创建导航行"""
        return [
            InlineKeyboardButton(f"{KeyboardBuilder.ICONS['back']} 返回", callback_data=back_callback),
            InlineKeyboardButton(f"{KeyboardBuilder.ICONS['home']} 主菜单", callback_data=home_callback)
        ]
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """主菜单键盘（优化版）"""
        keyboard = [
            [
                InlineKeyboardButton("📈 状态监控", callback_data="status"),
                InlineKeyboardButton("🎨 弹幕发送", callback_data="danmaku_style_menu")
            ],
            [
                InlineKeyboardButton("📋 队列管理", callback_data="queue_management"),
                InlineKeyboardButton("📊 数据统计", callback_data="statistics_menu")
            ],
            [
                InlineKeyboardButton("🛡️ 内容审核", callback_data="content_moderation"),
                InlineKeyboardButton("⚙️ 系统设置", callback_data="system_settings")
            ],
            [
                InlineKeyboardButton("🎬 电影搜索", callback_data="movie_search"),
                InlineKeyboardButton("❓ 帮助指南", callback_data="help_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def server_status() -> InlineKeyboardMarkup:
        """服务器状态键盘（简化版）"""
        keyboard = [
            [
                InlineKeyboardButton("🔄 刷新状态", callback_data="refresh_status"),
                InlineKeyboardButton("📊 详细信息", callback_data="detailed_status")
            ],
            [
                InlineKeyboardButton("⚙️ 系统控制", callback_data="system_control"),
                InlineKeyboardButton("📈 性能监控", callback_data="performance_monitor")
            ]
        ]
        keyboard.append(KeyboardBuilder._create_navigation_row("main_menu"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def danmaku_quick_menu() -> InlineKeyboardMarkup:
        """弹幕快捷菜单（新增）"""
        keyboard = [
            [
                InlineKeyboardButton("⚡ 快速发送", callback_data="quick_send_danmaku"),
                InlineKeyboardButton("📜 选择模板", callback_data="template_danmaku")
            ],
            [
                InlineKeyboardButton("⏸️ 暂停", callback_data="pause_danmaku"),
                InlineKeyboardButton("▶️ 恢复", callback_data="resume_danmaku"),
                InlineKeyboardButton("🚫 清空", callback_data="clear_danmaku")
            ],
            [
                InlineKeyboardButton("🎨 高级设置", callback_data="danmaku_advanced"),
                InlineKeyboardButton("📦 批量操作", callback_data="bulk_send_danmaku")
            ]
        ]
        keyboard.append(KeyboardBuilder._create_navigation_row("main_menu"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def danmaku_advanced() -> InlineKeyboardMarkup:
        """弹幕高级设置键盘"""
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
                InlineKeyboardButton("↩️ 返回弹幕快捷", callback_data="danmaku_quick_menu"),
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
    def statistics_menu() -> InlineKeyboardMarkup:
        """统计菜单（新增）"""
        keyboard = [
            [
                InlineKeyboardButton("👤 个人统计", callback_data="user_stats"),
                InlineKeyboardButton("🌍 全局统计", callback_data="system_stats")
            ],
            [
                InlineKeyboardButton("🏆 用户排行", callback_data="user_ranking"),
                InlineKeyboardButton("📈 趋势分析", callback_data="trend_analysis")
            ],
            [
                InlineKeyboardButton("📄 导出报告", callback_data="export_stats"),
                InlineKeyboardButton("🔄 重置统计", callback_data="reset_stats")
            ]
        ]
        keyboard.append(KeyboardBuilder._create_navigation_row("main_menu"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def system_settings() -> InlineKeyboardMarkup:
        """系统设置菜单（新增）"""
        keyboard = [
            [
                InlineKeyboardButton("⚙️ 弹幕设置", callback_data="danmaku_settings"),
                InlineKeyboardButton("🔧 API设置", callback_data="api_settings")
            ],
            [
                InlineKeyboardButton("👥 用户管理", callback_data="user_management"),
                InlineKeyboardButton("📋 日志管理", callback_data="log_management")
            ],
            [
                InlineKeyboardButton("🛡️ 安全设置", callback_data="security_settings"),
                InlineKeyboardButton("📊 监控设置", callback_data="monitor_settings")
            ]
        ]
        keyboard.append(KeyboardBuilder._create_navigation_row("main_menu"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """帮助菜单（新增）"""
        keyboard = [
            [
                InlineKeyboardButton("📖 使用教程", callback_data="tutorial"),
                InlineKeyboardButton("❓ 常见问题", callback_data="faq")
            ],
            [
                InlineKeyboardButton("🎯 功能介绍", callback_data="features"),
                InlineKeyboardButton("🔧 故障排除", callback_data="troubleshooting")
            ],
            [
                InlineKeyboardButton("📞 联系支持", callback_data="contact_support"),
                InlineKeyboardButton("📋 更新日志", callback_data="changelog")
            ]
        ]
        keyboard.append(KeyboardBuilder._create_navigation_row("main_menu"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def danmaku_style_menu() -> InlineKeyboardMarkup:
        """弹幕样式菜单（优化版）"""
        keyboard = [
            [
                InlineKeyboardButton("⚡ 快速发送", callback_data="quick_send_danmaku"),
                InlineKeyboardButton("📜 选择模板", callback_data="compact_template_selection")
            ],
            [
                InlineKeyboardButton("🎨 自定义样式", callback_data="custom_style_danmaku"),
                InlineKeyboardButton("📦 批量操作", callback_data="bulk_send_danmaku")
            ],
            [
                InlineKeyboardButton("⏸️ 暂停", callback_data="pause_danmaku"),
                InlineKeyboardButton("▶️ 恢复", callback_data="resume_danmaku"),
                InlineKeyboardButton("🚫 清空", callback_data="clear_danmaku")
            ],
            [
                InlineKeyboardButton("⚙️ 显示设置", callback_data="display_settings")
            ]
        ]
        keyboard.append(KeyboardBuilder._create_navigation_row("main_menu"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def danmaku_color_selection() -> InlineKeyboardMarkup:
        """弹幕颜色选择"""
        keyboard = [
            [
                InlineKeyboardButton("⬜ 白色", callback_data="color_#FFFFFF"),
                InlineKeyboardButton("🔴 红色", callback_data="color_#FF0000"),
                InlineKeyboardButton("🟡 黄色", callback_data="color_#FFD700")
            ],
            [
                InlineKeyboardButton("🟢 绿色", callback_data="color_#00FF00"),
                InlineKeyboardButton("🔵 蓝色", callback_data="color_#0080FF"),
                InlineKeyboardButton("🟣 紫色", callback_data="color_#9370DB")
            ],
            [
                InlineKeyboardButton("🟠 橙色", callback_data="color_#FF8C00"),
                InlineKeyboardButton("🤍 粉色", callback_data="color_#FF69B4"),
                InlineKeyboardButton("🟦 青色", callback_data="color_#00CED1")
            ],
            [
                InlineKeyboardButton("⬅️ 返回", callback_data="custom_style_danmaku")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def danmaku_position_selection() -> InlineKeyboardMarkup:
        """弹幕位置选择"""
        keyboard = [
            [
                InlineKeyboardButton("🔼 滚动", callback_data="position_scroll"),
                InlineKeyboardButton("⬆️ 顶部", callback_data="position_top")
            ],
            [
                InlineKeyboardButton("⬇️ 底部", callback_data="position_bottom"),
                InlineKeyboardButton("🎯 中间", callback_data="position_center")
            ],
            [
                InlineKeyboardButton("⬅️ 返回", callback_data="custom_style_danmaku")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def danmaku_font_size_selection() -> InlineKeyboardMarkup:
        """弹幕字体大小选择"""
        keyboard = [
            [
                InlineKeyboardButton("🔢 小字体 (18)", callback_data="fontsize_18"),
                InlineKeyboardButton("🔣 普通 (24)", callback_data="fontsize_24")
            ],
            [
                InlineKeyboardButton("🔤 大字体 (30)", callback_data="fontsize_30"),
                InlineKeyboardButton("🔥 特大 (36)", callback_data="fontsize_36")
            ],
            [
                InlineKeyboardButton("⬅️ 返回", callback_data="custom_style_danmaku")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def danmaku_template_categories() -> InlineKeyboardMarkup:
        """弹幕模板分类"""
        keyboard = [
            [
                InlineKeyboardButton("👋 问候", callback_data="template_category_greeting"),
                InlineKeyboardButton("🙏 感谢", callback_data="template_category_thanks")
            ],
            [
                InlineKeyboardButton("😍 反应", callback_data="template_category_reaction"),
                InlineKeyboardButton("⚠️ 警告", callback_data="template_category_warning")
            ],
            [
                InlineKeyboardButton("🎉 活动", callback_data="template_category_event"),
                InlineKeyboardButton("👥 互动", callback_data="template_category_interaction")
            ],
            [
                InlineKeyboardButton("🛠️ 自定义", callback_data="template_category_custom"),
                InlineKeyboardButton("📎 所有模板", callback_data="template_category_all")
            ],
            [
                InlineKeyboardButton("⬅️ 返回", callback_data="danmaku_style_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def danmaku_templates_list(templates: List[Tuple[str, str]], page: int = 1, total_pages: int = 1, category: str = "all") -> InlineKeyboardMarkup:
        """弹幕模板列表"""
        keyboard = []
        
        # 模板按钮（每行两个）
        for i in range(0, len(templates), 2):
            row = []
            for j in range(2):
                if i + j < len(templates):
                    name, text = templates[i + j]
                    display_text = name if len(name) <= 10 else name[:8] + "..."
                    row.append(InlineKeyboardButton(
                        display_text, 
                        callback_data=f"use_template_{name}"
                    ))
            keyboard.append(row)
        
        # 分页按钮
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"template_page_{category}_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️ 下一页", callback_data=f"template_page_{category}_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # 管理按钮
        keyboard.append([
            InlineKeyboardButton("➕ 添加模板", callback_data="add_template"),
            InlineKeyboardButton("🗑️ 管理模板", callback_data="manage_templates")
        ])
        
        # 返回按钮
        keyboard.append([
            InlineKeyboardButton("⬅️ 返回分类", callback_data="template_danmaku")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def danmaku_preset_styles() -> InlineKeyboardMarkup:
        """弹幕预设样式"""
        keyboard = [
            [
                InlineKeyboardButton("🌟 正常", callback_data="preset_normal"),
                InlineKeyboardButton("✨ 高亮", callback_data="preset_highlight")
            ],
            [
                InlineKeyboardButton("⚠️ 警告", callback_data="preset_warning"),
                InlineKeyboardButton("✅ 成功", callback_data="preset_success")
            ],
            [
                InlineKeyboardButton("❌ 错误", callback_data="preset_error"),
                InlineKeyboardButton("🎉 庆祝", callback_data="preset_celebration")
            ],
            [
                InlineKeyboardButton("⬅️ 返回", callback_data="danmaku_style_menu")
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
    def bulk_send_menu() -> InlineKeyboardMarkup:
        """批量发送菜单"""
        keyboard = [
            [
                InlineKeyboardButton("📄 文本列表", callback_data="bulk_text_list"),
                InlineKeyboardButton("📜 模板批量", callback_data="bulk_template_list")
            ],
            [
                InlineKeyboardButton("🕰️ 定时发送", callback_data="scheduled_send"),
                InlineKeyboardButton("🔁 循环发送", callback_data="loop_send")
            ],
            [
                InlineKeyboardButton("📋 队列管理", callback_data="queue_management"),
                InlineKeyboardButton("📈 发送统计", callback_data="send_statistics")
            ],
            [
                InlineKeyboardButton("⬅️ 返回", callback_data="danmaku_style_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def queue_management() -> InlineKeyboardMarkup:
        """队列管理菜单"""
        keyboard = [
            [
                InlineKeyboardButton("📄 查看队列", callback_data="view_queue"),
                InlineKeyboardButton("▶️ 开始处理", callback_data="start_queue")
            ],
            [
                InlineKeyboardButton("⏸️ 暂停处理", callback_data="pause_queue"),
                InlineKeyboardButton("🚫 清空队列", callback_data="clear_queue")
            ],
            [
                InlineKeyboardButton("📈 队列统计", callback_data="queue_stats"),
                InlineKeyboardButton("⚙️ 队列设置", callback_data="queue_settings")
            ],
            [
                InlineKeyboardButton("⬅️ 返回", callback_data="bulk_send_danmaku")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def queue_view(messages: List[Tuple[str, str, str]], page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
        """队列查看键盘"""
        keyboard = []
        
        # 消息列表（每页显示5条）
        for i, (msg_id, text, status) in enumerate(messages[:5]):
            status_emoji = {
                'pending': '⏳',
                'sending': '📤', 
                'success': '✅',
                'failed': '❌',
                'cancelled': '🚫'
            }.get(status, '❓')
            
            display_text = f"{status_emoji} {text[:25]}..."
            keyboard.append([
                InlineKeyboardButton(display_text, callback_data=f"queue_detail_{msg_id}")
            ])
        
        # 分页按钮
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"queue_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️ 下一页", callback_data=f"queue_page_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # 操作按钮
        keyboard.append([
            InlineKeyboardButton("🔄 刷新", callback_data="view_queue"),
            InlineKeyboardButton("🗑️ 清理已完成", callback_data="clear_completed")
        ])
        
        # 返回按钮
        keyboard.append([
            InlineKeyboardButton("⬅️ 返回管理", callback_data="queue_management")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def priority_selection() -> InlineKeyboardMarkup:
        """优先级选择键盘"""
        keyboard = [
            [
                InlineKeyboardButton("🔥 紧急 (5)", callback_data="priority_5"),
                InlineKeyboardButton("⬆️ 高 (4)", callback_data="priority_4")
            ],
            [
                InlineKeyboardButton("➡️ 普通 (3)", callback_data="priority_3"),
                InlineKeyboardButton("⬇️ 低 (2)", callback_data="priority_2")
            ],
            [
                InlineKeyboardButton("🐌 最低 (1)", callback_data="priority_1")
            ],
            [
                InlineKeyboardButton("⬅️ 返回", callback_data="bulk_send_danmaku")
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
            [
                InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def content_moderation() -> InlineKeyboardMarkup:
        """内容审核菜单（新增）"""
        keyboard = [
            [
                InlineKeyboardButton("📋 待审核列表", callback_data="pending_reviews"),
                InlineKeyboardButton("🔍 审核搜索", callback_data="search_reviews")
            ],
            [
                InlineKeyboardButton("📊 审核统计", callback_data="moderation_stats"),
                InlineKeyboardButton("⚠️ 风险报告", callback_data="risk_report")
            ],
            [
                InlineKeyboardButton("👤 用户风险", callback_data="user_risks"),
                InlineKeyboardButton("📈 趋势分析", callback_data="moderation_trends")
            ],
            [
                InlineKeyboardButton("🔧 审核设置", callback_data="moderation_settings")
            ]
        ]
        keyboard.append(KeyboardBuilder._create_navigation_row("system_settings"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def filter_settings() -> InlineKeyboardMarkup:
        """过滤设置菜单（新增）"""
        keyboard = [
            [
                InlineKeyboardButton("📝 过滤规则", callback_data="filter_rules"),
                InlineKeyboardButton("🚫 敏感词管理", callback_data="sensitive_words")
            ],
            [
                InlineKeyboardButton("⚙️ 过滤配置", callback_data="filter_config"),
                InlineKeyboardButton("📊 过滤统计", callback_data="filter_stats")
            ],
            [
                InlineKeyboardButton("🧪 规则测试", callback_data="test_filters"),
                InlineKeyboardButton("📤 导入导出", callback_data="import_export_filters")
            ],
            [
                InlineKeyboardButton("🔄 重置过滤器", callback_data="reset_filters")
            ]
        ]
        keyboard.append(KeyboardBuilder._create_navigation_row("system_settings"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def filter_rules_list(rules: List[Tuple[str, str, str, bool]], page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
        """过滤规则列表（新增）"""
        keyboard = []
        
        # 规则列表（每页显示5条）
        for rule_id, name, filter_type, enabled in rules[:5]:
            status_emoji = "✅" if enabled else "❌"
            type_emoji = {
                "keyword": "🔤",
                "regex": "🔧", 
                "length": "📏",
                "rate_limit": "⏱️"
            }.get(filter_type, "⚙️")
            
            display_text = f"{status_emoji} {type_emoji} {name}"
            keyboard.append([
                InlineKeyboardButton(display_text[:35], callback_data=f"edit_rule_{rule_id}")
            ])
        
        # 分页和操作按钮
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"rules_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️ 下一页", callback_data=f"rules_page_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # 管理按钮
        keyboard.append([
            InlineKeyboardButton("➕ 添加规则", callback_data="add_filter_rule"),
            InlineKeyboardButton("🗑️ 批量删除", callback_data="bulk_delete_rules")
        ])
        
        keyboard.append(KeyboardBuilder._create_navigation_row("filter_settings"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def review_item_actions(record_id: int) -> InlineKeyboardMarkup:
        """审核项目操作（新增）"""
        keyboard = [
            [
                InlineKeyboardButton("✅ 批准", callback_data=f"approve_{record_id}"),
                InlineKeyboardButton("❌ 拒绝", callback_data=f"reject_{record_id}")
            ],
            [
                InlineKeyboardButton("⚠️ 警告用户", callback_data=f"warn_user_{record_id}"),
                InlineKeyboardButton("🚫 封禁用户", callback_data=f"ban_user_{record_id}")
            ],
            [
                InlineKeyboardButton("📝 添加备注", callback_data=f"add_note_{record_id}"),
                InlineKeyboardButton("🔍 查看详情", callback_data=f"view_detail_{record_id}")
            ]
        ]
        keyboard.append(KeyboardBuilder._create_navigation_row("content_moderation"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def filter_action_selection() -> InlineKeyboardMarkup:
        """过滤动作选择（新增）"""
        keyboard = [
            [
                InlineKeyboardButton("✅ 允许", callback_data="action_allow"),
                InlineKeyboardButton("🚫 阻止", callback_data="action_block")
            ],
            [
                InlineKeyboardButton("⚠️ 警告", callback_data="action_warning"),
                InlineKeyboardButton("🔄 替换", callback_data="action_replace")
            ],
            [
                InlineKeyboardButton("👁️ 人工审核", callback_data="action_review"),
                InlineKeyboardButton("📦 隔离", callback_data="action_quarantine")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def risk_level_selection() -> InlineKeyboardMarkup:
        """风险等级选择（新增）"""
        keyboard = [
            [
                InlineKeyboardButton("🟢 低风险", callback_data="risk_low"),
                InlineKeyboardButton("🟡 中风险", callback_data="risk_medium")
            ],
            [
                InlineKeyboardButton("🟠 高风险", callback_data="risk_high"),
                InlineKeyboardButton("🔴 严重风险", callback_data="risk_critical")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def content_moderation_menu() -> InlineKeyboardMarkup:
        """内容审核主菜单"""
        keyboard = [
            [
                InlineKeyboardButton("📋 过滤规则", callback_data="filter_rules"),
                InlineKeyboardButton("📊 审核统计", callback_data="filter_statistics")
            ],
            [
                InlineKeyboardButton("📝 审核记录", callback_data="audit_records"),
                InlineKeyboardButton("⚙️ 系统设置", callback_data="filter_settings")
            ],
            [
                InlineKeyboardButton("➕ 添加规则", callback_data="add_filter_rule"),
                InlineKeyboardButton("📚 敏感词库", callback_data="sensitive_words")
            ]
        ]
        keyboard.append(KeyboardBuilder._create_navigation_row("main_menu"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def filter_rules_menu(rules: List) -> InlineKeyboardMarkup:
        """过滤规则管理菜单"""
        keyboard = []
        
        # 规则列表（显示前8条）
        for rule in rules[:8]:
            status_icon = "🟢" if rule.get('enabled', True) else "🔴"
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_icon} {rule['display'][:40]}...",
                    callback_data=f"rule_detail_{rule['id']}"
                ),
                InlineKeyboardButton(
                    "🔄",
                    callback_data=f"toggle_rule_{rule['id']}"
                ),
                InlineKeyboardButton(
                    "🗑️",
                    callback_data=f"delete_rule_{rule['id']}"
                )
            ])
        
        # 操作按钮
        keyboard.extend([
            [
                InlineKeyboardButton("➕ 新增规则", callback_data="add_filter_rule"),
                InlineKeyboardButton("📥 导入规则", callback_data="import_rules")
            ],
            [
                InlineKeyboardButton("🔄 刷新列表", callback_data="filter_rules"),
                InlineKeyboardButton("📤 导出规则", callback_data="export_rules")
            ]
        ])
        
        keyboard.append(KeyboardBuilder._create_navigation_row("content_moderation"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def audit_records_menu(records: List) -> InlineKeyboardMarkup:
        """审核记录菜单"""
        keyboard = []
        
        # 记录列表（显示前6条）
        for record in records[:6]:
            action_icon = {
                'block': '🚫',
                'warning': '⚠️',
                'replace': '🔄',
                'review': '👁️',
                'allow': '✅'
            }.get(record.get('action', ''), '❓')
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{action_icon} {record['display'][:35]}...",
                    callback_data=f"audit_detail_{record['id']}"
                )
            ])
        
        # 操作按钮
        keyboard.extend([
            [
                InlineKeyboardButton("🔍 按用户查询", callback_data="audit_by_user"),
                InlineKeyboardButton("📅 按时间查询", callback_data="audit_by_date")
            ],
            [
                InlineKeyboardButton("🔄 刷新记录", callback_data="audit_records"),
                InlineKeyboardButton("📤 导出记录", callback_data="export_audit")
            ]
        ])
        
        keyboard.append(KeyboardBuilder._create_navigation_row("content_moderation"))
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_content_moderation() -> InlineKeyboardMarkup:
        """返回内容审核菜单"""
        keyboard = [
            [
                InlineKeyboardButton("⬅️ 返回审核菜单", callback_data="content_moderation"),
                InlineKeyboardButton("🏠 主菜单", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

# 创建键盘实例
keyboards = KeyboardBuilder()