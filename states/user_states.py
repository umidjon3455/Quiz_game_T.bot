"""
FSM states for user profile and settings interactions.
"""

from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """States for user profile and settings interactions."""
    
    # Profile management
    editing_profile = State()
    setting_bio = State()
    setting_username = State()
    
    # Settings management
    changing_language = State()
    toggling_notifications = State()
    toggling_sound = State()
    
    # Referral system
    entering_referral_code = State()
    viewing_referrals = State()
    
    # Daily rewards
    claiming_daily_bonus = State()
    viewing_reward_history = State()
    
    # Achievement viewing
    viewing_achievements = State()
    viewing_achievement_details = State()
    
    # Leaderboard
    viewing_leaderboard = State()
    selecting_leaderboard_type = State()
    
    # Support and feedback
    sending_feedback = State()
    contacting_support = State()
