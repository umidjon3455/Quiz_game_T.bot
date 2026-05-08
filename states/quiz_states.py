"""
FSM states for quiz game interactions.
"""

from aiogram.fsm.state import State, StatesGroup


class QuizStates(StatesGroup):
    """States for quiz game interactions."""
    
    # Main quiz states
    choosing_category = State()
    choosing_difficulty = State()
    choosing_game_mode = State()
    
    # Active game states
    answering_question = State()
    viewing_results = State()
    
    # Question management (admin)
    adding_question = State()
    editing_question = State()
    setting_question_options = State()
    setting_correct_answer = State()
    
    # Category management
    adding_category = State()
    editing_category = State()
    
    # Game settings
    setting_time_limit = State()
    setting_question_count = State()
