"""
Quiz game handlers for managing quiz sessions and questions.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from models.user import User
from models.question import Question, Difficulty
from models.category import Category
from models.game_session import GameSession, GameMode, GameStatus
from states.quiz_states import QuizStates
from utils.formatters import format_quiz_results, format_progress_bar, get_rank_emoji
from utils.helpers import calculate_quiz_rewards, generate_random_questions
from keyboards.main_menu import get_quiz_modes_keyboard, get_difficulty_keyboard, get_category_keyboard
from keyboards.quiz_keyboard import (
    get_question_count_keyboard, 
    get_quiz_answer_keyboard,
    get_quiz_results_keyboard,
    get_quiz_confirmation_keyboard
)
from config import settings

logger = logging.getLogger(__name__)

router = Router()


class QuizFlow:
    """Quiz flow state management."""
    
    def __init__(self):
        self.active_quizzes: Dict[int, Dict] = {}
    
    def start_quiz(self, user_id: int, config: Dict) -> Dict:
        """Start a new quiz session."""
        quiz_data = {
            'user_id': user_id,
            'config': config,
            'current_question': 0,
            'correct_answers': 0,
            'wrong_answers': 0,
            'score': 0,
            'combo': 0,
            'max_combo': 0,
            'start_time': datetime.now(),
            'questions': [],
            'answers': [],
            'time_per_question': []
        }
        
        self.active_quizzes[user_id] = quiz_data
        return quiz_data
    
    def get_quiz(self, user_id: int) -> Optional[Dict]:
        """Get active quiz data."""
        return self.active_quizzes.get(user_id)
    
    def end_quiz(self, user_id: int) -> Optional[Dict]:
        """End quiz and return results."""
        quiz_data = self.active_quizzes.pop(user_id, None)
        if quiz_data:
            quiz_data['end_time'] = datetime.now()
            quiz_data['total_time'] = int((quiz_data['end_time'] - quiz_data['start_time']).total_seconds())
        return quiz_data


quiz_flow = QuizFlow()


@router.callback_query(F.data == "play_quiz")
async def handle_play_quiz(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handle quiz play button."""
    
    await callback.answer()
    
    await callback.message.edit_text(
        "🎮 <b>Select Quiz Mode</b>\n\n"
        "Choose your preferred game mode:",
        reply_markup=get_quiz_modes_keyboard()
    )


@router.callback_query(F.data.startswith("quiz_mode_"))
async def handle_quiz_mode_selection(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handle quiz mode selection."""
    
    mode = callback.data.split("_")[-1]
    
    await state.update_data(quiz_mode=mode)
    await callback.answer()
    
    # Show difficulty selection
    await callback.message.edit_text(
        "🎯 <b>Select Difficulty</b>\n\n"
        "Choose your difficulty level:",
        reply_markup=get_difficulty_keyboard()
    )


@router.callback_query(F.data.startswith("quiz_difficulty_"))
async def handle_difficulty_selection(
    callback: types.CallbackQuery, 
    state: FSMContext,
    db_session: AsyncSession
) -> None:
    """Handle difficulty selection and show categories."""
    
    difficulty_str = callback.data.split("_")[-1]
    
    # Convert difficulty to integer
    if difficulty_str == "random":
        difficulty = None
    else:
        difficulty = int(difficulty_str)
    
    await state.update_data(difficulty=difficulty)
    await callback.answer()
    
    # Get available categories
    result = await db_session.execute(
        select(Category).where(Category.is_active == True).order_by(Category.name)
    )
    categories = result.scalars().all()
    
    if not categories:
        await callback.message.edit_text(
            "❌ <b>No categories available</b>\n\n"
            "Please try again later.",
            reply_markup=get_quiz_modes_keyboard()
        )
        return
    
    # Get user level for category filtering
    user_id = callback.from_user.id
    user_result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = user_result.scalar_one_or_none()
    
    user_level = user.level if user else 1
    
    await callback.message.edit_text(
        "📚 <b>Select Category</b>\n\n"
        "Choose a category for your quiz:",
        reply_markup=get_category_keyboard(categories, user_level)
    )


@router.callback_query(F.data.startswith("quiz_category_"))
async def handle_category_selection(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_session: AsyncSession
) -> None:
    """Handle category selection and show question count options."""
    
    category_id = int(callback.data.split("_")[-1])
    
    # Get category details
    result = await db_session.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        await callback.answer("❌ Category not found", show_alert=True)
        return
    
    await state.update_data(category_id=category_id)
    await callback.answer()
    
    # Show question count selection
    await callback.message.edit_text(
        f"📊 <b>Select Question Count</b>\n\n"
        f"Category: {category.emoji} {category.name}\n"
        f"Available questions: {category.question_count}\n\n"
        "How many questions would you like to answer?",
        reply_markup=get_question_count_keyboard()
    )


@router.callback_query(F.data.startswith("quiz_count_"))
async def handle_question_count_selection(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_session: AsyncSession
) -> None:
    """Handle question count selection and start quiz."""
    
    count_str = callback.data.split("_")[-1]
    
    if count_str == "endless":
        question_count = 999  # Large number for endless mode
    elif count_str == "random":
        question_count = None  # Will be set randomly
    else:
        question_count = int(count_str)
    
    # Get quiz configuration
    data = await state.get_data()
    quiz_config = {
        'mode': data.get('quiz_mode', 'classic'),
        'difficulty': data.get('difficulty'),
        'category_id': data.get('category_id'),
        'question_count': question_count
    }
    
    await callback.answer()
    
    # Start quiz
    await start_quiz_session(callback, state, db_session, quiz_config)


async def start_quiz_session(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_session: AsyncSession,
    quiz_config: Dict
) -> None:
    """Start the actual quiz session."""
    
    user_id = callback.from_user.id
    
    # Get category and questions
    result = await db_session.execute(
        select(Category).where(Category.id == quiz_config['category_id'])
    )
    category = result.scalar_one_or_none()
    
    if not category:
        await callback.message.edit_text("❌ Category not found")
        return
    
    # Get questions for the category
    query = select(Question).where(
        and_(
            Question.category_id == quiz_config['category_id'],
            Question.is_active == True
        )
    )
    
    # Filter by difficulty if specified
    if quiz_config['difficulty']:
        query = query.where(Question.difficulty == quiz_config['difficulty'])
    
    result = await db_session.execute(query)
    questions = result.scalars().all()
    
    if not questions:
        await callback.message.edit_text(
            "❌ <b>No questions available</b>\n\n"
            "This category has no active questions.",
            reply_markup=get_quiz_modes_keyboard()
        )
        return
    
    # Determine question count
    if quiz_config['question_count'] is None:
        # Random count between 5 and 15
        import random
        question_count = random.randint(5, min(15, len(questions)))
    elif quiz_config['question_count'] == 999:
        # Endless mode - use all available questions
        question_count = len(questions)
    else:
        question_count = min(quiz_config['question_count'], len(questions))
    
    # Select random questions
    question_ids = [q.id for q in questions]
    selected_question_ids = generate_random_questions(question_ids, question_count)
    
    # Get selected questions
    result = await db_session.execute(
        select(Question).where(Question.id.in_(selected_question_ids))
    )
    selected_questions = result.scalars().all()
    
    # Start quiz flow
    quiz_data = quiz_flow.start_quiz(user_id, quiz_config)
    quiz_data['questions'] = selected_questions
    quiz_data['total_questions'] = len(selected_questions)
    
    # Create game session in database
    user_result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = user_result.scalar_one_or_none()
    
    game_session = GameSession(
        user_id=user.id,
        category_id=quiz_config['category_id'],
        game_mode=quiz_config['mode'],
        difficulty=quiz_config['difficulty'] or 1,
        max_questions=len(selected_questions),
        time_per_question=30,
        questions_asked=selected_question_ids
    )
    
    db_session.add(game_session)
    await db_session.commit()
    await db_session.refresh(game_session)
    
    quiz_data['session_id'] = game_session.id
    
    # Start with first question
    await show_question(callback, state, db_session, quiz_data)


async def show_question(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_session: AsyncSession,
    quiz_data: Dict
) -> None:
    """Show current question to user."""
    
    current_index = quiz_data['current_question']
    
    if current_index >= len(quiz_data['questions']):
        # Quiz completed
        await finish_quiz(callback, state, db_session, quiz_data)
        return
    
    question = quiz_data['questions'][current_index]
    question_number = current_index + 1
    
    # Format question text
    question_text = f"""
🧠 <b>Question {question_number}/{quiz_data['total_questions']}</b>

{question.question_text}

⏱️ <b>Time Limit: {question.time_limit} seconds</b>
🎯 <b>Difficulty: {question.difficulty_name}</b>
💎 <b>Points: {question.points}</b>
    """.strip()
    
    # Create answer keyboard
    keyboard = get_quiz_answer_keyboard(
        question.options,
        question_number,
        quiz_data['total_questions'],
        question.time_limit
    )
    
    await callback.message.edit_text(
        question_text,
        reply_markup=keyboard
    )
    
    # Start timer for this question
    asyncio.create_task(question_timer(callback, state, quiz_data, question.time_limit))


async def question_timer(
    callback: types.CallbackQuery,
    state: FSMContext,
    quiz_data: Dict,
    time_limit: int
) -> None:
    """Handle question timer."""
    
    user_id = callback.from_user.id
    
    # Wait for time limit
    await asyncio.sleep(time_limit)
    
    # Check if quiz is still active and question hasn't been answered
    current_quiz = quiz_flow.get_quiz(user_id)
    if current_quiz and current_quiz['current_question'] == quiz_data['current_question']:
        # Time's up - mark as wrong answer
        await handle_answer_timeout(callback, state, db_session, quiz_data)


async def handle_answer_timeout(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_session: AsyncSession,
    quiz_data: Dict
) -> None:
    """Handle timeout for question."""
    
    quiz_data['wrong_answers'] += 1
    quiz_data['combo'] = 0
    
    # Update database session
    await update_game_session(db_session, quiz_data)
    
    # Show timeout message
    await callback.message.edit_text(
        f"⏰ <b>Time's Up!</b>\n\n"
        f"The correct answer was: <b>{quiz_data['questions'][quiz_data['current_question']].options[quiz_data['questions'][quiz_data['current_question']].correct_answer]}</b>\n\n"
        f"⏭️ Moving to next question...",
        reply_markup=None
    )
    
    # Move to next question after delay
    await asyncio.sleep(2)
    quiz_data['current_question'] += 1
    await show_question(callback, state, db_session, quiz_data)


@router.callback_query(F.data.startswith("quiz_answer_"))
async def handle_answer_selection(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_session: AsyncSession
) -> None:
    """Handle answer selection."""
    
    answer_index = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    
    quiz_data = quiz_flow.get_quiz(user_id)
    if not quiz_data:
        await callback.answer("❌ Quiz not found", show_alert=True)
        return
    
    current_question = quiz_data['questions'][quiz_data['current_question']]
    is_correct = answer_index == current_question.correct_answer
    
    # Record answer
    quiz_data['answers'].append(answer_index)
    
    if is_correct:
        quiz_data['correct_answers'] += 1
        quiz_data['score'] += current_question.points
        quiz_data['combo'] += 1
        quiz_data['max_combo'] = max(quiz_data['max_combo'], quiz_data['combo'])
        
        result_text = f"✅ <b>Correct!</b>\n\n"
        result_text += f"🎯 +{current_question.points} points\n"
        result_text += f"🔥 Combo: {quiz_data['combo']}\n"
        
        if quiz_data['combo'] > 1:
            combo_bonus = quiz_data['combo'] * 5
            quiz_data['score'] += combo_bonus
            result_text += f"💫 Combo Bonus: +{combo_bonus}\n"
    else:
        quiz_data['wrong_answers'] += 1
        quiz_data['combo'] = 0
        
        correct_answer = current_question.options[current_question.correct_answer]
        result_text = f"❌ <b>Wrong!</b>\n\n"
        result_text += f"💡 Correct answer: <b>{correct_answer}</b>\n"
    
    # Add explanation if available
    if current_question.explanation:
        result_text += f"\n💬 <b>Explanation:</b> {current_question.explanation}"
    
    # Update database session
    await update_game_session(db_session, quiz_data)
    
    await callback.answer()
    
    # Show result
    await callback.message.edit_text(result_text)
    
    # Move to next question after delay
    await asyncio.sleep(3)
    quiz_data['current_question'] += 1
    await show_question(callback, state, db_session, quiz_data)


@router.callback_query(F.data == "quiz_end")
async def handle_quiz_end(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_session: AsyncSession
) -> None:
    """Handle manual quiz end."""
    
    user_id = callback.from_user.id
    quiz_data = quiz_flow.end_quiz(user_id)
    
    if not quiz_data:
        await callback.answer("❌ No active quiz", show_alert=True)
        return
    
    await callback.answer()
    
    # Finish quiz with current results
    await finish_quiz(callback, state, db_session, quiz_data)


@router.callback_query(F.data == "quiz_skip")
async def handle_quiz_skip(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_session: AsyncSession
) -> None:
    """Handle skipping current question."""
    
    user_id = callback.from_user.id
    quiz_data = quiz_flow.get_quiz(user_id)
    
    if not quiz_data:
        await callback.answer("❌ Quiz not found", show_alert=True)
        return
    
    quiz_data['wrong_answers'] += 1
    quiz_data['combo'] = 0
    
    await update_game_session(db_session, quiz_data)
    await callback.answer()
    
    # Move to next question
    quiz_data['current_question'] += 1
    await show_question(callback, state, db_session, quiz_data)


async def update_game_session(db_session: AsyncSession, quiz_data: Dict) -> None:
    """Update game session in database."""
    
    session_id = quiz_data.get('session_id')
    if not session_id:
        return
    
    result = await db_session.execute(
        select(GameSession).where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if session:
        session.current_question = quiz_data['current_question'] + 1
        session.correct_answers = quiz_data['correct_answers']
        session.wrong_answers = quiz_data['wrong_answers']
        session.score = quiz_data['score']
        session.combo = quiz_data['combo']
        session.max_combo = quiz_data['max_combo']
        session.answers_given = quiz_data['answers']
        
        await db_session.commit()


async def finish_quiz(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_session: AsyncSession,
    quiz_data: Dict
) -> None:
    """Finish quiz and show results."""
    
    user_id = callback.from_user.id
    
    # Calculate rewards
    rewards = calculate_quiz_rewards(
        quiz_data['correct_answers'],
        quiz_data['total_questions'],
        quiz_data['config']['difficulty'] or 1,
        quiz_data.get('total_time', 0),
        quiz_data['max_combo']
    )
    
    # Update user stats
    user_result = await db_session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = user_result.scalar_one_or_none()
    
    if user:
        user.experience += rewards['xp']
        user.coins += rewards['coins']
        user.total_games += 1
        user.correct_answers += quiz_data['correct_answers']
        user.wrong_answers += quiz_data['wrong_answers']
        user.last_active = datetime.now()
        
        # Check for level up
        if user.is_level_up_ready:
            user.level += 1
            user.experience -= user.level * 100 - 100  # Subtract XP for new level
            user.coins += settings.level_up_bonus
        
        await db_session.commit()
    
    # Update game session
    await update_game_session(db_session, quiz_data)
    
    # Finalize session
    session_id = quiz_data.get('session_id')
    if session_id:
        result = await db_session.execute(
            select(GameSession).where(GameSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if session:
            session.status = GameStatus.COMPLETED.value
            session.completed_at = datetime.now()
            session.total_time = quiz_data.get('total_time', 0)
            session.accuracy = (quiz_data['correct_answers'] / quiz_data['total_questions']) * 100 if quiz_data['total_questions'] > 0 else 0
            session.earned_xp = rewards['xp']
            session.earned_coins = rewards['coins']
            
            await db_session.commit()
    
    # Show results
    await show_quiz_results(callback, quiz_data, rewards, user)


async def show_quiz_results(
    callback: types.CallbackQuery,
    quiz_data: Dict,
    rewards: Dict,
    user: Optional[User]
) -> None:
    """Show quiz results to user."""
    
    accuracy = (quiz_data['correct_answers'] / quiz_data['total_questions']) * 100 if quiz_data['total_questions'] > 0 else 0
    
    results_text = f"""
🎉 <b>Quiz Complete!</b> 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>Your Results:</b>
✅ Correct: <b>{quiz_data['correct_answers']}</b>
❌ Wrong: <b>{quiz_data['wrong_answers']}</b>
📊 Accuracy: <b>{accuracy:.1f}%</b>
⚡ Score: <b>{quiz_data['score']}</b>
🔥 Max Combo: <b>{quiz_data['max_combo']}</b>

🎁 <b>Rewards Earned:</b>
⭐ XP: <b>+{rewards['xp']}</b>
💰 Coins: <b>+{rewards['coins']}</b>

⏱️ <b>Time:</b> <b>{quiz_data.get('total_time', 0)} seconds</b>
🎮 <b>Mode:</b> <b>{quiz_data['config']['mode'].title()}</b>
    """.strip()
    
    if user and user.is_level_up_ready:
        results_text += f"\n\n🎊 <b>LEVEL UP!</b> 🎊\n🌟 You're now level <b>{user.level}</b>!"
    
    keyboard = get_quiz_results_keyboard(quiz_data)
    
    await callback.message.edit_text(results_text, reply_markup=keyboard)


@router.callback_query(F.data == "quiz_play_again")
async def handle_play_again(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handle play again button."""
    
    await callback.answer()
    
    # Reset state and start new quiz
    await state.clear()
    
    await callback.message.edit_text(
        "🎮 <b>Select Quiz Mode</b>\n\n"
        "Choose your preferred game mode:",
        reply_markup=get_quiz_modes_keyboard()
    )
