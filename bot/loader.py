"""
Bot loader for setting up handlers, middlewares, and other components.
"""

import logging
from typing import NoReturn

from aiogram import Dispatcher
from aiogram.types import BotCommand

from handlers import (
    start_handlers,
    quiz_handlers,
    user_handlers,
    admin_handlers,
    callback_handlers
)
from middlewares import (
    DatabaseMiddleware,
    RedisMiddleware,
    RateLimitMiddleware,
    LoggingMiddleware
)

logger = logging.getLogger(__name__)


async def setup_bot() -> None:
    """Setup bot commands and other bot-specific configurations."""
    from bot import bot
    
    # Set bot commands
    commands = [
        BotCommand(command="/start", description="🚀 Start the bot"),
        BotCommand(command="/help", description="❓ Get help"),
        BotCommand(command="/profile", description="👤 View your profile"),
        BotCommand(command="/leaderboard", description="🏆 View leaderboard"),
        BotCommand(command="/daily", description="🎁 Claim daily bonus"),
        BotCommand(command="/quiz", description="🎮 Start a quiz"),
        BotCommand(command="/admin", description="👑 Admin panel"),
        BotCommand(command="/cancel", description="❌ Cancel current action"),
    ]
    
    await bot.set_my_commands(commands)
    logger.info("✅ Bot commands set")


async def setup_handlers(dp: Dispatcher) -> None:
    """Setup all bot handlers."""
    try:
        # Include all handler routers
        dp.include_router(start_handlers.router)
        dp.include_router(quiz_handlers.router)
        dp.include_router(user_handlers.router)
        dp.include_router(admin_handlers.router)
        dp.include_router(callback_handlers.router)
        
        logger.info("✅ All handlers registered")
        
    except Exception as e:
        logger.error(f"❌ Error setting up handlers: {e}")
        raise


async def setup_middlewares(dp: Dispatcher) -> None:
    """Setup bot middlewares."""
    try:
        # Setup middlewares in order
        dp.update.middleware(LoggingMiddleware())
        dp.update.middleware(DatabaseMiddleware())
        dp.update.middleware(RedisMiddleware())
        dp.update.middleware(RateLimitMiddleware())
        
        logger.info("✅ All middlewares registered")
        
    except Exception as e:
        logger.error(f"❌ Error setting up middlewares: {e}")
        raise


async def setup_filters(dp: Dispatcher) -> None:
    """Setup custom filters."""
    try:
        # Import and register custom filters
        from filters import AdminFilter, BannedFilter, PremiumFilter
        
        # Register filters
        dp.message.filter(AdminFilter())
        dp.message.filter(BannedFilter())
        dp.message.filter(PremiumFilter())
        
        logger.info("✅ Custom filters registered")
        
    except Exception as e:
        logger.error(f"❌ Error setting up filters: {e}")
        raise
