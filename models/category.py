"""
Category model for quiz question categories.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from database.engine import Base


class Category(Base):
    """Category model for organizing quiz questions."""
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    emoji = Column(String(10), default="📚", nullable=False)
    
    # Category settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    min_level = Column(Integer, default=1, nullable=False)
    
    # Statistics
    question_count = Column(Integer, default=0, nullable=False)
    play_count = Column(Integer, default=0, nullable=False)
    avg_difficulty = Column(Integer, default=1, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name}, emoji={self.emoji})>"
