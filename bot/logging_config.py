"""Filesystem helpers for bot logging."""

from pathlib import Path


def prepare_log_file(log_dir: Path | None = None) -> str:
    """Create the log directory and return the bot log file path."""
    directory = log_dir or Path(__file__).resolve().parent.parent / "logs"
    directory.mkdir(parents=True, exist_ok=True)
    return str(directory / "bot.log")
