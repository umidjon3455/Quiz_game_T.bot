"""
Database middleware for providing database session to handlers.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory


class DatabaseMiddleware(BaseMiddleware):
    """Middleware to provide database session to handlers."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Provide database session to handler."""
        async with async_session_factory() as session:
            data["db_session"] = session
            try:
                return await handler(event, data)
            finally:
                await session.close()
