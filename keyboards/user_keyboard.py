"""
User profile and settings keyboard layouts.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Create user profile keyboard with actions."""
    
    builder = InlineKeyboardBuilder()
    
    # Profile actions
    builder.row(
        InlineKeyboardButton(text="📊 View Stats", callback_data="view_stats"),
        InlineKeyboardButton(text="🏆 Achievements", callback_data="achievements")
    )
    
    builder.row(
        InlineKeyboardButton(text="🎁 Daily Bonus", callback_data="daily_bonus"),
        InlineKeyboardButton(text="👥 Referrals", callback_data="referrals")
    )
    
    builder.row(
        InlineKeyboardButton(text="⚙️ Settings", callback_data="settings"),
        InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_settings_keyboard(user: object) -> InlineKeyboardMarkup:
    """Create settings keyboard with user preferences."""
    
    builder = InlineKeyboardBuilder()
    
    # Notification settings
    notif_text = "🔔 ON" if user.notifications_enabled else "🔕 OFF"
    sound_text = "🔊 ON" if user.sound_enabled else "🔇 OFF"
    
    builder.row(
        InlineKeyboardButton(text=f"Notifications {notif_text}", callback_data="toggle_notifications"),
        InlineKeyboardButton(text=f"Sound {sound_text}", callback_data="toggle_sound")
    )
    
    # Profile settings
    builder.row(
        InlineKeyboardButton(text="✏️ Edit Bio", callback_data="edit_bio"),
        InlineKeyboardButton(text="🌐 Language", callback_data="language")
    )
    
    # Privacy settings
    builder.row(
        InlineKeyboardButton(text="👥 Privacy", callback_data="privacy"),
        InlineKeyboardButton(text="📊 Data", callback_data="data_management")
    )
    
    # Support
    builder.row(
        InlineKeyboardButton(text="💬 Support", callback_data="support"),
        InlineKeyboardButton(text="📝 Feedback", callback_data="feedback")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="profile")
    )
    
    return builder.as_markup()


def get_achievements_keyboard(achievements: list, user_achievements: list) -> InlineKeyboardMarkup:
    """Create achievements keyboard with progress indicators."""
    
    builder = InlineKeyboardBuilder()
    
    # Group achievements by category
    for achievement in achievements[:10]:  # Show first 10
        user_achievement = next((ua for ua in user_achievements if ua.achievement_id == achievement.id), None)
        
        if user_achievement and user_achievement.is_completed:
            status = "✅"
            callback_data = f"achievement_view_{achievement.id}"
        else:
            status = "🔒"
            callback_data = f"achievement_view_{achievement.id}"
        
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {achievement.emoji} {achievement.name}",
                callback_data=callback_data
            )
        )
    
    # Navigation
    builder.row(
        InlineKeyboardButton(text="📄 More", callback_data="achievements_more"),
        InlineKeyboardButton(text="🔙 Back", callback_data="profile")
    )
    
    return builder.as_markup()


def get_referrals_keyboard(referral_code: str, referral_count: int) -> InlineKeyboardMarkup:
    """Create referrals keyboard with referral info."""
    
    builder = InlineKeyboardBuilder()
    
    # Referral info
    builder.row(
        InlineKeyboardButton(text="📊 My Referrals", callback_data="my_referrals"),
        InlineKeyboardButton(text="🎁 Referral Rewards", callback_data="referral_rewards")
    )
    
    # Share referral
    builder.row(
        InlineKeyboardButton(text="📤 Share Referral", callback_data="share_referral"),
        InlineKeyboardButton(text="📋 Copy Code", callback_data="copy_referral")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="profile")
    )
    
    return builder.as_markup()


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Create language selection keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    languages = [
        ("🇬🇧 English", "en"),
        ("🇷🇺 Русский", "ru"),
        ("🇪🇸 Español", "es"),
        ("🇫🇷 Français", "fr"),
        ("🇩🇪 Deutsch", "de"),
        ("🇮🇹 Italiano", "it"),
        ("🇵🇹 Português", "pt"),
        ("🇹🇷 Türkçe", "tr")
    ]
    
    # Add languages in rows of 2
    for i in range(0, len(languages), 2):
        row_buttons = []
        
        if i < len(languages):
            flag, code = languages[i]
            row_buttons.append(
                InlineKeyboardButton(text=flag, callback_data=f"lang_{code}")
            )
        
        if i + 1 < len(languages):
            flag, code = languages[i + 1]
            row_buttons.append(
                InlineKeyboardButton(text=flag, callback_data=f"lang_{code}")
            )
        
        if row_buttons:
            builder.row(*row_buttons)
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="settings")
    )
    
    return builder.as_markup()


def get_privacy_keyboard() -> InlineKeyboardMarkup:
    """Create privacy settings keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👁️ Profile Visibility", callback_data="profile_visibility"),
        InlineKeyboardButton(text="📊 Stats Visibility", callback_data="stats_visibility")
    )
    
    builder.row(
        InlineKeyboardButton(text="🚫 Block User", callback_data="block_user"),
        InlineKeyboardButton(text="📝 Report Issue", callback_data="report_issue")
    )
    
    builder.row(
        InlineKeyboardButton(text="🗑️ Delete Account", callback_data="delete_account"),
        InlineKeyboardButton(text="🔙 Back", callback_data="settings")
    )
    
    return builder.as_markup()


def get_daily_bonus_keyboard(streak: int, can_claim: bool) -> InlineKeyboardMarkup:
    """Create daily bonus keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    if can_claim:
        builder.row(
            InlineKeyboardButton(text="🎁 Claim Bonus!", callback_data="claim_daily_bonus")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="⏰ Already Claimed", callback_data="daily_info")
        )
    
    builder.row(
        InlineKeyboardButton(text="📊 Bonus History", callback_data="bonus_history"),
        InlineKeyboardButton(text="🔙 Back", callback_data="profile")
    )
    
    return builder.as_markup()


def get_stats_keyboard() -> InlineKeyboardMarkup:
    """Create detailed statistics keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 Overall Stats", callback_data="stats_overall"),
        InlineKeyboardButton(text="🎯 Category Stats", callback_data="stats_category")
    )
    
    builder.row(
        InlineKeyboardButton(text="📈 Progress Chart", callback_data="stats_progress"),
        InlineKeyboardButton(text="🏆 Best Games", callback_data="stats_best")
    )
    
    builder.row(
        InlineKeyboardButton(text="📤 Export Stats", callback_data="stats_export"),
        InlineKeyboardButton(text="🔙 Back", callback_data="profile")
    )
    
    return builder.as_markup()
