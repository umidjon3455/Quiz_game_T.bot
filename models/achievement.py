"""
Achievement model for user achievements and badges.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from database.engine import Base
from enum import Enum


class AchievementType(Enum):
    """Achievement types."""
    STREAK = "streak"
    CORRECT_ANSWERS = "correct_answers"
    GAMES_PLAYED = "games_played"
    LEVEL_UP = "level_up"
    PERFECT_GAME = "perfect_game"
    SPEED = "speed"
    CATEGORY_MASTER = "category_master"
    SPECIAL = "special"


class Achievement(Base):
    """Achievement model for defining user achievements."""
    
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    emoji = Column(String(10), default="🏆", nullable=False)
    
    # Achievement details
    type = Column(String(20), nullable=False)
    requirement = Column(JSON, nullable=False)  # Achievement requirements
    reward_xp = Column(Integer, default=0, nullable=False)
    reward_coins = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    
    # Statistics
    unlock_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<Achievement(id={self.id}, name={self.name}, type={self.type})>"
    
    @property
    def type_name(self) -> str:
        """Get formatted type name."""
        type_names = {
            AchievementType.STREAK.value: "🔥 Streak",
            AchievementType.CORRECT_ANSWERS.value: "✅ Correct Answers",
            AchievementType.GAMES_PLAYED.value: "🎮 Games Played",
            AchievementType.LEVEL_UP.value: "⬆️ Level Up",
            AchievementType.PERFECT_GAME.value: "💯 Perfect Game",
            AchievementType.SPEED.value: "⚡ Speed",
            AchievementType.CATEGORY_MASTER.value: "🎓 Category Master",
            AchievementType.SPECIAL.value: "✨ Special"
        }
        return type_names.get(self.type, "📋 General")
