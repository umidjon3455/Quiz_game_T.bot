"""
Start command and welcome handlers.
"""

import logging
from typing import Dict, Any

from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User
from models.referral import Referral
from utils.formatters import format_user_profile
from utils.helpers import generate_referral_code, is_new_day
from keyboards.main_menu import get_main_menu_keyboard
from keyboards.user_keyboard import get_profile_keyboard
from config import settings

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def handle_start(message: types.Message, db_session: AsyncSession, **kwargs) -> None:
    """Handle /start command with user registration and referral support."""
    
    user_id = message.from_user.id
    user_data = message.from_user
    
    # Parse referral code if present
    referral_code = None
    if message.text and len(message.text.split()) > 1:
        referral_code = message.text.split()[1]
    
    # Check if user exists
    result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    existing_user = result.scalar_one_or_none()
    
    if not existing_user:
        # Create new user
        new_user = User(
            telegram_id=user_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            language_code=user_data.language_code,
            referral_code=generate_referral_code()
        )
        
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
        
        # Handle referral if code provided
        if referral_code:
            await handle_referral(db_session, new_user, referral_code)
        
        # Send welcome message
        await send_welcome_message(message, new_user, is_new=True)
        
    else:
        # Update user info if needed
        existing_user.last_active = message.date
        if user_data.username != existing_user.username:
            existing_user.username = user_data.username
        
        await db_session.commit()
        
        # Send welcome back message
        await send_welcome_message(message, existing_user, is_new=False)


async def handle_referral(db_session: AsyncSession, new_user: User, referral_code: str) -> None:
    """Handle referral processing."""
    try:
        # Find referrer by referral code (this would need to be added to User model)
        # For now, we'll skip this as it requires additional model changes
        logger.info(f"Referral code used: {referral_code} by user {new_user.telegram_id}")
        
        # Create referral record
        referral = Referral(
            referred_id=new_user.telegram_id,
            referral_code=referral_code
        )
        db_session.add(referral)
        
    except Exception as e:
        logger.error(f"Error processing referral: {e}")


async def send_welcome_message(message: types.Message, user: User, is_new: bool) -> None:
    """Send welcome message to user."""
    
    if is_new:
        welcome_text = f"""
🎉 <b>Welcome to Quiz Master, {user.first_name}!</b> 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 I'm your personal quiz bot! Test your knowledge, compete with friends, and climb the leaderboard!

🎮 <b>What you can do:</b>
• 🧠 Answer quiz questions
• 🏆 Compete on leaderboards
• 🎁 Claim daily bonuses
• 👤 Build your profile
• 🎯 Unlock achievements
• 👑 Become a quiz master!

💎 <b>Getting Started:</b>
• Start with easy questions
• Build your streak
• Invite friends for bonuses
• Level up to unlock features

🔥 <b>Your referral code:</b> <code>{user.referral_code if hasattr(user, 'referral_code') else 'COMING_SOON'}</code>
        """.strip()
    else:
        welcome_text = f"""
👋 <b>Welcome back, {user.first_name}!</b> 👋

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 <b>Your Stats:</b>
🌟 Level: <b>{user.level}</b>
💰 Coins: <b>{user.coins:,}</b>
🔥 Streak: <b>{user.current_streak}</b> days
📊 Accuracy: <b>{user.accuracy_rate:.1f}%</b>

🎮 <b>Ready for another quiz?</b>
        """.strip()
    
    # Send welcome message with main menu
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("help"))
async def handle_help(message: types.Message) -> None:
    """Handle /help command."""
    
    help_text = """
❓ <b>Quiz Master Help</b> ❓

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 <b>Commands:</b>
/start - Start the bot
/profile - View your profile
/leaderboard - View leaderboard
/daily - Claim daily bonus
/quiz - Start a quiz
/admin - Admin panel (admins only)
/cancel - Cancel current action

🎯 <b>How to Play:</b>
1. Select a quiz category
2. Choose difficulty level
3. Answer questions within time limit
4. Earn XP and coins for correct answers
5. Build streaks and unlock achievements

💎 <b>Tips:</b>
• Answer quickly for speed bonuses
• Maintain daily streaks for multipliers
• Invite friends for referral bonuses
• Check achievements for special rewards

🏆 <b>Scoring:</b>
• Correct answer = 10 XP + 5 coins
• Speed bonus = up to 30 XP
• Perfect quiz = 50 XP bonus
• Combo multipliers increase rewards

❤️ <b>Need more help?</b>
Contact our support team!
    """.strip()
    
    await message.answer(help_text)


@router.message(Command("profile"))
async def handle_profile_command(
    message: types.Message, 
    db_session: AsyncSession, 
    **kwargs
) -> None:
    """Handle /profile command."""
    
    user_id = message.from_user.id
    
    # Get user from database
    result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Profile not found. Please start the bot with /start")
        return
    
    # Send profile message
    await message.answer(
        format_user_profile(user),
        reply_markup=get_profile_keyboard()
    )


@router.message(Command("cancel"))
async def handle_cancel_command(message: types.Message, state: FSMContext) -> None:
    """Handle /cancel command to cancel current state."""
    
    current_state = await state.get_state()
    
    if current_state:
        await state.clear()
        await message.answer(
            "✅ <b>Action cancelled!</b>\n\n🎮 You're back to the main menu.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await message.answer(
            "ℹ️ <b>No active action to cancel.</b>\n\n🎮 You're already at the main menu.",
            reply_markup=get_main_menu_keyboard()
        )


@router.message(F.text.lower().in_(["menu", "main menu", "🏠", "home"]))
async def handle_menu_request(message: types.Message) -> None:
    """Handle menu requests from user."""
    
    await message.answer(
        "🏠 <b>Main Menu</b>\n\n🎮 What would you like to do?",
        reply_markup=get_main_menu_keyboard()
    )
