"""
Formatting utilities for creating beautiful messages.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from models.user import User
from models.game_session import GameSession
from models.achievement import Achievement


def format_user_profile(user: User) -> str:
    """Format user profile message with modern styling."""
    
    # Create progress bar for XP
    xp_progress = format_progress_bar(user.experience, user.level * 100, 10)
    
    # Create rank emoji based on level
    rank_emoji = get_rank_emoji(user.level)
    
    profile_text = f"""
{rank_emoji} <b>{user.first_name}'s Profile</b> {rank_emoji}

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>Statistics:</b>
🎯 Level: <b>{user.level}</b> {xp_progress}
⭐ XP: <b>{user.experience}/{user.level * 100}</b>
💰 Coins: <b>{user.coins:,}</b>
🔥 Streak: <b>{user.current_streak}</b> days
🏆 Rank: <b>{user.rank}</b>

📈 <b>Performance:</b>
✅ Correct: <b>{user.correct_answers}</b>
❌ Wrong: <b>{user.wrong_answers}</b>
📊 Accuracy: <b>{user.accuracy_rate:.1f}%</b>
🎮 Games: <b>{user.total_games}</b>
⚡ Win Rate: <b>{user.win_rate:.1f}%</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━
🗓️ Joined: <b>{user.created_at.strftime('%d %b %Y')}</b>
🕐 Last Active: <b>{user.last_active.strftime('%d %b %Y, %H:%M')}</b>
    """.strip()
    
    return profile_text


def format_leaderboard(users: List[User], current_user: Optional[User] = None) -> str:
    """Format leaderboard message with rankings."""
    
    leaderboard_text = "🏆 <b>Global Leaderboard</b> 🏆\n\n"
    
    for i, user in enumerate(users[:10], 1):
        # Get medal emoji for top 3
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"#{i}"
        
        # Highlight current user
        if current_user and user.id == current_user.id:
            highlight = "👉 "
        else:
            highlight = ""
        
        username = user.username or user.first_name
        leaderboard_text += f"{highlight}{medal} {username} - Level {user.level} ({user.coins:,} coins)\n"
    
    return leaderboard_text


def format_quiz_results(session: GameSession, user: User) -> str:
    """Format quiz results message."""
    
    # Calculate performance rating
    accuracy = session.accuracy_rate
    if accuracy >= 90:
        rating = "🌟 Perfect!"
    elif accuracy >= 80:
        rating = "🔥 Excellent!"
    elif accuracy >= 70:
        rating = "👍 Great!"
    elif accuracy >= 60:
        rating = "😊 Good!"
    else:
        rating = "💪 Keep Trying!"
    
    # Create progress bar for accuracy
    accuracy_bar = format_progress_bar(accuracy, 100, 10)
    
    results_text = f"""
{rating} <b>Quiz Complete!</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>Your Results:</b>
✅ Correct: <b>{session.correct_answers}</b>
❌ Wrong: <b>{session.wrong_answers}</b>
📊 Accuracy: <b>{accuracy:.1f}%</b> {accuracy_bar}
⚡ Score: <b>{session.score}</b>
🔥 Max Combo: <b>{session.max_combo}</b>

🎁 <b>Rewards Earned:</b>
⭐ XP: <b>+{session.earned_xp}</b>
💰 Coins: <b>+{session.earned_coins}</b>

⏱️ <b>Time:</b> <b>{session.total_time} seconds</b>
🎮 <b>Mode:</b> <b>{session.game_mode.title()}</b>
    """.strip()
    
    return results_text


def format_achievement_notification(achievement: Achievement, user: User) -> str:
    """Format achievement unlock notification."""
    
    notification_text = f"""
🎉 <b>Achievement Unlocked!</b> 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━
{achievement.emoji} <b>{achievement.name}</b>

{achievement.description}

🎁 <b>Rewards:</b>
⭐ XP: <b>+{achievement.reward_xp}</b>
💰 Coins: <b>+{achievement.reward_coins}</b>

🎊 <b>Congratulations, {user.first_name}!</b>
    """.strip()
    
    return notification_text


def format_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Create a visual progress bar using emojis."""
    
    if total == 0:
        return "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️"
    
    filled = int((current / total) * length)
    empty = length - filled
    
    # Use different emojis for filled and empty
    filled_bar = "🟦" * filled
    empty_bar = "⬜" * empty
    
    return f"{filled_bar}{empty_bar} ({current}/{total})"


def get_rank_emoji(level: int) -> str:
    """Get rank emoji based on user level."""
    if level >= 100:
        return "👑"
    elif level >= 80:
        return "💎"
    elif level >= 60:
        return "🏆"
    elif level >= 40:
        return "🥇"
    elif level >= 30:
        return "🥈"
    elif level >= 20:
        return "🥉"
    elif level >= 10:
        return "🌟"
    else:
        return "🌱"


def format_category_list(categories: List[Any]) -> str:
    """Format category selection message."""
    
    categories_text = "📚 <b>Select Quiz Category</b> 📚\n\n"
    
    for category in categories:
        status = "🔒" if category.min_level > 1 else "✅"
        categories_text += f"{status} {category.emoji} {category.name}"
        
        if category.min_level > 1:
            categories_text += f" (Level {category.min_level}+)"
        
        categories_text += f"\n📝 {category.question_count} questions\n\n"
    
    return categories_text


def format_daily_bonus(streak: int, coins: int) -> str:
    """Format daily bonus notification."""
    
    # Calculate bonus multiplier
    multiplier = min(1 + (streak - 1) * 0.1, 2.0)  # Max 2x bonus
    bonus_coins = int(coins * multiplier)
    
    bonus_text = f"""
🎁 <b>Daily Bonus Claimed!</b> 🎁

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 <b>Streak: {streak} days</b>
💰 <b>Coins: +{bonus_coins:,}</b>
🎯 <b>Multiplier: {multiplier:.1f}x</b>

🎊 <b>Come back tomorrow for more!</b>
    """.strip()
    
    return bonus_text
