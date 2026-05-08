"""
Helper functions for common operations.
"""

import random
import string
from typing import Optional, List
from datetime import datetime, timedelta

from models.user import User


def get_user_rank(level: int) -> str:
    """Get user rank based on level."""
    ranks = {
        range(1, 5): "🌱 Newbie",
        range(5, 10): "🌿 Beginner", 
        range(10, 20): "🍀 Learner",
        range(20, 30): "🌳 Intermediate",
        range(30, 40): "🌲 Advanced",
        range(40, 50): "🎯 Expert",
        range(50, 60): "⭐ Master",
        range(60, 80): "💎 Diamond",
        range(80, 100): "👑 Legend",
        range(100, 999): "🚀 Immortal"
    }
    
    for level_range, rank in ranks.items():
        if level in level_range:
            return rank
    
    return "🌱 Newbie"


def calculate_level_xp(level: int) -> int:
    """Calculate total XP needed for a specific level."""
    return level * 100


def calculate_xp_to_next_level(current_xp: int, level: int) -> int:
    """Calculate XP needed to reach next level."""
    required_xp = calculate_level_xp(level)
    return max(0, required_xp - current_xp)


def generate_referral_code(length: int = 8) -> str:
    """Generate a random referral code."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))


def escape_markdown(text: str) -> str:
    """Escape markdown special characters."""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text


def calculate_daily_bonus(streak: int, base_amount: int = 100) -> int:
    """Calculate daily bonus based on streak."""
    # 10% bonus per streak day, max 2x (100% bonus)
    multiplier = min(1.0 + (streak - 1) * 0.1, 2.0)
    return int(base_amount * multiplier)


def calculate_quiz_rewards(
    correct_answers: int,
    total_questions: int,
    difficulty: int,
    time_taken: int,
    combo: int
) -> dict:
    """Calculate quiz rewards (XP and coins)."""
    
    # Base rewards
    base_xp = correct_answers * 10
    base_coins = correct_answers * 5
    
    # Difficulty multiplier
    difficulty_multiplier = {1: 1.0, 2: 1.5, 3: 2.0}
    diff_mult = difficulty_multiplier.get(difficulty, 1.0)
    
    # Accuracy bonus
    accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    accuracy_bonus = 0
    if accuracy >= 100:
        accuracy_bonus = 50  # Perfect score bonus
    elif accuracy >= 90:
        accuracy_bonus = 30
    elif accuracy >= 80:
        accuracy_bonus = 20
    elif accuracy >= 70:
        accuracy_bonus = 10
    
    # Speed bonus (under time limit)
    speed_bonus = 0
    if time_taken > 0:
        avg_time_per_question = time_taken / total_questions
        if avg_time_per_question < 10:
            speed_bonus = 30
        elif avg_time_per_question < 15:
            speed_bonus = 20
        elif avg_time_per_question < 20:
            speed_bonus = 10
    
    # Combo bonus
    combo_bonus = combo * 5
    
    # Calculate final rewards
    final_xp = int((base_xp + accuracy_bonus + speed_bonus + combo_bonus) * diff_mult)
    final_coins = int((base_coins + (accuracy_bonus // 2) + (speed_bonus // 2) + combo_bonus) * diff_mult)
    
    return {
        "xp": final_xp,
        "coins": final_coins,
        "accuracy_bonus": accuracy_bonus,
        "speed_bonus": speed_bonus,
        "combo_bonus": combo_bonus,
        "difficulty_multiplier": diff_mult
    }


def generate_random_questions(
    available_questions: List[int],
    count: int,
    exclude: Optional[List[int]] = None
) -> List[int]:
    """Generate random question IDs excluding specified ones."""
    if exclude is None:
        exclude = []
    
    # Filter out excluded questions
    filtered_questions = [q for q in available_questions if q not in exclude]
    
    # Randomly select questions
    if len(filtered_questions) <= count:
        return filtered_questions
    else:
        return random.sample(filtered_questions, count)


def calculate_win_rate(wins: int, total_games: int) -> float:
    """Calculate win rate percentage."""
    if total_games == 0:
        return 0.0
    return (wins / total_games) * 100


def format_time_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"


def get_time_until_next_reset() -> int:
    """Get seconds until next daily reset (midnight)."""
    now = datetime.now()
    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return int((tomorrow - now).total_seconds())


def is_new_day(last_activity: datetime) -> bool:
    """Check if user's last activity was on a different day."""
    now = datetime.now()
    return last_activity.date() != now.date()


def calculate_streak_bonus(streak: int) -> int:
    """Calculate streak bonus multiplier."""
    if streak >= 30:
        return 2  # 2x bonus for 30+ day streak
    elif streak >= 14:
        return 1.5  # 1.5x bonus for 14+ day streak
    elif streak >= 7:
        return 1.25  # 1.25x bonus for 7+ day streak
    else:
        return 1.0  # No bonus


def get_random_emoji() -> str:
    """Get a random celebration emoji."""
    emojis = ["🎉", "🎊", "🎈", "🎁", "🌟", "✨", "🎯", "🏆", "🥇", "👏"]
    return random.choice(emojis)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
