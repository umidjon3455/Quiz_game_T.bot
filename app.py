#!/usr/bin/env python3
"""
Start script for the Telegram Quiz Bot.
This script handles initialization and startup of the bot.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import settings
from database.engine import engine
from database.redis_client import redis_client
from services.achievement_service import AchievementService


def setup_logging():
    """Setup logging configuration."""
    log_level = getattr(logging, settings.log_level.upper())
    
    # Create logs directory if it doesn't exist
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logs_dir / "bot.log", encoding="utf-8"),
            logging.FileHandler(logs_dir / "error.log", encoding="utf-8", level=logging.ERROR)
        ]
    )


async def initialize_database():
    """Initialize database and create tables."""
    from database.engine import Base
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database initialized successfully")
        
        # Create default achievements
        from database.engine import async_session_factory
        async with async_session_factory() as session:
            await AchievementService.create_default_achievements(session)
        
        print("✅ Default achievements created")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


async def initialize_redis():
    """Initialize Redis connection."""
    try:
        await redis_client.connect()
        print("✅ Redis connected successfully")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        raise


async def check_environment():
    """Check if environment is properly configured."""
    required_vars = [
        "BOT_TOKEN",
        "DATABASE_URL",
        "REDIS_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        sys.exit(1)
    
    print("✅ Environment variables check passed")


async def run_migrations():
    """Run database migrations."""
    try:
        import subprocess
        
        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print("✅ Database migrations completed")
        else:
            print(f"⚠️ Migration output: {result.stdout}")
            print(f"⚠️ Migration errors: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ Migration check failed: {e}")


async def main():
    """Main startup function."""
    print("🚀 Starting Telegram Quiz Bot...")
    print("=" * 50)
    
    try:
        # Setup logging
        setup_logging()
        print("✅ Logging configured")
        
        # Check environment
        await check_environment()
        
        # Initialize Redis
        await initialize_redis()
        
        # Initialize database
        await initialize_database()
        
        # Run migrations
        await run_migrations()
        
        print("=" * 50)
        print("🎮 Bot initialization complete!")
        print("🚀 Starting bot...")
        print("=" * 50)
        
        # Import and start bot
        from bot.bot import main as bot_main
        await bot_main()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logging.exception("Fatal error during startup")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            await redis_client.disconnect()
            print("✅ Redis disconnected")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
