"""
Daily reward model for tracking user daily bonuses.
"""

from sqlalchemy import Column, Integer, BigInteger, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from database.engine import Base


class DailyReward(Base):
    """Daily reward model for tracking user daily bonuses."""
    
    __tablename__ = "daily_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    
    # Reward details
    day_streak = Column(Integer, default=1, nullable=False)
    coins_rewarded = Column(Integer, default=0, nullable=False)
    xp_rewarded = Column(Integer, default=0, nullable=False)
    
    # Bonus items
    bonus_items = Column(JSON, nullable=True)  # Additional bonus items
    
    # Status
    is_claimed = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    reward_date = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<DailyReward(user_id={self.user_id}, day_streak={self.day_streak}, claimed={self.is_claimed})>"
    
    @property
    def total_reward_value(self) -> int:
        """Calculate total reward value."""
        return self.coins_rewarded + (self.xp_rewarded // 10)  # 1 XP = 0.1 coins value
