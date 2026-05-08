"""
Question model for storing quiz questions.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.engine import Base
from enum import Enum


class Difficulty(Enum):
    """Question difficulty levels."""
    EASY = 1
    MEDIUM = 2
    HARD = 3


class Question(Base):
    """Question model for storing quiz questions."""
    
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_image = Column(String(512), nullable=True)
    question_type = Column(String(20), default="multiple_choice", nullable=False)
    
    # Answer options
    options = Column(JSON, nullable=False)  # List of answer options
    correct_answer = Column(Integer, nullable=False)  # Index of correct answer
    explanation = Column(Text, nullable=True)
    
    # Question settings
    difficulty = Column(Integer, default=Difficulty.EASY.value, nullable=False)
    time_limit = Column(Integer, default=30, nullable=False)  # seconds
    points = Column(Integer, default=10, nullable=False)
    
    # Statistics
    total_attempts = Column(Integer, default=0, nullable=False)
    correct_attempts = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    category = relationship("Category", backref="questions")
    
    def __repr__(self) -> str:
        return f"<Question(id={self.id}, category_id={self.category_id}, difficulty={self.difficulty})>"
    
    @property
    def accuracy_rate(self) -> float:
        """Calculate question accuracy rate."""
        if self.total_attempts == 0:
            return 0.0
        return (self.correct_attempts / self.total_attempts) * 100
    
    @property
    def difficulty_name(self) -> str:
        """Get difficulty name as string."""
        difficulty_map = {
            Difficulty.EASY.value: "Easy",
            Difficulty.MEDIUM.value: "Medium", 
            Difficulty.HARD.value: "Hard"
        }
        return difficulty_map.get(self.difficulty, "Unknown")
