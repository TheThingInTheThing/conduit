"""Regression tests for bounded on-disk history (issue #9).

Runs on the standard library only (matches the project's zero-external-dependency
constraint). Execute with:  python3 -m unittest discover -s tests -v
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class HistoryRotationTest(unittest.TestCase):
    def setUp(self):
        import src.engine as e
        self.e = e
        self.sandbox = tempfile.mkdtemp()

    def _history_file(self):
        return os.path.join(self.sandbox, "conduit_history.jsonl")

    def test_file_grows_beyond_cap_is_trimmed(self):
        """Appending more than MAX_HISTORY_LINES entries keeps the file capped."""

        # Seed a log already far over the cap, then rotate it.
        with open(self._history_file(), "w", encoding="utf-8") as f:
            for i in range(self.e.MAX_HISTORY_LINES + 100):
                f.write(json.dumps({"n": i}) + "\n")

        self.e._rotate_history_file(self._history_file(), self.e.MAX_HISTORY_LINES)

        with open(self._history_file(), encoding="utf-8") as f:
            lines = f.read().splitlines()

        self.assertEqual(len(lines), self.e.MAX_HISTORY_LINES)
        # Most recent entries are preserved: the largest seeded n survives.
        self.assertEqual(json.loads(lines[-1])["n"], self.e.MAX_HISTORY_LINES + 99)

    def test_log_history_keeps_file_bounded(self):
        """log_history caps the on-disk file even after many calls."""
        orig_file = self.e.history_file
        try:
            self.e.history_file = self._history_file()

            for i in range(self.e.MAX_HISTORY_LINES + 50):
                self.e.log_history("rid", "sh", "cmd", "ok", "", "", 1, 0)

            with open(self._history_file(), encoding="utf-8") as f:
                lines = f.read().splitlines()
            self.assertLessEqual(len(lines), self.e.MAX_HISTORY_LINES)
        finally:
            self.e.history_file = orig_file

    def test_rotate_absent_file_is_noop(self):
        """Rotating a file that does not exist does not raise."""
        self.e._rotate_history_file(
            os.path.join(self.sandbox, "does-not-exist.jsonl"), self.e.MAX_HISTORY_LINES
        )


if __name__ == "__main__":
    unittest.main()
