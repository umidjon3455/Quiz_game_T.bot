"""
User model for storing Telegram user information and game stats.
"""

from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Text, Float
from sqlalchemy.sql import func
from database.engine import Base


class User(Base):
    """User model representing a Telegram bot user."""
    
    __tablename__ = "users"
    
    # Basic user information
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(64), nullable=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=True)
    language_code = Column(String(10), nullable=True)
    
    # Game statistics
    level = Column(Integer, default=1, nullable=False)
    experience = Column(Integer, default=0, nullable=False)
    coins = Column(Integer, default=0, nullable=False)
    total_games = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    wrong_answers = Column(Integer, default=0, nullable=False)
    
    # Streak and activity
    current_streak = Column(Integer, default=0, nullable=False)
    max_streak = Column(Integer, default=0, nullable=False)
    last_active = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    daily_claimed = Column(DateTime(timezone=True), nullable=True)
    
    # User preferences
    is_banned = Column(Boolean, default=False, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    sound_enabled = Column(Boolean, default=True, nullable=False)
    
    # Additional fields
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(512), nullable=True)
    rank = Column(String(50), default="Newbie", nullable=False)
    
    # Statistics
    win_rate = Column(Float, default=0.0, nullable=False)
    avg_score = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"
    
    @property
    def total_answers(self) -> int:
        """Get total number of answers."""
        return self.correct_answers + self.wrong_answers
    
    @property
    def accuracy_rate(self) -> float:
        """Calculate answer accuracy rate."""
        if self.total_answers == 0:
            return 0.0
        return (self.correct_answers / self.total_answers) * 100
    
    @property
    def experience_to_next_level(self) -> int:
        """Calculate experience needed for next level."""
        return self.level * 100 - self.experience
    
    @property
    def is_level_up_ready(self) -> bool:
        """Check if user can level up."""
        return self.experience >= self.level * 100
