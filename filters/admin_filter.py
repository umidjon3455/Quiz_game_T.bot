"""
Admin filter for restricting handlers to admin users only.
"""

from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery

from config import settings


class AdminFilter(Filter):
    """Filter to allow only admin users."""
    
    def __init__(self):
        super().__init__()
    
    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        """Check if user is admin."""
        if isinstance(obj, Message):
            user_id = obj.from_user.id
        elif isinstance(obj, CallbackQuery):
            user_id = obj.from_user.id
        else:
            return False
        
        return settings.is_admin(user_id)
