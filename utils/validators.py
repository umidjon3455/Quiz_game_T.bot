"""
Validation utilities for input validation and sanitization.
"""

import re
from typing import Dict, Any, List, Optional


def validate_username(username: str) -> bool:
    """Validate Telegram username format."""
    if not username:
        return False
    
    # Username should be 5-32 characters, letters, numbers, underscores
    pattern = r'^[a-zA-Z0-9_]{5,32}$'
    return bool(re.match(pattern, username))


def validate_referral_code(code: str) -> bool:
    """Validate referral code format."""
    if not code:
        return False
    
    # Referral code should be 8-16 characters, alphanumeric
    pattern = r'^[a-zA-Z0-9]{8,16}$'
    return bool(re.match(pattern, code))


def validate_question_data(question_data: Dict[str, Any]) -> List[str]:
    """Validate quiz question data and return list of errors."""
    errors = []
    
    # Check required fields
    required_fields = ['question_text', 'options', 'correct_answer', 'category_id']
    for field in required_fields:
        if field not in question_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate question text
    if 'question_text' in question_data:
        question_text = question_data['question_text']
        if not question_text or len(question_text.strip()) < 5:
            errors.append("Question text must be at least 5 characters")
        elif len(question_text) > 1000:
            errors.append("Question text too long (max 1000 characters)")
    
    # Validate options
    if 'options' in question_data:
        options = question_data['options']
        if not isinstance(options, list):
            errors.append("Options must be a list")
        elif len(options) < 2:
            errors.append("At least 2 options required")
        elif len(options) > 10:
            errors.append("Too many options (max 10)")
        else:
            for i, option in enumerate(options):
                if not option or len(option.strip()) < 1:
                    errors.append(f"Option {i+1} cannot be empty")
                elif len(option) > 100:
                    errors.append(f"Option {i+1} too long (max 100 characters)")
    
    # Validate correct answer
    if 'correct_answer' in question_data and 'options' in question_data:
        correct_answer = question_data['correct_answer']
        options = question_data['options']
        
        if not isinstance(correct_answer, int):
            errors.append("Correct answer must be an integer")
        elif correct_answer < 0 or correct_answer >= len(options):
            errors.append("Correct answer index out of range")
    
    # Validate difficulty
    if 'difficulty' in question_data:
        difficulty = question_data['difficulty']
        if not isinstance(difficulty, int) or difficulty not in [1, 2, 3]:
            errors.append("Difficulty must be 1 (Easy), 2 (Medium), or 3 (Hard)")
    
    # Validate time limit
    if 'time_limit' in question_data:
        time_limit = question_data['time_limit']
        if not isinstance(time_limit, int) or time_limit < 5 or time_limit > 120:
            errors.append("Time limit must be between 5 and 120 seconds")
    
    return errors


def validate_category_data(category_data: Dict[str, Any]) -> List[str]:
    """Validate category data and return list of errors."""
    errors = []
    
    # Check required fields
    required_fields = ['name']
    for field in required_fields:
        if field not in category_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate name
    if 'name' in category_data:
        name = category_data['name']
        if not name or len(name.strip()) < 2:
            errors.append("Category name must be at least 2 characters")
        elif len(name) > 50:
            errors.append("Category name too long (max 50 characters)")
    
    # Validate description
    if 'description' in category_data:
        description = category_data['description']
        if description and len(description) > 200:
            errors.append("Description too long (max 200 characters)")
    
    # Validate emoji
    if 'emoji' in category_data:
        emoji = category_data['emoji']
        if emoji and len(emoji) > 2:
            errors.append("Emoji must be 1-2 characters")
    
    # Validate min_level
    if 'min_level' in category_data:
        min_level = category_data['min_level']
        if not isinstance(min_level, int) or min_level < 1 or min_level > 100:
            errors.append("Minimum level must be between 1 and 100")
    
    return errors


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize text input by removing potentially harmful content."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove potentially harmful characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()


def validate_user_input(text: str, input_type: str = "general") -> Dict[str, Any]:
    """Validate user input based on type."""
    result = {
        "valid": True,
        "sanitized": sanitize_text(text),
        "errors": []
    }
    
    if input_type == "username":
        if not validate_username(result["sanitized"]):
            result["valid"] = False
            result["errors"].append("Invalid username format")
    
    elif input_type == "bio":
        if len(result["sanitized"]) > 150:
            result["valid"] = False
            result["errors"].append("Bio too long (max 150 characters)")
    
    elif input_type == "referral_code":
        if not validate_referral_code(result["sanitized"]):
            result["valid"] = False
            result["errors"].append("Invalid referral code format")
    
    return result
