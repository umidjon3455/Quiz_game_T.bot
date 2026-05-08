"""
Main menu keyboard layouts.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create main menu keyboard with beautiful layout."""
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🎮 Play Quiz"),
                KeyboardButton(text="🏆 Leaderboard")
            ],
            [
                KeyboardButton(text="👤 Profile"),
                KeyboardButton(text="🎁 Daily Bonus")
            ],
            [
                KeyboardButton(text="🧠 Random Question"),
                KeyboardButton(text="⚙️ Settings")
            ],
            [
                KeyboardButton(text="👑 Admin Panel"),
                KeyboardButton(text="📊 Statistics")
            ]
        ],
        resize_keyboard=True,
        keyboard_one_time=False,
        input_field_placeholder="🎮 Choose an action..."
    )
    
    return keyboard


def get_main_menu_inline_keyboard() -> InlineKeyboardMarkup:
    """Create inline version of main menu for callbacks."""
    
    builder = InlineKeyboardBuilder()
    
    # Main actions row
    builder.row(
        InlineKeyboardButton(text="🎮 Play Quiz", callback_data="play_quiz"),
        InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard")
    )
    
    # User actions row
    builder.row(
        InlineKeyboardButton(text="👤 Profile", callback_data="profile"),
        InlineKeyboardButton(text="🎁 Daily Bonus", callback_data="daily_bonus")
    )
    
    # Features row
    builder.row(
        InlineKeyboardButton(text="🧠 Random Question", callback_data="random_question"),
        InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")
    )
    
    # Admin row (only shown to admins)
    builder.row(
        InlineKeyboardButton(text="👑 Admin Panel", callback_data="admin_panel"),
        InlineKeyboardButton(text="📊 Statistics", callback_data="statistics")
    )
    
    # Help row
    builder.row(
        InlineKeyboardButton(text="❓ Help", callback_data="help")
    )
    
    return builder.as_markup()


def get_quiz_modes_keyboard() -> InlineKeyboardMarkup:
    """Create quiz mode selection keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🎯 Classic", callback_data="quiz_mode_classic"),
        InlineKeyboardButton(text="⚡ Timed", callback_data="quiz_mode_timed")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔄 Endless", callback_data="quiz_mode_endless"),
        InlineKeyboardButton(text="💪 Survival", callback_data="quiz_mode_survival")
    )
    
    builder.row(
        InlineKeyboardButton(text="⚔️ Duel", callback_data="quiz_mode_duel"),
        InlineKeyboardButton(text="🎲 Mixed", callback_data="quiz_mode_mixed")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_difficulty_keyboard() -> InlineKeyboardMarkup:
    """Create difficulty selection keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🟢 Easy", callback_data="difficulty_easy"),
        InlineKeyboardButton(text="🟡 Medium", callback_data="difficulty_medium"),
        InlineKeyboardButton(text="🔴 Hard", callback_data="difficulty_hard")
    )
    
    builder.row(
        InlineKeyboardButton(text="🎲 Random", callback_data="difficulty_random")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="back_to_modes")
    )
    
    return builder.as_markup()


def get_category_keyboard(categories: list, user_level: int = 1) -> InlineKeyboardMarkup:
    """Create category selection keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    # Add categories in rows of 2
    for i in range(0, len(categories), 2):
        row_buttons = []
        
        # First category in row
        if i < len(categories):
            category = categories[i]
            is_locked = category.min_level > user_level
            status = "🔒" if is_locked else "✅"
            
            row_buttons.append(
                InlineKeyboardButton(
                    text=f"{status} {category.emoji} {category.name}",
                    callback_data=f"category_{category.id}"
                )
            )
        
        # Second category in row
        if i + 1 < len(categories):
            category = categories[i + 1]
            is_locked = category.min_level > user_level
            status = "🔒" if is_locked else "✅"
            
            row_buttons.append(
                InlineKeyboardButton(
                    text=f"{status} {category.emoji} {category.name}",
                    callback_data=f"category_{category.id}"
                )
            )
        
        if row_buttons:
            builder.row(*row_buttons)
    
    # Navigation buttons
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="back_to_difficulty")
    )
    
    return builder.as_markup()


def get_quiz_answer_keyboard(options: list, question_number: int, total_questions: int) -> InlineKeyboardMarkup:
    """Create quiz answer keyboard with progress indicator."""
    
    builder = InlineKeyboardBuilder()
    
    # Add answer options
    for i, option in enumerate(options):
        # Truncate long options
        display_text = option[:30] + "..." if len(option) > 30 else option
        
        builder.row(
            InlineKeyboardButton(
                text=f"{chr(65 + i)}) {display_text}",
                callback_data=f"answer_{i}"
            )
        )
    
    # Progress and navigation row
    progress_text = f"📊 Question {question_number}/{total_questions}"
    builder.row(
        InlineKeyboardButton(text=progress_text, callback_data="quiz_info")
    )
    
    # Cancel button
    builder.row(
        InlineKeyboardButton(text="❌ End Quiz", callback_data="end_quiz")
    )
    
    return builder.as_markup()


def get_leaderboard_type_keyboard() -> InlineKeyboardMarkup:
    """Create leaderboard type selection keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🌍 Global", callback_data="leaderboard_global"),
        InlineKeyboardButton(text="🏆 Weekly", callback_data="leaderboard_weekly")
    )
    
    builder.row(
        InlineKeyboardButton(text="👥 Friends", callback_data="leaderboard_friends"),
        InlineKeyboardButton(text="🎯 Category", callback_data="leaderboard_category")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_confirmation_keyboard(action: str, text: str = "Are you sure?") -> InlineKeyboardMarkup:
    """Create confirmation keyboard for actions."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Yes", callback_data=f"confirm_{action}"),
        InlineKeyboardButton(text="❌ No", callback_data=f"cancel_{action}")
    )
    
    return builder.as_markup()


def get_pagination_keyboard(current_page: int, total_pages: int, prefix: str = "page") -> InlineKeyboardMarkup:
    """Create pagination keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    # Previous button
    if current_page > 1:
        builder.row(
            InlineKeyboardButton(text="⬅️ Previous", callback_data=f"{prefix}_{current_page - 1}")
        )
    
    # Page indicator
    page_text = f"📄 {current_page}/{total_pages}"
    builder.row(
        InlineKeyboardButton(text=page_text, callback_data="page_info")
    )
    
    # Next button
    if current_page < total_pages:
        builder.row(
            InlineKeyboardButton(text="Next ➡️", callback_data=f"{prefix}_{current_page + 1}")
        )
    
    return builder.as_markup()
