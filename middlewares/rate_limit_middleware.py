"""
Rate limiting middleware for preventing spam and abuse.
"""

import asyncio
import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from config import settings


class RateLimitMiddleware(BaseMiddleware):
    """Middleware for rate limiting user requests."""
    
    def __init__(self):
        self.user_requests: Dict[int, list] = {}
        self.user_last_request: Dict[int, float] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Check rate limits before processing request."""
        
        # Get user ID
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if not user_id:
            return await handler(event, data)
        
        current_time = time.time()
        
        # Check per-second limit
        await self._check_per_second_limit(user_id, current_time)
        
        # Check per-minute limit
        await self._check_per_minute_limit(user_id, current_time)
        
        # Update last request time
        self.user_last_request[user_id] = current_time
        
        return await handler(event, data)
    
    async def _check_per_second_limit(self, user_id: int, current_time: float) -> None:
        """Check per-second rate limit."""
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        # Remove requests older than 1 second
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if current_time - req_time < 1.0
        ]
        
        # Check if user exceeded limit
        if len(self.user_requests[user_id]) >= settings.rate_limit_per_second:
            await asyncio.sleep(0.5)  # Small delay
        
        # Add current request
        self.user_requests[user_id].append(current_time)
    
    async def _check_per_minute_limit(self, user_id: int, current_time: float) -> None:
        """Check per-minute rate limit."""
        minute_key = f"{user_id}_{int(current_time // 60)}"
        
        if minute_key not in self.user_requests:
            self.user_requests[minute_key] = 0
        
        # Increment counter
        self.user_requests[minute_key] += 1
        
        # Check if user exceeded minute limit
        if self.user_requests[minute_key] > settings.rate_limit_per_minute:
            raise Exception("Rate limit exceeded. Please wait before trying again.")
