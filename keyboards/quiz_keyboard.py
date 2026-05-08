"""
Quiz-specific keyboard layouts.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_category_keyboard(categories: list, user_level: int = 1) -> InlineKeyboardMarkup:
    """Create category selection keyboard for quiz."""
    
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
                    text=f"{status} {category.emoji} {category.name} ({category.question_count})",
                    callback_data=f"quiz_category_{category.id}"
                )
            )
        
        # Second category in row
        if i + 1 < len(categories):
            category = categories[i + 1]
            is_locked = category.min_level > user_level
            status = "🔒" if is_locked else "✅"
            
            row_buttons.append(
                InlineKeyboardButton(
                    text=f"{status} {category.emoji} {category.name} ({category.question_count})",
                    callback_data=f"quiz_category_{category.id}"
                )
            )
        
        if row_buttons:
            builder.row(*row_buttons)
    
    # Navigation buttons
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="quiz_modes")
    )
    
    return builder.as_markup()


def get_difficulty_keyboard() -> InlineKeyboardMarkup:
    """Create difficulty selection keyboard for quiz."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🟢 Easy (10 XP)", callback_data="quiz_difficulty_1"),
        InlineKeyboardButton(text="🟡 Medium (15 XP)", callback_data="quiz_difficulty_2"),
        InlineKeyboardButton(text="🔴 Hard (20 XP)", callback_data="quiz_difficulty_3")
    )
    
    builder.row(
        InlineKeyboardButton(text="🎲 Random (10-20 XP)", callback_data="quiz_difficulty_random")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="quiz_categories")
    )
    
    return builder.as_markup()


def get_question_count_keyboard() -> InlineKeyboardMarkup:
    """Create question count selection keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="⚡ Quick (5)", callback_data="quiz_count_5"),
        InlineKeyboardButton(text="🎯 Standard (10)", callback_data="quiz_count_10"),
        InlineKeyboardButton(text="📊 Extended (20)", callback_data="quiz_count_20")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔄 Endless", callback_data="quiz_count_endless"),
        InlineKeyboardButton(text="🎲 Random", callback_data="quiz_count_random")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="quiz_difficulty")
    )
    
    return builder.as_markup()


def get_quiz_answer_keyboard(
    options: list, 
    question_number: int, 
    total_questions: int,
    time_remaining: int = 30
) -> InlineKeyboardMarkup:
    """Create quiz answer keyboard with progress and timer."""
    
    builder = InlineKeyboardBuilder()
    
    # Add answer options
    for i, option in enumerate(options):
        # Truncate long options
        display_text = option[:35] + "..." if len(option) > 35 else option
        
        builder.row(
            InlineKeyboardButton(
                text=f"{chr(65 + i)}) {display_text}",
                callback_data=f"quiz_answer_{i}"
            )
        )
    
    # Progress and timer row
    progress_text = f"📊 Q{question_number}/{total_questions} | ⏱️ {time_remaining}s"
    builder.row(
        InlineKeyboardButton(text=progress_text, callback_data="quiz_info")
    )
    
    # Skip and end buttons
    builder.row(
        InlineKeyboardButton(text="⏭️ Skip", callback_data="quiz_skip"),
        InlineKeyboardButton(text="❌ End Quiz", callback_data="quiz_end")
    )
    
    return builder.as_markup()


def get_quiz_results_keyboard(session_results: dict) -> InlineKeyboardMarkup:
    """Create quiz results keyboard with actions."""
    
    builder = InlineKeyboardBuilder()
    
    # Action buttons
    builder.row(
        InlineKeyboardButton(text="🔄 Play Again", callback_data="quiz_play_again"),
        InlineKeyboardButton(text="🏆 Share Results", callback_data="quiz_share")
    )
    
    builder.row(
        InlineKeyboardButton(text="📊 View Details", callback_data="quiz_details"),
        InlineKeyboardButton(text="🎮 Main Menu", callback_data="main_menu")
    )
    
    # Leaderboard button if score is good
    if session_results.get('accuracy', 0) >= 70:
        builder.row(
            InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard")
        )
    
    return builder.as_markup()


def get_quiz_settings_keyboard(current_settings: dict) -> InlineKeyboardMarkup:
    """Create quiz settings keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    # Timer settings
    timer_text = f"⏱️ {current_settings.get('time_per_question', 30)}s"
    builder.row(
        InlineKeyboardButton(text=timer_text, callback_data="quiz_timer"),
        InlineKeyboardButton(text="🎯 Question Count", callback_data="quiz_count")
    )
    
    # Difficulty settings
    builder.row(
        InlineKeyboardButton(text="📊 Difficulty", callback_data="quiz_difficulty"),
        InlineKeyboardButton(text="🎮 Game Mode", callback_data="quiz_mode")
    )
    
    # Category settings
    builder.row(
        InlineKeyboardButton(text="📚 Categories", callback_data="quiz_categories"),
        InlineKeyboardButton(text="🎲 Random Mix", callback_data="quiz_random")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_duel_invite_keyboard() -> InlineKeyboardMarkup:
    """Create duel invitation keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👤 Choose Opponent", callback_data="duel_choose_opponent"),
        InlineKeyboardButton(text="🎲 Random Opponent", callback_data="duel_random")
    )
    
    builder.row(
        InlineKeyboardButton(text="📤 Invite Friend", callback_data="duel_invite_friend"),
        InlineKeyboardButton(text="🔙 Back", callback_data="quiz_modes")
    )
    
    return builder.as_markup()


def get_tournament_keyboard(tournaments: list) -> InlineKeyboardMarkup:
    """Create tournament selection keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    for tournament in tournaments:
        status = "🟢" if tournament.is_active else "🔴"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {tournament.name}",
                callback_data=f"tournament_{tournament.id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_power_ups_keyboard(power_ups: list, user_coins: int) -> InlineKeyboardMarkup:
    """Create power-ups selection keyboard."""
    
    builder = InlineKeyboardBuilder()
    
    power_up_buttons = []
    for power_up in power_ups:
        can_afford = user_coins >= power_up.cost
        status = "✅" if can_afford else "🔒"
        
        power_up_buttons.append(
            InlineKeyboardButton(
                text=f"{status} {power_up.emoji} {power_up.name} ({power_up.cost} coins)",
                callback_data=f"powerup_{power_up.id}"
            )
        )
    
    # Add buttons in rows of 2
    for i in range(0, len(power_up_buttons), 2):
        if i + 1 < len(power_up_buttons):
            builder.row(power_up_buttons[i], power_up_buttons[i + 1])
        else:
            builder.row(power_up_buttons[i])
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="quiz_start")
    )
    
    return builder.as_markup()


def get_quiz_confirmation_keyboard(quiz_config: dict) -> InlineKeyboardMarkup:
    """Create quiz confirmation keyboard with summary."""
    
    builder = InlineKeyboardBuilder()
    
    # Summary text would be in the message, buttons for confirmation
    builder.row(
        InlineKeyboardButton(text="🚀 Start Quiz!", callback_data="quiz_start_confirm"),
        InlineKeyboardButton(text="⚙️ Change Settings", callback_data="quiz_change_settings")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
    )
    
    return builder.as_markup()
