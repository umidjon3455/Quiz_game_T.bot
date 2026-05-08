"""
Banned filter for preventing banned users from using the bot.
"""

from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User


class BannedFilter(Filter):
    """Filter to block banned users."""
    
    def __init__(self):
        super().__init__()
    
    async def __call__(self, obj: Message | CallbackQuery, **kwargs) -> bool:
        """Check if user is not banned."""
        # Get database session from kwargs
        db_session = kwargs.get('db_session')
        if not db_session:
            return True  # Allow if no session available
        
        # Get user ID
        if isinstance(obj, Message):
            user_id = obj.from_user.id
        elif isinstance(obj, CallbackQuery):
            user_id = obj.from_user.id
        else:
            return True
        
        # Check if user is banned
        try:
            result = await db_session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            # If user doesn't exist or is not banned, allow
            if not user or not user.is_banned:
                return True
            
            # User is banned, block
            return False
            
        except Exception:
            # If error occurs, allow by default
            return True
