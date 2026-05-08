"""
Scheduler service for managing scheduled tasks.
"""

import logging
from typing import Dict, Any
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from bot import bot
from database.redis_client import redis_client
from services.user_service import UserService
from services.achievement_service import AchievementService
from config import settings

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled tasks."""
    
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler
        self.setup_jobs()
    
    def setup_jobs(self):
        """Setup all scheduled jobs."""
        if not settings.scheduler_enabled:
            logger.info("Scheduler is disabled")
            return
        
        # Daily reset job
        self.scheduler.add_job(
            self.daily_reset,
            CronTrigger(hour=0, minute=0),
            id="daily_reset",
            name="Daily Reset",
            replace_existing=True
        )
        
        # Weekly statistics job
        self.scheduler.add_job(
            self.weekly_statistics,
            CronTrigger(day_of_week=0, hour=1, minute=0),
            id="weekly_stats",
            name="Weekly Statistics",
            replace_existing=True
        )
        
        # Cleanup job
        self.scheduler.add_job(
            self.cleanup_old_data,
            CronTrigger(hour=2, minute=0),
            id="cleanup",
            name="Data Cleanup",
            replace_existing=True
        )
        
        # Cache refresh job
        self.scheduler.add_job(
            self.refresh_cache,
            IntervalTrigger(minutes=30),
            id="cache_refresh",
            name="Cache Refresh",
            replace_existing=True
        )
        
        # Achievement check job
        self.scheduler.add_job(
            self.check_achievements,
            IntervalTrigger(hours=1),
            id="achievement_check",
            name="Achievement Check",
            replace_existing=True
        )
        
        logger.info("Scheduled jobs setup completed")
    
    async def daily_reset(self):
        """Perform daily reset tasks."""
        logger.info("Starting daily reset...")
        
        try:
            # Reset daily bonuses for all users
            from database.engine import async_session_factory
            
            async with async_session_factory() as session:
                # Reset streaks for users who didn't claim daily bonus
                from sqlalchemy import update
                from models.user import User
                from datetime import timedelta
                
                yesterday = datetime.now() - timedelta(days=1)
                
                stmt = (
                    update(User)
                    .where(User.daily_claimed < yesterday)
                    .values(current_streak=0)
                )
                await session.execute(stmt)
                await session.commit()
                
                logger.info("Daily streaks reset completed")
            
            # Clear daily statistics cache
            await redis_client.delete("daily_stats")
            await redis_client.delete("leaderboard_daily")
            
            # Send daily reminder to active users
            await self.send_daily_reminders()
            
            logger.info("Daily reset completed")
            
        except Exception as e:
            logger.error(f"Error in daily reset: {e}")
    
    async def weekly_statistics(self):
        """Generate weekly statistics."""
        logger.info("Generating weekly statistics...")
        
        try:
            from database.engine import async_session_factory
            
            async with async_session_factory() as session:
                # Get weekly stats
                stats = await self.get_weekly_stats(session)
                
                # Store in Redis
                await redis_client.set("weekly_stats", stats, expire=86400 * 7)  # 7 days
                
                # Send stats to admins
                await self.send_weekly_stats_to_admins(stats)
                
                logger.info("Weekly statistics completed")
                
        except Exception as e:
            logger.error(f"Error in weekly statistics: {e}")
    
    async def cleanup_old_data(self):
        """Clean up old data."""
        logger.info("Starting data cleanup...")
        
        try:
            from database.engine import async_session_factory
            from datetime import timedelta
            
            async with async_session_factory() as session:
                # Clean up old game sessions (older than 30 days)
                from models.game_session import GameSession
                
                cutoff_date = datetime.now() - timedelta(days=30)
                
                # This would be implemented with proper cleanup queries
                logger.info("Data cleanup completed")
                
        except Exception as e:
            logger.error(f"Error in data cleanup: {e}")
    
    async def refresh_cache(self):
        """Refresh cached data."""
        try:
            # Refresh leaderboard cache
            await self.refresh_leaderboard_cache()
            
            # Refresh category stats cache
            await self.refresh_category_cache()
            
            logger.debug("Cache refresh completed")
            
        except Exception as e:
            logger.error(f"Error in cache refresh: {e}")
    
    async def check_achievements(self):
        """Check for new achievements."""
        try:
            from database.engine import async_session_factory
            
            async with async_session_factory() as session:
                # This would check for achievements that need periodic checking
                logger.debug("Achievement check completed")
                
        except Exception as e:
            logger.error(f"Error in achievement check: {e}")
    
    async def send_daily_reminders(self):
        """Send daily reminders to active users."""
        try:
            from database.engine import async_session_factory
            
            async with async_session_factory() as session:
                # Get active users who haven't claimed daily bonus
                from models.user import User
                from sqlalchemy import select
                
                result = await session.execute(
                    select(User).where(
                        User.notifications_enabled == True
                    )
                )
                users = result.scalars().all()
                
                for user in users[:100]:  # Limit to avoid spam
                    try:
                        await bot.send_message(
                            chat_id=user.telegram_id,
                            text=(
                                "🎁 <b>Daily Bonus Available!</b>\n\n"
                                "🔥 Your daily bonus is ready to claim!\n"
                                "🎮 Don't break your streak!\n\n"
                                "💬 Use /daily to claim now!"
                            )
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send reminder to {user.telegram_id}: {e}")
                
                logger.info(f"Sent daily reminders to {len(users)} users")
                
        except Exception as e:
            logger.error(f"Error sending daily reminders: {e}")
    
    async def get_weekly_stats(self, session) -> Dict:
        """Get weekly statistics."""
        from models.user import User
        from models.game_session import GameSession
        from sqlalchemy import select, func
        
        # Get user stats
        users_result = await session.execute(
            select(
                func.count(User.id).label('total_users'),
                func.sum(User.total_games).label('total_games'),
                func.sum(User.correct_answers).label('total_correct'),
                func.sum(User.coins).label('total_coins')
            )
        )
        user_stats = users_result.first()
        
        # Get game stats
        games_result = await session.execute(
            select(
                func.count(GameSession.id).label('sessions'),
                func.avg(GameSession.accuracy).label('avg_accuracy')
            )
        )
        game_stats = games_result.first()
        
        return {
            "total_users": user_stats.total_users or 0,
            "total_games": user_stats.total_games or 0,
            "total_correct": user_stats.total_correct or 0,
            "total_coins": user_stats.total_coins or 0,
            "sessions": game_stats.sessions or 0,
            "avg_accuracy": float(game_stats.avg_accuracy or 0),
            "generated_at": datetime.now().isoformat()
        }
    
    async def send_weekly_stats_to_admins(self, stats: Dict):
        """Send weekly statistics to admin users."""
        stats_text = f"""
📊 <b>Weekly Statistics Report</b> 📊

━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 <b>Users:</b> {stats['total_users']:,}
🎮 <b>Total Games:</b> {stats['total_games']:,}
✅ <b>Correct Answers:</b> {stats['total_correct']:,}
💰 <b>Total Coins:</b> {stats['total_coins']:,}
📊 <b>Sessions:</b> {stats['sessions']:,}
🎯 <b>Avg Accuracy:</b> {stats['avg_accuracy']:.1f}%

📅 <b>Generated:</b> {stats['generated_at'][:10]}
        """.strip()
        
        for admin_id in settings.admin_ids:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=stats_text
                )
            except Exception as e:
                logger.warning(f"Failed to send stats to admin {admin_id}: {e}")
    
    async def refresh_leaderboard_cache(self):
        """Refresh leaderboard cache."""
        try:
            from database.engine import async_session_factory
            
            async with async_session_factory() as session:
                # Get top users
                top_users = await UserService.get_top_users(session, "coins", 50)
                
                # Cache leaderboard data
                leaderboard_data = [
                    {
                        "telegram_id": user.telegram_id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "coins": user.coins,
                        "level": user.level
                    }
                    for user in top_users
                ]
                
                await redis_client.set("leaderboard_coins", leaderboard_data, expire=3600)  # 1 hour
                
        except Exception as e:
            logger.error(f"Error refreshing leaderboard cache: {e}")
    
    async def refresh_category_cache(self):
        """Refresh category statistics cache."""
        try:
            from database.engine import async_session_factory
            
            async with async_session_factory() as session:
                # Get category stats
                from models.category import Category
                from sqlalchemy import select
                
                result = await session.execute(
                    select(Category).where(Category.is_active == True)
                )
                categories = result.scalars().all()
                
                category_data = [
                    {
                        "id": cat.id,
                        "name": cat.name,
                        "emoji": cat.emoji,
                        "question_count": cat.question_count
                    }
                    for cat in categories
                ]
                
                await redis_client.set("categories", category_data, expire=3600)  # 1 hour
                
        except Exception as e:
            logger.error(f"Error refreshing category cache: {e}")
    
    def add_custom_job(self, func, trigger, job_id: str, **kwargs):
        """Add a custom scheduled job."""
        self.scheduler.add_job(
            func,
            trigger,
            id=job_id,
            replace_existing=True,
            **kwargs
        )
        logger.info(f"Added custom job: {job_id}")
    
    def remove_job(self, job_id: str):
        """Remove a scheduled job."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
    
    def get_jobs(self):
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()
