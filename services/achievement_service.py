"""
Achievement service for managing user achievements and progress.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from models.user import User
from models.achievement import Achievement, AchievementType
from models.user_achievement import UserAchievement

logger = logging.getLogger(__name__)


class AchievementService:
    """Service for managing achievements."""
    
    @staticmethod
    async def get_all_achievements(db_session: AsyncSession) -> List[Achievement]:
        """Get all active achievements."""
        result = await db_session.execute(
            select(Achievement).where(Achievement.is_active == True)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_user_achievements(db_session: AsyncSession, user_id: int) -> List[UserAchievement]:
        """Get user's achievements."""
        # Get user database ID
        user_result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            return []
        
        result = await db_session.execute(
            select(UserAchievement).where(UserAchievement.user_id == user.id)
        )
        return result.scalars().all()
    
    @staticmethod
    async def check_and_unlock_achievements(
        db_session: AsyncSession,
        user_id: int,
        event_type: str,
        event_data: Dict
    ) -> List[Achievement]:
        """Check and unlock achievements based on user events."""
        # Get user
        user_result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            return []
        
        # Get user's existing achievements
        user_achievements_result = await db_session.execute(
            select(UserAchievement).where(UserAchievement.user_id == user.id)
        )
        existing_achievements = {ua.achievement_id: ua for ua in user_achievements_result.scalars().all()}
        
        # Get all achievements
        all_achievements_result = await db_session.execute(
            select(Achievement).where(Achievement.is_active == True)
        )
        achievements = all_achievements_result.scalars().all()
        
        newly_unlocked = []
        
        for achievement in achievements:
            # Skip if already unlocked
            if achievement.id in existing_achievements and existing_achievements[achievement.id].is_completed:
                continue
            
            # Check if achievement should be unlocked
            if await AchievementService._check_achievement_criteria(user, achievement, event_type, event_data):
                # Unlock achievement
                await AchievementService._unlock_achievement(db_session, user, achievement, existing_achievements)
                newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    @staticmethod
    async def _check_achievement_criteria(
        user: User,
        achievement: Achievement,
        event_type: str,
        event_data: Dict
    ) -> bool:
        """Check if user meets achievement criteria."""
        requirements = achievement.requirement
        
        if achievement.type == AchievementType.STREAK.value:
            return user.current_streak >= requirements.get('streak', 0)
        
        elif achievement.type == AchievementType.CORRECT_ANSWERS.value:
            return user.correct_answers >= requirements.get('correct_answers', 0)
        
        elif achievement.type == AchievementType.GAMES_PLAYED.value:
            return user.total_games >= requirements.get('games_played', 0)
        
        elif achievement.type == AchievementType.LEVEL_UP.value:
            return user.level >= requirements.get('level', 0)
        
        elif achievement.type == AchievementType.PERFECT_GAME.value:
            return event_type == 'perfect_game'
        
        elif achievement.type == AchievementType.SPEED.value:
            return event_type == 'speed_bonus' and event_data.get('time_taken', 0) <= requirements.get('max_time', 999)
        
        elif achievement.type == AchievementType.CATEGORY_MASTER.value:
            # This would require checking category-specific stats
            return False  # Placeholder
        
        elif achievement.type == AchievementType.SPECIAL.value:
            # Special achievements with custom logic
            return event_type == requirements.get('event', '')
        
        return False
    
    @staticmethod
    async def _unlock_achievement(
        db_session: AsyncSession,
        user: User,
        achievement: Achievement,
        existing_achievements: Dict[int, UserAchievement]
    ) -> None:
        """Unlock achievement for user."""
        
        if achievement.id in existing_achievements:
            # Update existing achievement
            user_achievement = existing_achievements[achievement.id]
            user_achievement.is_completed = True
            user_achievement.progress = 100
            user_achievement.unlocked_at = datetime.now()
        else:
            # Create new user achievement
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id,
                progress=100,
                is_completed=True,
                unlocked_at=datetime.now()
            )
            db_session.add(user_achievement)
        
        # Give rewards
        user.experience += achievement.reward_xp
        user.coins += achievement.reward_coins
        
        # Update achievement unlock count
        achievement.unlock_count += 1
        
        await db_session.commit()
        
        logger.info(f"Achievement unlocked: {achievement.name} for user {user.telegram_id}")
    
    @staticmethod
    async def update_achievement_progress(
        db_session: AsyncSession,
        user_id: int,
        achievement_id: int,
        progress: int
    ) -> bool:
        """Update progress for an achievement."""
        # Get user
        user_result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            return False
        
        # Get or create user achievement
        result = await db_session.execute(
            select(UserAchievement).where(
                and_(
                    UserAchievement.user_id == user.id,
                    UserAchievement.achievement_id == achievement_id
                )
            )
        )
        user_achievement = result.scalar_one_or_none()
        
        if not user_achievement:
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement_id,
                progress=progress
            )
            db_session.add(user_achievement)
        else:
            user_achievement.progress = max(user_achievement.progress, progress)
        
        # Check if completed
        if user_achievement.progress >= 100 and not user_achievement.is_completed:
            user_achievement.is_completed = True
            user_achievement.unlocked_at = datetime.now()
            
            # Get achievement and give rewards
            achievement_result = await db_session.execute(
                select(Achievement).where(Achievement.id == achievement_id)
            )
            achievement = achievement_result.scalar_one_or_none()
            
            if achievement:
                user.experience += achievement.reward_xp
                user.coins += achievement.reward_coins
                achievement.unlock_count += 1
        
        await db_session.commit()
        return True
    
    @staticmethod
    async def get_achievement_stats(db_session: AsyncSession) -> Dict:
        """Get achievement statistics."""
        # Total achievements
        total_result = await db_session.execute(
            select(func.count(Achievement.id))
        )
        total_achievements = total_result.scalar() or 0
        
        # Active achievements
        active_result = await db_session.execute(
            select(func.count(Achievement.id))
            .where(Achievement.is_active == True)
        )
        active_achievements = active_result.scalar() or 0
        
        # Total unlocks
        unlocks_result = await db_session.execute(
            select(func.sum(Achievement.unlock_count))
        )
        total_unlocks = unlocks_result.scalar() or 0
        
        # Completed user achievements
        completed_result = await db_session.execute(
            select(func.count(UserAchievement.id))
            .where(UserAchievement.is_completed == True)
        )
        completed_count = completed_result.scalar() or 0
        
        return {
            "total_achievements": total_achievements,
            "active_achievements": active_achievements,
            "total_unlocks": total_unlocks,
            "completed_count": completed_count
        }
    
    @staticmethod
    async def create_default_achievements(db_session: AsyncSession) -> None:
        """Create default achievements if they don't exist."""
        default_achievements = [
            {
                "name": "First Steps",
                "description": "Complete your first quiz",
                "emoji": "👶",
                "type": AchievementType.GAMES_PLAYED.value,
                "requirement": {"games_played": 1},
                "reward_xp": 50,
                "reward_coins": 25
            },
            {
                "name": "Quiz Enthusiast",
                "description": "Complete 10 quizzes",
                "emoji": "🎮",
                "type": AchievementType.GAMES_PLAYED.value,
                "requirement": {"games_played": 10},
                "reward_xp": 100,
                "reward_coins": 50
            },
            {
                "name": "Quiz Master",
                "description": "Complete 100 quizzes",
                "emoji": "🏆",
                "type": AchievementType.GAMES_PLAYED.value,
                "requirement": {"games_played": 100},
                "reward_xp": 500,
                "reward_coins": 250
            },
            {
                "name": "Knowledge Seeker",
                "description": "Answer 100 questions correctly",
                "emoji": "🧠",
                "type": AchievementType.CORRECT_ANSWERS.value,
                "requirement": {"correct_answers": 100},
                "reward_xp": 200,
                "reward_coins": 100
            },
            {
                "name": "Perfect Score",
                "description": "Complete a quiz with 100% accuracy",
                "emoji": "💯",
                "type": AchievementType.PERFECT_GAME.value,
                "requirement": {},
                "reward_xp": 100,
                "reward_coins": 50
            },
            {
                "name": "Speed Demon",
                "description": "Answer a question in under 5 seconds",
                "emoji": "⚡",
                "type": AchievementType.SPEED.value,
                "requirement": {"max_time": 5},
                "reward_xp": 75,
                "reward_coins": 35
            },
            {
                "name": "Week Warrior",
                "description": "Maintain a 7-day streak",
                "emoji": "🔥",
                "type": AchievementType.STREAK.value,
                "requirement": {"streak": 7},
                "reward_xp": 150,
                "reward_coins": 75
            },
            {
                "name": "Monthly Champion",
                "description": "Maintain a 30-day streak",
                "emoji": "👑",
                "type": AchievementType.STREAK.value,
                "requirement": {"streak": 30},
                "reward_xp": 500,
                "reward_coins": 250
            },
            {
                "name": "Level Up!",
                "description": "Reach level 10",
                "emoji": "⬆️",
                "type": AchievementType.LEVEL_UP.value,
                "requirement": {"level": 10},
                "reward_xp": 200,
                "reward_coins": 100
            },
            {
                "name": "Expert Player",
                "description": "Reach level 50",
                "emoji": "🎯",
                "type": AchievementType.LEVEL_UP.value,
                "requirement": {"level": 50},
                "reward_xp": 1000,
                "reward_coins": 500
            }
        ]
        
        for achievement_data in default_achievements:
            # Check if achievement already exists
            result = await db_session.execute(
                select(Achievement).where(Achievement.name == achievement_data["name"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                achievement = Achievement(**achievement_data)
                db_session.add(achievement)
        
        await db_session.commit()
        logger.info("Default achievements created")
