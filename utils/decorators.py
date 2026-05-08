"""
Decorators for handler protection and functionality.
"""

import functools
import logging
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import settings

logger = logging.getLogger(__name__)


def admin_required(func: Callable) -> Callable:
    """Decorator to restrict function to admin users only."""
    @functools.wraps(func)
    async def wrapper(event: TelegramObject, *args, **kwargs) -> Any:
        # Get user ID from event
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if not user_id:
            logger.warning("Could not determine user ID for admin check")
            return
        
        # Check if user is admin
        if not settings.is_admin(user_id):
            logger.warning(f"Non-admin user {user_id} attempted to access admin function")
            if isinstance(event, Message):
                await event.answer("🚫 Access denied. Admin privileges required.")
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Access denied. Admin privileges required.", show_alert=True)
            return
        
        return await func(event, *args, **kwargs)
    
    return wrapper


def premium_required(func: Callable) -> Callable:
    """Decorator to restrict function to premium users only."""
    @functools.wraps(func)
    async def wrapper(event: TelegramObject, *args, **kwargs) -> Any:
        # Get user and session from kwargs
        user = kwargs.get('user')
        if not user:
            logger.warning("User object not found for premium check")
            return
        
        # Check if user is premium
        if not user.is_premium:
            if isinstance(event, Message):
                await event.answer("💎 This feature is available for premium users only.\n\n🌟 Upgrade to premium to unlock exclusive features!")
            elif isinstance(event, CallbackQuery):
                await event.answer("💎 Premium feature only!", show_alert=True)
            return
        
        return await func(event, *args, **kwargs)
    
    return wrapper


def rate_limit(calls_per_minute: int = 30) -> Callable:
    """Decorator for rate limiting specific functions."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(event: TelegramObject, *args, **kwargs) -> Any:
            # Get user ID from event
            user_id = None
            if isinstance(event, Message):
                user_id = event.from_user.id
            elif isinstance(event, CallbackQuery):
                user_id = event.from_user.id
            
            if not user_id:
                return await func(event, *args, **kwargs)
            
            # Get Redis client from kwargs
            redis = kwargs.get('redis')
            if not redis:
                logger.warning("Redis client not found for rate limiting")
                return await func(event, *args, **kwargs)
            
            # Check rate limit
            rate_key = f"rate_limit:{user_id}:{func.__name__}"
            current_calls = await redis.get(rate_key) or 0
            
            if int(current_calls) >= calls_per_minute:
                if isinstance(event, Message):
                    await event.answer("⏰ Too many requests! Please wait a moment before trying again.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("⏰ Too many requests!", show_alert=True)
                return
            
            # Increment counter
            await redis.incr(rate_key)
            await redis.expire(rate_key, 60)  # Reset after 1 minute
            
            return await func(event, *args, **kwargs)
        
        return wrapper
    return decorator


def require_level(min_level: int) -> Callable:
    """Decorator to require minimum user level."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(event: TelegramObject, *args, **kwargs) -> Any:
            # Get user from kwargs
            user = kwargs.get('user')
            if not user:
                logger.warning("User object not found for level check")
                return
            
            # Check user level
            if user.level < min_level:
                if isinstance(event, Message):
                    await event.answer(f"📊 You need to be at least level {min_level} to use this feature.\n\n🎯 Current level: {user.level}")
                elif isinstance(event, CallbackQuery):
                    await event.answer(f"📊 Level {min_level} required!", show_alert=True)
                return
            
            return await func(event, *args, **kwargs)
        
        return wrapper
    return decorator


def cancel_state_on_error(func: Callable) -> Callable:
    """Decorator to cancel FSM state on function error."""
    @functools.wraps(func)
    async def wrapper(event: TelegramObject, *args, **kwargs) -> Any:
        # Get FSM context from kwargs
        state: FSMContext = kwargs.get('state')
        if not state:
            return await func(event, *args, **kwargs)
        
        try:
            return await func(event, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            
            # Cancel current state
            await state.clear()
            
            # Notify user
            if isinstance(event, Message):
                await event.answer("❌ An error occurred. The operation has been cancelled.")
            elif isinstance(event, CallbackQuery):
                await event.answer("❌ An error occurred.", show_alert=True)
                await event.message.edit("❌ An error occurred. The operation has been cancelled.")
            
            return
    
    return wrapper


def log_user_action(action_name: str) -> Callable:
    """Decorator to log user actions."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(event: TelegramObject, *args, **kwargs) -> Any:
            # Get user ID from event
            user_id = None
            username = None
            if isinstance(event, Message):
                user_id = event.from_user.id
                username = event.from_user.username
            elif isinstance(event, CallbackQuery):
                user_id = event.from_user.id
                username = event.from_user.username
            
            if user_id:
                logger.info(f"User action: {action_name} | User: {user_id} (@{username})")
            
            return await func(event, *args, **kwargs)
        
        return wrapper
    return decorator


def validate_input(validation_func: Callable) -> Callable:
    """Decorator for input validation."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(event: TelegramObject, *args, **kwargs) -> Any:
            # Get input text
            input_text = None
            if isinstance(event, Message):
                input_text = event.text
            elif isinstance(event, CallbackQuery):
                input_text = event.data
            
            if not input_text:
                return await func(event, *args, **kwargs)
            
            # Validate input
            validation_result = validation_func(input_text)
            if not validation_result.get('valid', False):
                if isinstance(event, Message):
                    await event.answer("❌ Invalid input. Please check your input and try again.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("❌ Invalid input!", show_alert=True)
                return
            
            # Add sanitized input to kwargs
            kwargs['validated_input'] = validation_result.get('sanitized', input_text)
            
            return await func(event, *args, **kwargs)
        
        return wrapper
    return decorator
