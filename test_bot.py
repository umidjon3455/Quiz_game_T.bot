#!/usr/bin/env python3
"""
Test script to verify bot configuration and connections.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import settings
from database.engine import engine
from database.redis_client import redis_client


def test_config():
    """Test configuration loading."""
    print("🔧 Testing Configuration...")
    
    try:
        # Check bot token
        if settings.bot_token:
            print(f"✅ Bot Token: {'*' * 10}{settings.bot_token[-4:]}")
        else:
            print("❌ Bot Token not configured")
            return False
        
        # Check admin IDs
        if settings.admin_ids:
            print(f"✅ Admin IDs: {len(settings.admin_ids)} configured")
        else:
            print("❌ Admin IDs not configured")
            return False
        
        # Check database URL
        if settings.database_url:
            print("✅ Database URL configured")
        else:
            print("❌ Database URL not configured")
            return False
        
        # Check Redis URL
        if settings.redis_url:
            print("✅ Redis URL configured")
        else:
            print("❌ Redis URL not configured")
            return False
        
        print("✅ Configuration test passed\n")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def test_database():
    """Test database connection."""
    print("🗄️ Testing Database Connection...")
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_redis():
    """Test Redis connection."""
    print("🔴 Testing Redis Connection...")
    
    try:
        await redis_client.connect()
        await redis_client.set("test_key", "test_value", expire=10)
        value = await redis_client.get("test_key")
        await redis_client.delete("test_key")
        
        if value == "test_value":
            print("✅ Redis connection successful")
            await redis_client.disconnect()
            return True
        else:
            print("❌ Redis test failed")
            return False
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


async def test_bot():
    """Test bot connection to Telegram."""
    print("🤖 Testing Bot Connection...")
    
    try:
        from aiogram import Bot
        bot = Bot(token=settings.bot_token)
        
        # Get bot info
        bot_info = await bot.get_me()
        print(f"✅ Bot connection successful")
        print(f"🤖 Bot: @{bot_info.username}")
        print(f"📝 Name: {bot_info.first_name}")
        
        await bot.session.close()
        return True
    except Exception as e:
        print(f"❌ Bot connection failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🧪 Telegram Quiz Bot - Connection Test")
    print("=" * 50)
    
    # Test configuration
    if not test_config():
        print("\n❌ Configuration test failed. Please check your .env file.")
        sys.exit(1)
    
    # Test database
    if not await test_database():
        print("\n❌ Database test failed. Please check your database configuration.")
        sys.exit(1)
    
    # Test Redis
    if not await test_redis():
        print("\n❌ Redis test failed. Please check your Redis configuration.")
        sys.exit(1)
    
    # Test bot
    if not await test_bot():
        print("\n❌ Bot test failed. Please check your bot token.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Your bot is ready to start!")
    print("🚀 Run 'python start.py' to start the bot.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
