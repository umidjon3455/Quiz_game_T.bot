"""
Premium filter for restricting handlers to premium users only.
"""

from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User


class PremiumFilter(Filter):
    """Filter to allow only premium users."""
    
    def __init__(self):
        super().__init__()
    
    async def __call__(self, obj: Message | CallbackQuery, **kwargs) -> bool:
        """Check if user is premium."""
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
        
        # Check if user is premium
        try:
            result = await db_session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            # If user doesn't exist or is not premium, deny
            if not user or not user.is_premium:
                return False
            
            # User is premium, allow
            return True
            
        except Exception:
            # If error occurs, deny by default
            return False
