"""
Game session model for tracking user quiz sessions.
"""

from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.engine import Base
from enum import Enum


class GameMode(Enum):
    """Game mode types."""
    CLASSIC = "classic"
    TIMED = "timed"
    ENDLESS = "endless"
    SURVIVAL = "survival"
    DUEL = "duel"
    MIXED = "mixed"


class GameStatus(Enum):
    """Game session status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    TIMEOUT = "timeout"


class GameSession(Base):
    """Game session model for tracking quiz games."""
    
    __tablename__ = "game_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Game settings
    game_mode = Column(String(20), default=GameMode.CLASSIC.value, nullable=False)
    difficulty = Column(Integer, default=1, nullable=False)
    max_questions = Column(Integer, default=10, nullable=False)
    time_per_question = Column(Integer, default=30, nullable=False)
    
    # Game progress
    current_question = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    wrong_answers = Column(Integer, default=0, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    combo = Column(Integer, default=0, nullable=False)
    max_combo = Column(Integer, default=0, nullable=False)
    
    # Game details
    questions_asked = Column(JSON, nullable=True)  # List of question IDs
    answers_given = Column(JSON, nullable=True)  # List of user answers
    time_taken = Column(JSON, nullable=True)  # Time taken for each question
    
    # Status and timing
    status = Column(String(20), default=GameStatus.ACTIVE.value, nullable=False)
    started_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Results
    total_time = Column(Integer, default=0, nullable=False)  # Total time in seconds
    accuracy = Column(Float, default=0.0, nullable=False)
    earned_xp = Column(Integer, default=0, nullable=False)
    earned_coins = Column(Integer, default=0, nullable=False)
    
    # Relationships
    user = relationship("User", backref="game_sessions")
    category = relationship("Category", backref="game_sessions")
    
    def __repr__(self) -> str:
        return f"<GameSession(id={self.id}, user_id={self.user_id}, mode={self.game_mode})>"
    
    @property
    def total_answers(self) -> int:
        """Get total number of answers."""
        return self.correct_answers + self.wrong_answers
    
    @property
    def accuracy_rate(self) -> float:
        """Calculate accuracy rate."""
        if self.total_answers == 0:
            return 0.0
        return (self.correct_answers / self.total_answers) * 100
    
    @property
    def is_completed(self) -> bool:
        """Check if game is completed."""
        return self.status == GameStatus.COMPLETED.value
    
    @property
    def is_active(self) -> bool:
        """Check if game is active."""
        return self.status == GameStatus.ACTIVE.value
    
    @property
    def progress_percentage(self) -> float:
        """Calculate game progress percentage."""
        if self.max_questions == 0:
            return 0.0
        return (self.current_question / self.max_questions) * 100
