"""
Redis middleware for providing Redis client to handlers.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database.redis_client import redis_client


class RedisMiddleware(BaseMiddleware):
    """Middleware to provide Redis client to handlers."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Provide Redis client to handler."""
        data["redis"] = redis_client
        return await handler(event, data)
