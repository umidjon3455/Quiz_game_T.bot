"""
User achievement model for tracking unlocked achievements.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.engine import Base


class UserAchievement(Base):
    """User achievement model for tracking user's unlocked achievements."""
    
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False, index=True)
    
    # Progress tracking
    progress = Column(Integer, default=0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    
    # Additional data
    progress_data = Column(Text, nullable=True)  # JSON string for complex progress
    
    # Timestamps
    unlocked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="user_achievements")
    achievement = relationship("Achievement", backref="user_achievements")
    
    def __repr__(self) -> str:
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id}, completed={self.is_completed})>"
