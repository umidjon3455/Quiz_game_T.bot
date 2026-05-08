"""
Main bot configuration and dispatcher setup.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiogram
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from database.redis_client import redis_client
from .loader import setup_bot, setup_handlers, setup_middlewares


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/bot.log", encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)

# Initialize bot with default properties
bot = Bot(
    token=settings.bot_token,
    default_properties=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        protect_content=True
    )
)

# Initialize dispatcher
dp = Dispatcher(
    fsm_strategy=FSMStrategy.CHAT,
    disable_web_page_preview=True
)

# Initialize scheduler
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def bot_lifespan() -> AsyncGenerator[None, None]:
    """Manage bot lifecycle."""
    try:
        logger.info("Starting bot initialization...")
        
        # Connect to Redis
        await redis_client.connect()
        logger.info("✅ Redis connected")
        
        # Setup bot components
        await setup_bot()
        await setup_handlers(dp)
        await setup_middlewares(dp)
        logger.info("✅ Bot components initialized")
        
        # Start scheduler if enabled
        if settings.scheduler_enabled:
            scheduler.start()
            logger.info("✅ Scheduler started")
        
        logger.info("🚀 Bot started successfully!")
        yield
        
    except Exception as e:
        logger.error(f"❌ Error during bot startup: {e}")
        raise
    finally:
        logger.info("Shutting down bot...")
        
        # Stop scheduler
        if scheduler.running:
            scheduler.shutdown()
            logger.info("✅ Scheduler stopped")
        
        # Disconnect from Redis
        await redis_client.disconnect()
        logger.info("✅ Redis disconnected")
        
        # Close bot session
        await bot.session.close()
        logger.info("✅ Bot session closed")
        
        logger.info("👋 Bot shutdown complete")


async def main() -> None:
    """Main entry point for the bot."""
    async with bot_lifespan():
        # Start polling
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )


def run_bot() -> None:
    """Run the bot (synchronous entry point)."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    run_bot()
