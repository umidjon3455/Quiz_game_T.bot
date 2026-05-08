"""Main bot module for the Telegram Quiz Bot."""

from .bot import bot, dp
from .loader import setup_bot

__all__ = ["bot", "dp", "setup_bot"]
