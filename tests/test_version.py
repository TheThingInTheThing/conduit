"""Regression test: every surface reports the same version (single source of truth).

Runs on the standard library only (matches the project's zero-external-dependency
constraint). Execute with:  python3 -m unittest discover -s tests -v
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class VersionConsistencyTest(unittest.TestCase):
    def test_single_source_of_truth(self):
        import src as package
        import src.mcp_server as m
        self.assertEqual(package.__version__, m.SERVER_VERSION)
        # The CLI banner imports the same package __version__.
        self.assertEqual(package.__version__, "2.2.0")


if __name__ == "__main__":
    unittest.main()
