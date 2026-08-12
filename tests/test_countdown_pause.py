"""Regression tests for the async countdown pause during the Always-Always modal (issue #11).

Runs on the standard library only + tkinter, under a virtual display (xvfb-run).
Execute with:  xvfb-run -a python3 -m unittest discover -s tests -v
"""
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class _TickStub:
    """Minimal stand-in carrying only the state _tick needs to exercise issue #11."""

    def __init__(self, timeout=60):
        import types

        self.timeout = timeout
        self._closed = False
        self._confirming = False
        self._deadline = time.monotonic() + timeout
        self._stripe_mode = "ok"
        self.deny_calls = 0
        self.after_calls = 0

        # Fake the canvas/text widgets _tick touches.
        stripe = types.SimpleNamespace(
            coords=lambda *a: None,
            itemconfig=lambda *a, **k: None,
            tag_raise=lambda *a: None,
        )
        self.stripe = stripe
        self._stripe_w = 300
        self._stripe_cover = "cover"
        self._stripe_tint = "tint"
        self.timer_value = types.SimpleNamespace(config=lambda **k: None)

        def _after(*a):
            self.after_calls += 1

        self.root = types.SimpleNamespace(after=_after)
        self._tick = lambda: None

    def deny(self):
        self.deny_calls += 1


class CountdownPauseTest(unittest.TestCase):
    def _tick_on(self, stub):
        import src.dialogs as d

        d.ApprovalDialog._tick(stub)

    def test_no_deny_while_confirm_modal_open(self):
        """_tick must not auto-deny while _confirming is True even after deadline."""

        stub = _TickStub(timeout=1)
        stub._confirming = True
        stub._deadline = time.monotonic() - 10  # deadline long past
        self._tick_on(stub)
        self.assertEqual(stub.deny_calls, 0, "must not deny while modal is open")

    def test_denies_when_not_confirming(self):
        stub = _TickStub(timeout=1)
        stub._confirming = False
        stub._deadline = time.monotonic() - 10
        self._tick_on(stub)
        self.assertEqual(stub.deny_calls, 1, "should deny once the deadline passes")
        self.assertEqual(stub.after_calls, 0, "should stop rescheduling after deny")


if __name__ == "__main__":
    unittest.main()
