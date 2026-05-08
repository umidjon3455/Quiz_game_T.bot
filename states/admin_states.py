"""
FSM states for admin panel interactions.
"""

from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """States for admin panel interactions."""
    
    # Main admin menu
    admin_main_menu = State()
    
    # Broadcast system
    creating_broadcast = State()
    setting_broadcast_recipients = State()
    confirming_broadcast = State()
    
    # User management
    managing_users = State()
    viewing_user_details = State()
    banning_user = State()
    unbanning_user = State()
    setting_user_coins = State()
    setting_user_level = State()
    
    # Analytics and statistics
    viewing_analytics = State()
    selecting_analytics_period = State()
    exporting_statistics = State()
    
    # Content management
    managing_questions = State()
    managing_categories = State()
    managing_achievements = State()
    
    # System settings
    configuring_bot = State()
    setting_bot_tokens = State()
    configuring_rate_limits = State()
    testing_system = State()
    
    # Database operations
    database_backup = State()
    database_restore = State()
    clearing_cache = State()
    
    # Reward management
    managing_rewards = State()
    setting_daily_bonus = State()
    configuring_referral_bonus = State()
    
    # Tournament management
    creating_tournament = State()
    managing_tournament = State()
    viewing_tournament_results = State()
