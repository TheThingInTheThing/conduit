"""Regression tests for session persistence (atomic write).

Runs on the standard library only (matches the project's zero-external-dependency
constraint). Execute with:  python3 -m unittest discover -s tests -v
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SessionAtomicWriteTest(unittest.TestCase):
    def setUp(self):
        import src.session as s
        self.s = s
        self.sandbox = tempfile.mkdtemp()
        self._orig_dir, self._orig_file = s.SESSION_DIR, s.SESSION_FILE
        s.SESSION_DIR = self.sandbox
        s.SESSION_FILE = os.path.join(self.sandbox, "session.json")

    def tearDown(self):
        import src.session as s
        s.SESSION_DIR, s.SESSION_FILE = self._orig_dir, self._orig_file

    def test_write_read_roundtrip(self):
        self.assertTrue(self.s.write_session("tok123", "127.0.0.1", 40404))
        d = self.s.read_session()
        self.assertEqual(d["token"], "tok123")
        self.assertEqual(d["port"], 40404)

    def test_rewrite_reflects_new_values(self):
        self.assertTrue(self.s.write_session("old", "127.0.0.1", 40404))
        self.assertTrue(self.s.write_session("new", "0.0.0.0", 9999))
        d = self.s.read_session()
        self.assertEqual(d["token"], "new")
        self.assertEqual(d["port"], 9999)

    def test_no_temp_litter_and_valid_json(self):
        self.assertTrue(self.s.write_session("tok456", "127.0.0.1", 40404))
        leftovers = [f for f in os.listdir(self.sandbox) if f.endswith(".tmp")]
        self.assertEqual(leftovers, [])
        with open(self.s.SESSION_FILE, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["token"], "tok456")

    def test_read_returns_none_when_absent(self):
        # No write happened -> no session file -> None
        self.assertIsNone(self.s.read_session())


if __name__ == "__main__":
    unittest.main()
