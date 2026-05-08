"""
Admin panel keyboard layouts.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Create main admin menu keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    # Main admin functions
    builder.row(
        InlineKeyboardButton(text="📊 Statistics", callback_data="admin_stats"),
        InlineKeyboardButton(text="👥 Users", callback_data="admin_users")
    )
    
    builder.row(
        InlineKeyboardButton(text="📚 Content", callback_data="admin_content"),
        InlineKeyboardButton(text="🎮 Games", callback_data="admin_games")
    )
    
    builder.row(
        InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
        InlineKeyboardButton(text="⚙️ Settings", callback_data="admin_settings")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back to User", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_admin_actions_keyboard() -> InlineKeyboardMarkup:
    """Create admin actions keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📤 Send Message", callback_data="admin_send_message"),
        InlineKeyboardButton(text="📊 View Analytics", callback_data="admin_analytics")
    )
    
    builder.row(
        InlineKeyboardButton(text="👤 Manage Users", callback_data="admin_manage_users"),
        InlineKeyboardButton(text="🎁 Manage Rewards", callback_data="admin_manage_rewards")
    )
    
    builder.row(
        InlineKeyboardButton(text="🗄️ Database", callback_data="admin_database"),
        InlineKeyboardButton(text="🔧 System", callback_data="admin_system")
    )
    
    return builder.as_markup()


def get_admin_stats_keyboard() -> InlineKeyboardMarkup:
    """Create admin statistics keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 Overview", callback_data="admin_stats_overview"),
        InlineKeyboardButton(text="👥 Users", callback_data="admin_stats_users")
    )
    
    builder.row(
        InlineKeyboardButton(text="🎮 Games", callback_data="admin_stats_games"),
        InlineKeyboardButton(text="📈 Activity", callback_data="admin_stats_activity")
    )
    
    builder.row(
        InlineKeyboardButton(text="💰 Economy", callback_data="admin_stats_economy"),
        InlineKeyboardButton(text="📤 Export", callback_data="admin_stats_export")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="admin_menu")
    )
    
    return builder.as_markup()


def get_admin_users_keyboard() -> InlineKeyboardMarkup:
    """Create admin user management keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔍 Search User", callback_data="admin_search_user"),
        InlineKeyboardButton(text="📋 User List", callback_data="admin_user_list")
    )
    
    builder.row(
        InlineKeyboardButton(text="🚫 Banned Users", callback_data="admin_banned_users"),
        InlineKeyboardButton(text="👑 Admin Users", callback_data="admin_admin_users")
    )
    
    builder.row(
        InlineKeyboardButton(text="💎 Premium Users", callback_data="admin_premium_users"),
        InlineKeyboardButton(text="📊 Top Users", callback_data="admin_top_users")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="admin_menu")
    )
    
    return builder.as_markup()


def get_admin_content_keyboard() -> InlineKeyboardMarkup:
    """Create admin content management keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📝 Questions", callback_data="admin_questions"),
        InlineKeyboardButton(text="📚 Categories", callback_data="admin_categories")
    )
    
    builder.row(
        InlineKeyboardButton(text="🏆 Achievements", callback_data="admin_achievements"),
        InlineKeyboardButton(text="🎁 Rewards", callback_data="admin_rewards")
    )
    
    builder.row(
        InlineKeyboardButton(text="📤 Import", callback_data="admin_import"),
        InlineKeyboardButton(text="📥 Export", callback_data="admin_export")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="admin_menu")
    )
    
    return builder.as_markup()


def get_admin_question_keyboard() -> InlineKeyboardMarkup:
    """Create admin question management keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Add Question", callback_data="admin_add_question"),
        InlineKeyboardButton(text="📝 Edit Question", callback_data="admin_edit_question")
    )
    
    builder.row(
        InlineKeyboardButton(text="🗑️ Delete Question", callback_data="admin_delete_question"),
        InlineKeyboardButton(text="📊 Question Stats", callback_data="admin_question_stats")
    )
    
    builder.row(
        InlineKeyboardButton(text="📤 Bulk Import", callback_data="admin_bulk_import"),
        InlineKeyboardButton(text="🔙 Back", callback_data="admin_content")
    )
    
    return builder.as_markup()


def get_admin_broadcast_keyboard() -> InlineKeyboardMarkup:
    """Create admin broadcast keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📢 Send Broadcast", callback_data="admin_send_broadcast"),
        InlineKeyboardButton(text="👥 Select Users", callback_data="admin_select_users")
    )
    
    builder.row(
        InlineKeyboardButton(text="📋 Templates", callback_data="admin_broadcast_templates"),
        InlineKeyboardButton(text="📊 History", callback_data="admin_broadcast_history")
    )
    
    builder.row(
        InlineKeyboardButton(text="⚙️ Settings", callback_data="admin_broadcast_settings"),
        InlineKeyboardButton(text="🔙 Back", callback_data="admin_menu")
    )
    
    return builder.as_markup()


def get_admin_user_actions_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create admin user actions keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👤 View Profile", callback_data=f"admin_view_user_{user_id}"),
        InlineKeyboardButton(text="✏️ Edit User", callback_data=f"admin_edit_user_{user_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="🚫 Ban User", callback_data=f"admin_ban_user_{user_id}"),
        InlineKeyboardButton(text="✅ Unban User", callback_data=f"admin_unban_user_{user_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="💎 Give Premium", callback_data=f"admin_premium_user_{user_id}"),
        InlineKeyboardButton(text="💰 Add Coins", callback_data=f"admin_coins_user_{user_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="📊 Send Message", callback_data=f"admin_message_user_{user_id}"),
        InlineKeyboardButton(text="🔙 Back", callback_data="admin_users")
    )
    
    return builder.as_markup()


def get_admin_settings_keyboard() -> InlineKeyboardMarkup:
    """Create admin settings keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🤖 Bot Settings", callback_data="admin_bot_settings"),
        InlineKeyboardButton(text="🎮 Game Settings", callback_data="admin_game_settings")
    )
    
    builder.row(
        InlineKeyboardButton(text="💰 Economy Settings", callback_data="admin_economy_settings"),
        InlineKeyboardButton(text="🔐 Security Settings", callback_data="admin_security_settings")
    )
    
    builder.row(
        InlineKeyboardButton(text="📊 Analytics Settings", callback_data="admin_analytics_settings"),
        InlineKeyboardButton(text="🗄️ Database Settings", callback_data="admin_database_settings")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="admin_menu")
    )
    
    return builder.as_markup()


def get_admin_confirmation_keyboard(action: str, target: str) -> InlineKeyboardMarkup:
    """Create admin confirmation keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Confirm", callback_data=f"admin_confirm_{action}_{target}"),
        InlineKeyboardButton(text="❌ Cancel", callback_data=f"admin_cancel_{action}")
    )
    
    return builder.as_markup()
