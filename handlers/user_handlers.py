"""
User profile and settings handlers.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from models.user import User
from models.daily_reward import DailyReward
from models.user_achievement import UserAchievement, Achievement
from models.referral import Referral
from states.user_states import UserStates
from utils.formatters import (
    format_user_profile,
    format_leaderboard,
    format_daily_bonus,
    format_achievement_notification
)
from utils.helpers import (
    calculate_daily_bonus,
    is_new_day,
    get_time_until_next_reset,
    generate_referral_code
)
from keyboards.user_keyboard import (
    get_profile_keyboard,
    get_settings_keyboard,
    get_achievements_keyboard,
    get_daily_bonus_keyboard
)
from keyboards.main_menu import get_main_menu_keyboard, get_leaderboard_type_keyboard
from config import settings

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "profile")
async def handle_profile_callback(
    callback: types.CallbackQuery,
    db_session: AsyncSession
) -> None:
    """Handle profile button callback."""
    
    user_id = callback.from_user.id
    
    # Get user from database
    result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ Profile not found", show_alert=True)
        return
    
    await callback.answer()
    
    await callback.message.edit_text(
        format_user_profile(user),
        reply_markup=get_profile_keyboard()
    )


@router.callback_query(F.data == "settings")
async def handle_settings_callback(
    callback: types.CallbackQuery,
    db_session: AsyncSession
) -> None:
    """Handle settings button callback."""
    
    user_id = callback.from_user.id
    
    # Get user from database
    result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ User not found", show_alert=True)
        return
    
    await callback.answer()
    
    settings_text = f"""
⚙️ <b>Settings</b> ⚙️

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔔 <b>Notifications:</b> {'ON' if user.notifications_enabled else 'OFF'}
🔊 <b>Sound Effects:</b> {'ON' if user.sound_enabled else 'OFF'}
🌐 <b>Language:</b> {user.language_code or 'English'}
👤 <b>Username:</b> @{user.username or 'Not set'}

💎 <b>Premium Status:</b> {'✅ Active' if user.is_premium else '❌ Inactive'}
🎯 <b>Level:</b> {user.level}
💰 <b>Coins:</b> {user.coins:,}
    """.strip()
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=get_settings_keyboard(user)
    )


@router.callback_query(F.data.startswith("toggle_"))
async def handle_toggle_settings(
    callback: types.CallbackQuery,
    db_session: AsyncSession
) -> None:
    """Handle toggle settings callbacks."""
    
    setting = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    # Get user from database
    result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ User not found", show_alert=True)
        return
    
    # Toggle setting
    if setting == "notifications":
        user.notifications_enabled = not user.notifications_enabled
        status = "enabled" if user.notifications_enabled else "disabled"
        await callback.answer(f"🔔 Notifications {status}")
    elif setting == "sound":
        user.sound_enabled = not user.sound_enabled
        status = "enabled" if user.sound_enabled else "disabled"
        await callback.answer(f"🔊 Sound {status}")
    else:
        await callback.answer("❌ Unknown setting", show_alert=True)
        return
    
    await db_session.commit()
    
    # Update settings message
    await handle_settings_callback(callback, db_session)


@router.callback_query(F.data == "daily_bonus")
async def handle_daily_bonus_callback(
    callback: types.CallbackQuery,
    db_session: AsyncSession
) -> None:
    """Handle daily bonus callback."""
    
    user_id = callback.from_user.id
    
    # Get user from database
    result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ User not found", show_alert=True)
        return
    
    # Check if user can claim daily bonus
    can_claim = True
    streak = 1
    
    if user.daily_claimed and is_new_day(user.daily_claimed):
        # Can claim today
        streak = user.current_streak + 1
    elif user.daily_claimed and not is_new_day(user.daily_claimed):
        # Already claimed today
        can_claim = False
        streak = user.current_streak
    
    await callback.answer()
    
    if can_claim:
        bonus_text = f"""
🎁 <b>Daily Bonus</b> 🎁

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 <b>Current Streak:</b> {streak} days
💰 <b>Base Bonus:</b> {settings.daily_bonus_coins} coins
🎯 <b>Multiplier:</b> {min(1.0 + (streak - 1) * 0.1, 2.0):.1f}x

💎 <b>Total Bonus:</b> {calculate_daily_bonus(streak, settings.daily_bonus_coins):,} coins
⭐ <b>XP Bonus:</b> {calculate_daily_bonus(streak, 50):,} XP

🎊 <b>Claim your daily reward!</b>
        """.strip()
        
        keyboard = get_daily_bonus_keyboard(streak, True)
    else:
        time_until_reset = get_time_until_next_reset()
        hours = time_until_reset // 3600
        minutes = (time_until_reset % 3600) // 60
        
        bonus_text = f"""
🎁 <b>Daily Bonus</b> 🎁

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 <b>Current Streak:</b> {user.current_streak} days
⏰ <b>Next Bonus:</b> In {hours}h {minutes}m

🎊 <b>Come back tomorrow for your reward!</b>
        """.strip()
        
        keyboard = get_daily_bonus_keyboard(user.current_streak, False)
    
    await callback.message.edit_text(bonus_text, reply_markup=keyboard)


@router.callback_query(F.data == "claim_daily_bonus")
async def handle_claim_daily_bonus(
    callback: types.CallbackQuery,
    db_session: AsyncSession
) -> None:
    """Handle claiming daily bonus."""
    
    user_id = callback.from_user.id
    
    # Get user from database
    result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ User not found", show_alert=True)
        return
    
    # Check if can claim
    if user.daily_claimed and not is_new_day(user.daily_claimed):
        await callback.answer("⏰ Already claimed today!", show_alert=True)
        return
    
    # Calculate streak and bonus
    if user.daily_claimed and is_new_day(user.daily_claimed):
        streak = user.current_streak + 1
    else:
        streak = 1
    
    bonus_coins = calculate_daily_bonus(streak, settings.daily_bonus_coins)
    bonus_xp = calculate_daily_bonus(streak, 50)
    
    # Update user
    user.coins += bonus_coins
    user.experience += bonus_xp
    user.current_streak = streak
    user.max_streak = max(user.max_streak, streak)
    user.daily_claimed = datetime.now()
    user.last_active = datetime.now()
    
    # Create daily reward record
    daily_reward = DailyReward(
        user_id=user_id,
        day_streak=streak,
        coins_rewarded=bonus_coins,
        xp_rewarded=bonus_xp,
        is_claimed=True,
        claimed_at=datetime.now()
    )
    
    db_session.add(daily_reward)
    await db_session.commit()
    
    await callback.answer()
    
    # Show success message
    success_text = format_daily_bonus(streak, bonus_coins)
    
    await callback.message.edit_text(
        success_text,
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "leaderboard")
async def handle_leaderboard_callback(callback: types.CallbackQuery) -> None:
    """Handle leaderboard callback."""
    
    await callback.answer()
    
    await callback.message.edit_text(
        "🏆 <b>Select Leaderboard Type</b>\n\n"
        "Choose which leaderboard you want to view:",
        reply_markup=get_leaderboard_type_keyboard()
    )


@router.callback_query(F.data.startswith("leaderboard_"))
async def handle_leaderboard_type(
    callback: types.CallbackQuery,
    db_session: AsyncSession,
    **kwargs
) -> None:
    """Handle leaderboard type selection."""
    
    leaderboard_type = callback.data.split("_")[-1]
    
    await callback.answer()
    
    # Get top users
    result = await db_session.execute(
        select(User)
        .where(User.is_banned == False)
        .order_by(User.coins.desc())
        .limit(10)
    )
    top_users = result.scalars().all()
    
    # Get current user
    current_user_id = callback.from_user.id
    current_user_result = await db_session.execute(
        select(User).where(User.telegram_id == current_user_id)
    )
    current_user = current_user_result.scalar_one_or_none()
    
    leaderboard_text = format_leaderboard(top_users, current_user)
    
    await callback.message.edit_text(
        leaderboard_text,
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "achievements")
async def handle_achievements_callback(
    callback: types.CallbackQuery,
    db_session: AsyncSession
) -> None:
    """Handle achievements callback."""
    
    user_id = callback.from_user.id
    
    # Get user and achievements
    user_result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ User not found", show_alert=True)
        return
    
    # Get achievements
    achievements_result = await db_session.execute(
        select(Achievement).where(Achievement.is_active == True).limit(10)
    )
    achievements = achievements_result.scalars().all()
    
    # Get user achievements
    user_achievements_result = await db_session.execute(
        select(UserAchievement).where(UserAchievement.user_id == user.id)
    )
    user_achievements = user_achievements_result.scalars().all()
    
    await callback.answer()
    
    achievements_text = f"""
🏆 <b>Achievements</b> 🏆

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 <b>Unlocked:</b> {len([ua for ua in user_achievements if ua.is_completed])}/{len(achievements)}
⭐ <b>Total Points:</b> {sum(ua.achievement.reward_xp for ua in user_achievements if ua.is_completed)}
💰 <b>Bonus Coins:</b> {sum(ua.achievement.reward_coins for ua in user_achievements if ua.is_completed)}

🎮 <b>Keep playing to unlock more!</b>
    """.strip()
    
    await callback.message.edit_text(
        achievements_text,
        reply_markup=get_achievements_keyboard(achievements, user_achievements)
    )


@router.callback_query(F.data == "referrals")
async def handle_referrals_callback(
    callback: types.CallbackQuery,
    db_session: AsyncSession
) -> None:
    """Handle referrals callback."""
    
    user_id = callback.from_user.id
    
    # Get user
    user_result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ User not found", show_alert=True)
        return
    
    # Get referral count
    referral_result = await db_session.execute(
        select(func.count(Referral.id)).where(Referral.referrer_id == user_id)
    )
    referral_count = referral_result.scalar() or 0
    
    await callback.answer()
    
    referral_code = getattr(user, 'referral_code', generate_referral_code())
    
    referrals_text = f"""
👥 <b>Referral System</b> 👥

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 <b>Your Referral Code:</b>
<code>{referral_code}</code>

👥 <b>Referrals:</b> {referral_count}
🎁 <b>Bonus per Referral:</b> {settings.referral_bonus} coins

💡 <b>How it works:</b>
1. Share your referral code with friends
2. Friends use your code when starting the bot
3. You get bonus coins when they play their first game
4. Your friends also get a welcome bonus!

📤 <b>Share your code and earn rewards!</b>
    """.strip()
    
    # Create referral keyboard
    from keyboards.user_keyboard import get_referrals_keyboard
    keyboard = get_referrals_keyboard(referral_code, referral_count)
    
    await callback.message.edit_text(referrals_text, reply_markup=keyboard)


@router.message(F.text.lower().in_(["profile", "my profile", "👤"]))
async def handle_profile_message(message: types.Message, db_session: AsyncSession) -> None:
    """Handle profile text messages."""
    
    user_id = message.from_user.id
    
    # Get user from database
    result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Profile not found. Please start the bot with /start")
        return
    
    await message.answer(
        format_user_profile(user),
        reply_markup=get_profile_keyboard()
    )


@router.message(F.text.lower().in_(["leaderboard", "top", "🏆"]))
async def handle_leaderboard_message(message: types.Message, db_session: AsyncSession) -> None:
    """Handle leaderboard text messages."""
    
    # Get top users
    result = await db_session.execute(
        select(User)
        .where(User.is_banned == False)
        .order_by(User.coins.desc())
        .limit(10)
    )
    top_users = result.scalars().all()
    
    # Get current user
    current_user_id = message.from_user.id
    current_user_result = await db_session.execute(
        select(User).where(User.telegram_id == current_user_id)
    )
    current_user = current_user_result.scalar_one_or_none()
    
    leaderboard_text = format_leaderboard(top_users, current_user)
    
    await message.answer(leaderboard_text, reply_markup=get_main_menu_keyboard())


@router.message(F.text.lower().in_(["daily", "bonus", "🎁"]))
async def handle_daily_bonus_message(message: types.Message, db_session: AsyncSession) -> None:
    """Handle daily bonus text messages."""
    
    # Use the callback handler logic
    await handle_daily_bonus_callback(
        types.CallbackQuery(id="dummy", from_user=message.from_user, message=message),
        db_session
    )
