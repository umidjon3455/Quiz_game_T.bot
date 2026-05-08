"""
Logging middleware for tracking bot activity and debugging.
"""

import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging bot activity."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Log incoming requests and responses."""
        
        # Log incoming request
        await self._log_request(event, data)
        
        try:
            # Process the request
            result = await handler(event, data)
            
            # Log successful response
            await self._log_response(event, data, success=True)
            
            return result
            
        except Exception as e:
            # Log error
            await self._log_response(event, data, success=False, error=e)
            raise
    
    async def _log_request(self, event: TelegramObject, data: Dict[str, Any]) -> None:
        """Log incoming request details."""
        user_info = "Unknown"
        
        if isinstance(event, Message):
            user_info = f"User: {event.from_user.id} (@{event.from_user.username})"
            if event.text:
                logger.info(f"📨 Message: {user_info} | Text: {event.text[:50]}...")
            elif event.caption:
                logger.info(f"📨 Message: {user_info} | Caption: {event.caption[:50]}...")
            else:
                logger.info(f"📨 Message: {user_info} | Type: {event.content_type}")
                
        elif isinstance(event, CallbackQuery):
            user_info = f"User: {event.from_user.id} (@{event.from_user.username})"
            logger.info(f"📨 Callback: {user_info} | Data: {event.data[:50]}...")
    
    async def _log_response(
        self, 
        event: TelegramObject, 
        data: Dict[str, Any], 
        success: bool, 
        error: Exception = None
    ) -> None:
        """Log response details."""
        user_info = "Unknown"
        
        if isinstance(event, Message):
            user_info = f"User: {event.from_user.id}"
        elif isinstance(event, CallbackQuery):
            user_info = f"User: {event.from_user.id}"
        
        if success:
            logger.debug(f"✅ Response: {user_info} | Success")
        else:
            logger.error(f"❌ Response: {user_info} | Error: {str(error)}")
