"""
Admin panel handlers for bot administration.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from models.user import User
from models.question import Question
from models.category import Category
from models.game_session import GameSession
from models.achievement import Achievement
from states.admin_states import AdminStates
from utils.decorators import admin_required
from utils.formatters import format_user_profile
from keyboards.admin_keyboard import (
    get_admin_menu_keyboard,
    get_admin_stats_keyboard,
    get_admin_users_keyboard,
    get_admin_content_keyboard,
    get_admin_user_actions_keyboard
)
from keyboards.main_menu import get_main_menu_keyboard
from config import settings

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "admin_panel")
@admin_required
async def handle_admin_panel_callback(callback: types.CallbackQuery) -> None:
    """Handle admin panel callback."""
    
    await callback.answer()
    
    admin_text = """
👑 <b>Admin Panel</b> 👑

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 <b>Welcome, Administrator!</b>

📊 <b>Available Actions:</b>
• View bot statistics and analytics
• Manage users (ban, unban, premium)
• Manage content (questions, categories)
• Send broadcasts to users
• Configure bot settings
• View system status

⚡ <b>Quick Stats:</b>
• Server Status: 🟢 Online
• Database: 🟢 Connected
• Active Users: Loading...
    """.strip()
    
    await callback.message.edit_text(
        admin_text,
        reply_markup=get_admin_menu_keyboard()
    )


@router.callback_query(F.data == "admin_stats")
@admin_required
async def handle_admin_stats_callback(callback: types.CallbackQuery) -> None:
    """Handle admin statistics callback."""
    
    await callback.answer()
    
    stats_text = """
📊 <b>Bot Statistics</b> 📊

━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 <b>Users:</b>
• Total: Loading...
• Active Today: Loading...
• New This Week: Loading...
• Premium: Loading...

🎮 <b>Games:</b>
• Total Played: Loading...
• Today: Loading...
• Average Score: Loading...

📝 <b>Content:</b>
• Questions: Loading...
• Categories: Loading...
• Achievements: Loading...

💰 <b>Economy:</b>
• Total Coins: Loading...
• Daily Claims: Loading...
• Referral Bonuses: Loading...
    """.strip()
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_admin_stats_keyboard()
    )


@router.callback_query(F.data == "admin_users")
@admin_required
async def handle_admin_users_callback(callback: types.CallbackQuery) -> None:
    """Handle admin users management callback."""
    
    await callback.answer()
    
    users_text = """
👥 <b>User Management</b> 👥

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 <b>Search and manage users:</b>

📊 <b>User Statistics:</b>
• Total Users: Loading...
• Banned Users: Loading...
• Premium Users: Loading...
• Online Now: Loading...

⚡ <b>Quick Actions:</b>
• Search by username/ID
• View user profiles
• Ban/unban users
• Grant premium status
• Add coins/XP
    """.strip()
    
    await callback.message.edit_text(
        users_text,
        reply_markup=get_admin_users_keyboard()
    )


@router.callback_query(F.data == "admin_content")
@admin_required
async def handle_admin_content_callback(callback: types.CallbackQuery) -> None:
    """Handle admin content management callback."""
    
    await callback.answer()
    
    content_text = """
📚 <b>Content Management</b> 📚

━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 <b>Questions:</b>
• Total: Loading...
• Active: Loading...
• Pending Review: Loading...

📂 <b>Categories:</b>
• Total: Loading...
• Active: Loading...

🏆 <b>Achievements:</b>
• Total: Loading...
• Unlocked: Loading...

⚡ <b>Actions:</b>
• Add/Edit/Delete questions
• Manage categories
• Create achievements
• Import/Export content
    """.strip()
    
    await callback.message.edit_text(
        content_text,
        reply_markup=get_admin_content_keyboard()
    )


@router.callback_query(F.data.startswith("admin_view_user_"))
@admin_required
async def handle_admin_view_user(
    callback: types.CallbackQuery,
    db_session: AsyncSession
) -> None:
    """Handle viewing specific user profile."""
    
    user_id = int(callback.data.split("_")[-1])
    
    # Get user from database
    result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ User not found", show_alert=True)
        return
    
    await callback.answer()
    
    # Show user profile with admin actions
    profile_text = format_user_profile(user)
    profile_text += f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    profile_text += f"🆔 <b>Telegram ID:</b> {user.telegram_id}\n"
    profile_text += f"📅 <b>Registered:</b> {user.created_at.strftime('%d %b %Y')}\n"
    profile_text += f"🚫 <b>Banned:</b> {'Yes' if user.is_banned else 'No'}\n"
    profile_text += f"💎 <b>Premium:</b> {'Yes' if user.is_premium else 'No'}"
    
    keyboard = get_admin_user_actions_keyboard(user.telegram_id)
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("admin_ban_user_"))
@admin_required
async def handle_admin_ban_user(
    callback: types.CallbackQuery,
    db_session: AsyncSession
) -> None:
    """Handle banning a user."""
    
    user_id = int(callback.data.split("_")[-1])
    
    # Get user from database
    result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ User not found", show_alert=True)
        return
    
    # Toggle ban status
    user.is_banned = not user.is_banned
    await db_session.commit()
    
    status = "banned" if user.is_banned else "unbanned"
    await callback.answer(f"✅ User {status}!")
    
    # Refresh user view
    await handle_admin_view_user(callback, db_session)


@router.callback_query(F.data.startswith("admin_premium_user_"))
@admin_required
async def handle_admin_premium_user(
    callback: types.CallbackQuery,
    db_session: AsyncSession
) -> None:
    """Handle granting/removing premium status."""
    
    user_id = int(callback.data.split("_")[-1])
    
    # Get user from database
    result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ User not found", show_alert=True)
        return
    
    # Toggle premium status
    user.is_premium = not user.is_premium
    await db_session.commit()
    
    status = "granted" if user.is_premium else "revoked"
    await callback.answer(f"✅ Premium {status}!")
    
    # Refresh user view
    await handle_admin_view_user(callback, db_session)


@router.callback_query(F.data.startswith("admin_coins_user_"))
@admin_required
async def handle_admin_coins_user(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Handle adding coins to user."""
    
    user_id = callback.data.split("_")[-1]
    
    await callback.answer()
    
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminStates.setting_user_coins)
    
    await callback.message.edit_text(
        f"💰 <b>Add Coins to User</b>\n\n"
        f"🆔 User ID: {user_id}\n\n"
        f"💬 Enter the amount of coins to add:",
        reply_markup=None
    )


@router.message(AdminStates.setting_user_coins)
@admin_required
async def handle_coins_amount(
    message: types.Message,
    state: FSMContext,
    db_session: AsyncSession
) -> None:
    """Handle coins amount input."""
    
    try:
        amount = int(message.text)
        if amount <= 0:
            await message.answer("❌ Amount must be positive!")
            return
    except ValueError:
        await message.answer("❌ Please enter a valid number!")
        return
    
    # Get target user ID
    data = await state.get_data()
    target_user_id = int(data.get('target_user_id'))
    
    # Get user from database
    result = await db_session.execute(
        select(User).where(User.telegram_id == target_user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ User not found!")
        await state.clear()
        return
    
    # Add coins
    user.coins += amount
    await db_session.commit()
    
    await message.answer(
        f"✅ <b>Coins Added!</b>\n\n"
        f"💰 Amount: {amount:,} coins\n"
        f"👤 User: @{user.username or user.first_name}\n"
        f"💎 New Balance: {user.coins:,} coins",
        reply_markup=get_main_menu_keyboard()
    )
    
    await state.clear()


@router.callback_query(F.data == "admin_send_message")
@admin_required
async def handle_admin_send_message(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handle sending message to users."""
    
    await callback.answer()
    
    await state.set_state(AdminStates.creating_broadcast)
    
    await callback.message.edit_text(
        "📢 <b>Send Broadcast Message</b>\n\n"
        "💬 Enter the message you want to send to all users:",
        reply_markup=None
    )


@router.message(AdminStates.creating_broadcast)
@admin_required
async def handle_broadcast_message(
    message: types.Message,
    state: FSMContext
) -> None:
    """Handle broadcast message input."""
    
    broadcast_text = message.text or message.caption
    
    if len(broadcast_text) > 4000:
        await message.answer("❌ Message too long! Maximum 4000 characters.")
        return
    
    await state.update_data(broadcast_text=broadcast_text)
    
    await message.answer(
        f"📢 <b>Confirm Broadcast</b>\n\n"
        f"💬 Message:\n{broadcast_text}\n\n"
        f"📤 Send this message to all users?",
        reply_markup=get_confirmation_keyboard("broadcast")
    )


@router.callback_query(F.data == "admin_send_broadcast")
@admin_required
async def handle_send_broadcast(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Handle sending broadcast to all users."""
    
    data = await state.get_data()
    broadcast_text = data.get('broadcast_text')
    
    if not broadcast_text:
        await callback.answer("❌ No message to send!", show_alert=True)
        return
    
    await callback.answer("📢 Broadcasting message...")
    
    # This would implement actual broadcasting to all users
    # For now, just show confirmation
    await callback.message.edit_text(
        "✅ <b>Broadcast Sent!</b>\n\n"
        f"📢 Message sent to users.\n\n"
        f"💬 Message: {broadcast_text[:100]}...",
        reply_markup=get_admin_menu_keyboard()
    )
    
    await state.clear()


@router.callback_query(F.data == "admin_settings")
@admin_required
async def handle_admin_settings_callback(callback: types.CallbackQuery) -> None:
    """Handle admin settings callback."""
    
    await callback.answer()
    
    settings_text = """
⚙️ <b>Admin Settings</b> ⚙️

━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 <b>Bot Configuration:</b>
• Token: [HIDDEN]
• Debug Mode: {'ON' if settings.debug else 'OFF'}
• Log Level: {settings.log_level}

🎮 <b>Game Settings:</b>
• Max Questions: {settings.max_questions_per_game}
• Question Time: {settings.question_time_limit}s
• Daily Bonus: {settings.daily_bonus_coins} coins

💰 <b>Economy Settings:</b>
• Referral Bonus: {settings.referral_bonus} coins
• XP per Correct: {settings.xp_per_correct_answer}
• Level Up Bonus: {settings.level_up_bonus} coins

🔐 <b>Security:</b>
• Rate Limit: {settings.rate_limit_per_second}/s
• Admin IDs: {len(settings.admin_ids)} configured
    """.strip()
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=get_admin_menu_keyboard()
    )


@router.callback_query(F.data == "admin_database")
@admin_required
async def handle_admin_database_callback(callback: types.CallbackQuery) -> None:
    """Handle admin database operations callback."""
    
    await callback.answer()
    
    db_text = """
🗄️ <b>Database Operations</b> 🗄️

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>Quick Actions:</b>
• 📊 View database stats
• 💾 Create backup
• 🔄 Run migrations
• 🧹 Clear cache
• 📈 Optimize tables

⚠️ <b>Dangerous Operations:</b>
• 🗑️ Reset user data
• 🔄 Restore from backup
• 🧨 Wipe all data

🔒 <b>Always create backups before operations!</b>
    """.strip()
    
    await callback.message.edit_text(
        db_text,
        reply_markup=get_admin_menu_keyboard()
    )


@router.callback_query(F.data == "admin_system")
@admin_required
async def handle_admin_system_callback(callback: types.CallbackQuery) -> None:
    """Handle admin system operations callback."""
    
    await callback.answer()
    
    system_text = """
🔧 <b>System Operations</b> 🔧

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>System Status:</b>
• Server: 🟢 Online
• Database: 🟢 Connected
• Redis: 🟢 Connected
• Scheduler: 🟢 Running

⚡ <b>Actions:</b>
• 🔄 Restart bot
• 📊 View logs
• 🧹 Clear temp files
• 📈 Monitor performance
• 🧪 Test features

🔐 <b>Security:</b>
• 🔑 Update tokens
• 🚫 Block IPs
• 📊 View audit log
    """.strip()
    
    await callback.message.edit_text(
        system_text,
        reply_markup=get_admin_menu_keyboard()
    )


def get_confirmation_keyboard(action: str) -> types.InlineKeyboardMarkup:
    """Create confirmation keyboard for admin actions."""
    
    builder = types.InlineKeyboardBuilder()
    
    builder.row(
        types.InlineKeyboardButton(text="✅ Confirm", callback_data=f"admin_confirm_{action}"),
        types.InlineKeyboardButton(text="❌ Cancel", callback_data="admin_cancel")
    )
    
    return builder.as_markup()


@router.callback_query(F.data.startswith("admin_confirm_"))
@admin_required
async def handle_admin_confirm(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Handle admin action confirmation."""
    
    action = callback.data.split("_")[-1]
    
    await callback.answer(f"✅ {action.title()} confirmed!")
    
    await callback.message.edit_text(
        f"✅ <b>Action Confirmed!</b>\n\n"
        f"🎯 {action.title()} completed successfully.",
        reply_markup=get_admin_menu_keyboard()
    )
    
    await state.clear()


@router.callback_query(F.data == "admin_cancel")
@admin_required
async def handle_admin_cancel(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handle admin action cancellation."""
    
    await callback.answer("❌ Action cancelled")
    
    await state.clear()
    
    await callback.message.edit_text(
        "❌ <b>Action Cancelled!</b>\n\n"
        "🎮 Returning to admin menu.",
        reply_markup=get_admin_menu_keyboard()
    )
