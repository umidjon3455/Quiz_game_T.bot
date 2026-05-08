"""
Configuration settings for the Telegram Quiz Bot.
Loads environment variables and provides configuration access.
"""

import os
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    # Telegram Bot Configuration
    bot_token: str = Field(..., env="BOT_TOKEN")
    admin_ids: Union[List[int], str, int] = Field(default=[], env="ADMIN_IDS")
    
    @field_validator('admin_ids', mode='before')
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(id.strip()) for id in v.split(",")]
        elif isinstance(v, int):
            return [v]
        return v
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    postgres_user: str = Field(default="quizbot", env="POSTGRES_USER")
    postgres_password: str = Field(default="your_password_here", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="quizbot", env="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Bot Settings
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_questions_per_game: int = Field(default=20, env="MAX_QUESTIONS_PER_GAME")
    question_time_limit: int = Field(default=30, env="QUESTION_TIME_LIMIT")
    daily_bonus_coins: int = Field(default=100, env="DAILY_BONUS_COINS")
    referral_bonus: int = Field(default=50, env="REFERRAL_BONUS")
    
    # Game Configuration
    xp_per_correct_answer: int = Field(default=10, env="XP_PER_CORRECT_ANSWER")
    xp_per_streak_day: int = Field(default=5, env="XP_PER_STREAK_DAY")
    level_up_bonus: int = Field(default=500, env="LEVEL_UP_BONUS")
    achievement_bonus: int = Field(default=200, env="ACHIEVEMENT_BONUS")
    
    # Scheduler Configuration
    scheduler_enabled: bool = Field(default=True, env="SCHEDULER_ENABLED")
    daily_reset_time: str = Field(default="00:00", env="DAILY_RESET_TIME")
    
    # Security
    rate_limit_per_second: int = Field(default=5, env="RATE_LIMIT_PER_SECOND")
    rate_limit_per_minute: int = Field(default=30, env="RATE_LIMIT_PER_MINUTE")
    
    @property
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id in self.admin_ids
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for migrations."""
        return self.database_url.replace("+asyncpg", "")
    
    def get_admin_ids(self) -> List[int]:
        """Get list of admin IDs."""
        if isinstance(self.admin_ids, str):
            # Remove quotes and split by comma
            clean_ids = self.admin_ids.strip('"\'')
            return [int(id.strip()) for id in clean_ids.split(",")]
        return self.admin_ids


# Global settings instance
settings = Settings()
