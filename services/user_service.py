"""
User service for managing user operations and statistics.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update

from models.user import User
from models.daily_reward import DailyReward
from models.referral import Referral
from utils.helpers import (
    calculate_daily_bonus,
    is_new_day,
    get_user_rank,
    calculate_level_xp,
    get_time_until_next_reset
)

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user operations."""
    
    @staticmethod
    async def get_or_create_user(
        db_session: AsyncSession,
        telegram_id: int,
        username: Optional[str],
        first_name: str,
        last_name: Optional[str],
        language_code: Optional[str]
    ) -> User:
        """Get existing user or create new one."""
        # Try to get existing user
        result = await db_session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Update user info if changed
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.language_code = language_code
            user.last_active = datetime.now()
            await db_session.commit()
            return user
        else:
            # Create new user
            new_user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code,
                rank=get_user_rank(1)
            )
            
            db_session.add(new_user)
            await db_session.commit()
            await db_session.refresh(new_user)
            
            logger.info(f"Created new user: {telegram_id} (@{username})")
            return new_user
    
    @staticmethod
    async def update_user_stats(
        db_session: AsyncSession,
        user_id: int,
        correct_answers: int,
        wrong_answers: int,
        earned_xp: int,
        earned_coins: int
    ) -> Tuple[User, bool]:
        """Update user statistics after a game."""
        result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Update stats
        user.correct_answers += correct_answers
        user.wrong_answers += wrong_answers
        user.total_games += 1
        user.experience += earned_xp
        user.coins += earned_coins
        user.last_active = datetime.now()
        
        # Check for level up
        level_up = False
        required_xp = calculate_level_xp(user.level)
        
        while user.experience >= required_xp:
            user.experience -= required_xp
            user.level += 1
            user.rank = get_user_rank(user.level)
            user.coins += 500  # Level up bonus
            required_xp = calculate_level_xp(user.level)
            level_up = True
        
        # Update win rate and accuracy
        total_answers = user.correct_answers + user.wrong_answers
        if total_answers > 0:
            user.accuracy_rate = (user.correct_answers / total_answers) * 100
        
        await db_session.commit()
        await db_session.refresh(user)
        
        return user, level_up
    
    @staticmethod
    async def claim_daily_bonus(db_session: AsyncSession, user_id: int) -> Tuple[User, int, int]:
        """Claim daily bonus for user."""
        result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Check if can claim
        if user.daily_claimed and not is_new_day(user.daily_claimed):
            raise ValueError("Daily bonus already claimed today")
        
        # Calculate streak and bonus
        if user.daily_claimed and is_new_day(user.daily_claimed):
            streak = user.current_streak + 1
        else:
            streak = 1
        
        bonus_coins = calculate_daily_bonus(streak, 100)
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
        await db_session.refresh(user)
        
        return user, bonus_coins, bonus_xp
    
    @staticmethod
    async def get_user_profile(db_session: AsyncSession, user_id: int) -> Optional[User]:
        """Get user profile."""
        result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user_settings(
        db_session: AsyncSession,
        user_id: int,
        **kwargs
    ) -> User:
        """Update user settings."""
        result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Update provided settings
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.last_active = datetime.now()
        await db_session.commit()
        await db_session.refresh(user)
        
        return user
    
    @staticmethod
    async def get_user_statistics(db_session: AsyncSession, user_id: int) -> Dict:
        """Get detailed user statistics."""
        result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {}
        
        # Get daily rewards history
        daily_result = await db_session.execute(
            select(func.sum(DailyReward.coins_rewarded))
            .where(DailyReward.user_id == user_id)
        )
        total_daily_coins = daily_result.scalar() or 0
        
        # Get referral count
        referral_result = await db_session.execute(
            select(func.count(Referral.id))
            .where(Referral.referrer_id == user_id)
        )
        referral_count = referral_result.scalar() or 0
        
        return {
            "user": user,
            "total_daily_coins": total_daily_coins,
            "referral_count": referral_count,
            "xp_to_next_level": calculate_level_xp(user.level) - user.experience,
            "time_until_reset": get_time_until_next_reset()
        }
    
    @staticmethod
    async def ban_user(db_session: AsyncSession, user_id: int, reason: Optional[str] = None) -> bool:
        """Ban a user."""
        result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        user.is_banned = True
        await db_session.commit()
        
        logger.info(f"User {user_id} banned. Reason: {reason}")
        return True
    
    @staticmethod
    async def unban_user(db_session: AsyncSession, user_id: int) -> bool:
        """Unban a user."""
        result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        user.is_banned = False
        await db_session.commit()
        
        logger.info(f"User {user_id} unbanned")
        return True
    
    @staticmethod
    async def grant_premium(db_session: AsyncSession, user_id: int) -> bool:
        """Grant premium status to user."""
        result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        user.is_premium = True
        await db_session.commit()
        
        logger.info(f"Premium granted to user {user_id}")
        return True
    
    @staticmethod
    async def revoke_premium(db_session: AsyncSession, user_id: int) -> bool:
        """Revoke premium status from user."""
        result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        user.is_premium = False
        await db_session.commit()
        
        logger.info(f"Premium revoked from user {user_id}")
        return True
    
    @staticmethod
    async def add_coins(db_session: AsyncSession, user_id: int, amount: int) -> bool:
        """Add coins to user."""
        if amount <= 0:
            return False
        
        result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        user.coins += amount
        await db_session.commit()
        
        logger.info(f"Added {amount} coins to user {user_id}")
        return True
    
    @staticmethod
    async def get_active_users_count(db_session: AsyncSession, days: int = 7) -> int:
        """Get count of active users in the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        result = await db_session.execute(
            select(func.count(User.id))
            .where(User.last_active >= cutoff_date)
        )
        return result.scalar() or 0
    
    @staticmethod
    async def get_top_users(db_session: AsyncSession, metric: str = "coins", limit: int = 10) -> List[User]:
        """Get top users by metric."""
        if metric == "coins":
            order_by = User.coins.desc()
        elif metric == "level":
            order_by = User.level.desc()
        elif metric == "experience":
            order_by = User.experience.desc()
        elif metric == "accuracy":
            order_by = User.accuracy_rate.desc()
        else:
            order_by = User.coins.desc()
        
        result = await db_session.execute(
            select(User)
            .where(User.is_banned == False)
            .order_by(order_by)
            .limit(limit)
        )
        return result.scalars().all()
