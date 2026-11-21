import tempfile
import unittest
from pathlib import Path

from bot.logging_config import prepare_log_file


class PrepareLogFileTests(unittest.TestCase):
    def test_creates_log_directory_and_returns_log_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "logs"

            log_file = Path(prepare_log_file(log_dir))

            self.assertEqual(log_file, log_dir / "bot.log")
            self.assertTrue(log_dir.is_dir())
            self.assertFalse(log_file.exists())


if __name__ == "__main__":
    unittest.main()
