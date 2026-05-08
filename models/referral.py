"""
Referral model for tracking user referrals and rewards.
"""

from sqlalchemy import Column, Integer, BigInteger, DateTime, Boolean, Text
from sqlalchemy.sql import func
from database.engine import Base


class Referral(Base):
    """Referral model for tracking user referrals."""
    
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(BigInteger, nullable=False, index=True)  # User who referred
    referred_id = Column(BigInteger, nullable=False, index=True)  # User who was referred
    
    # Reward details
    reward_coins = Column(Integer, default=0, nullable=False)
    reward_xp = Column(Integer, default=0, nullable=False)
    
    # Status
    is_completed = Column(Boolean, default=False, nullable=False)  # Referral completed (new user played first game)
    is_rewarded = Column(Boolean, default=False, nullable=False)  # Rewards were given
    
    # Additional data
    referral_code = Column(Text, nullable=True)  # Custom referral code if used
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    rewarded_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self) -> str:
        return f"<Referral(referrer_id={self.referrer_id}, referred_id={self.referred_id}, completed={self.is_completed})>"
    
    @property
    def total_reward_value(self) -> int:
        """Calculate total reward value."""
        return self.reward_coins + (self.reward_xp // 10)  # 1 XP = 0.1 coins value
