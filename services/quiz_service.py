"""
Quiz service for managing quiz logic and data.
"""

import logging
from typing import List, Dict, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from models.question import Question, Difficulty
from models.category import Category
from models.game_session import GameSession
from models.user import User
from utils.helpers import generate_random_questions, calculate_quiz_rewards

logger = logging.getLogger(__name__)


class QuizService:
    """Service for managing quiz operations."""
    
    @staticmethod
    async def get_available_categories(db_session: AsyncSession) -> List[Category]:
        """Get all active categories."""
        result = await db_session.execute(
            select(Category).where(Category.is_active == True).order_by(Category.name)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_questions_for_category(
        db_session: AsyncSession,
        category_id: int,
        difficulty: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Question]:
        """Get questions for a specific category."""
        query = select(Question).where(
            and_(
                Question.category_id == category_id,
                Question.is_active == True
            )
        )
        
        if difficulty:
            query = query.where(Question.difficulty == difficulty)
        
        if limit:
            query = query.limit(limit)
        
        result = await db_session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_random_questions(
        db_session: AsyncSession,
        category_id: int,
        count: int,
        difficulty: Optional[int] = None
    ) -> List[Question]:
        """Get random questions for a quiz."""
        questions = await QuizService.get_questions_for_category(
            db_session, category_id, difficulty
        )
        
        if len(questions) <= count:
            return questions
        
        # Randomly select questions
        import random
        return random.sample(questions, count)
    
    @staticmethod
    async def create_game_session(
        db_session: AsyncSession,
        user_id: int,
        category_id: int,
        game_mode: str,
        difficulty: int,
        max_questions: int,
        question_ids: List[int]
    ) -> GameSession:
        """Create a new game session."""
        # Get user database ID
        user_result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Create game session
        session = GameSession(
            user_id=user.id,
            category_id=category_id,
            game_mode=game_mode,
            difficulty=difficulty,
            max_questions=max_questions,
            questions_asked=question_ids
        )
        
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        return session
    
    @staticmethod
    async def update_game_session(
        db_session: AsyncSession,
        session_id: int,
        current_question: int,
        correct_answers: int,
        wrong_answers: int,
        score: int,
        combo: int,
        max_combo: int,
        answers: List[int]
    ) -> None:
        """Update game session progress."""
        result = await db_session.execute(
            select(GameSession).where(GameSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError(f"Game session {session_id} not found")
        
        session.current_question = current_question
        session.correct_answers = correct_answers
        session.wrong_answers = wrong_answers
        session.score = score
        session.combo = combo
        session.max_combo = max_combo
        session.answers_given = answers
        
        await db_session.commit()
    
    @staticmethod
    async def complete_game_session(
        db_session: AsyncSession,
        session_id: int,
        total_time: int,
        earned_xp: int,
        earned_coins: int
    ) -> GameSession:
        """Complete a game session and calculate results."""
        result = await db_session.execute(
            select(GameSession).where(GameSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError(f"Game session {session_id} not found")
        
        # Calculate accuracy
        total_answers = session.correct_answers + session.wrong_answers
        accuracy = (session.correct_answers / total_answers * 100) if total_answers > 0 else 0
        
        # Update session
        session.status = "completed"
        session.completed_at = func.now()
        session.total_time = total_time
        session.accuracy = accuracy
        session.earned_xp = earned_xp
        session.earned_coins = earned_coins
        
        await db_session.commit()
        await db_session.refresh(session)
        
        return session
    
    @staticmethod
    async def get_user_quiz_history(
        db_session: AsyncSession,
        user_id: int,
        limit: int = 10
    ) -> List[GameSession]:
        """Get user's quiz history."""
        # Get user database ID
        user_result = await db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            return []
        
        result = await db_session.execute(
            select(GameSession)
            .where(GameSession.user_id == user.id)
            .order_by(GameSession.completed_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_leaderboard(
        db_session: AsyncSession,
        metric: str = "coins",
        limit: int = 10
    ) -> List[User]:
        """Get leaderboard based on different metrics."""
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
    
    @staticmethod
    async def get_category_stats(db_session: AsyncSession, category_id: int) -> Dict:
        """Get statistics for a category."""
        # Get category
        category_result = await db_session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = category_result.scalar_one_or_none()
        
        if not category:
            return {}
        
        # Get question count
        question_result = await db_session.execute(
            select(func.count(Question.id))
            .where(Question.category_id == category_id)
        )
        question_count = question_result.scalar() or 0
        
        # Get play count
        play_result = await db_session.execute(
            select(func.count(GameSession.id))
            .where(GameSession.category_id == category_id)
        )
        play_count = play_result.scalar() or 0
        
        return {
            "category": category,
            "question_count": question_count,
            "play_count": play_count
        }
    
    @staticmethod
    async def validate_answer(question: Question, answer_index: int) -> bool:
        """Validate if answer is correct."""
        return answer_index == question.correct_answer
    
    @staticmethod
    def calculate_time_bonus(time_taken: int, time_limit: int) -> int:
        """Calculate time bonus for quick answers."""
        if time_taken <= time_limit * 0.3:  # Under 30% of time limit
            return 30
        elif time_taken <= time_limit * 0.5:  # Under 50% of time limit
            return 20
        elif time_taken <= time_limit * 0.7:  # Under 70% of time limit
            return 10
        else:
            return 0
