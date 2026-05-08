"""
Level filter for restricting handlers based on user level.
"""

from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User


class LevelFilter(Filter):
    """Filter to allow users based on minimum level."""
    
    def __init__(self, min_level: int = 1):
        self.min_level = min_level
        super().__init__()
    
    async def __call__(self, obj: Message | CallbackQuery, **kwargs) -> bool:
        """Check if user meets minimum level requirement."""
        # Get database session from kwargs
        db_session = kwargs.get('db_session')
        if not db_session:
            return False  # Deny if no session available
        
        # Get user ID
        if isinstance(obj, Message):
            user_id = obj.from_user.id
        elif isinstance(obj, CallbackQuery):
            user_id = obj.from_user.id
        else:
            return False
        
        # Check user level
        try:
            result = await db_session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            # If user doesn't exist or level too low, deny
            if not user or user.level < self.min_level:
                return False
            
            # User meets level requirement, allow
            return True
            
        except Exception:
            # If error occurs, deny by default
            return False
