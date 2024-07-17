import sys
sys.path.append("project")
from ..Timer_class import Timer
import unittest
from datetime import date

class TestTimer(unittest.TestCase):
    def setUp(self):
        self.timer = Timer()

    def test_start(self):
        self.timer.start()
        self.assertTrue(self.timer.running)

    def test_pause(self):
        self.timer.start()
        self.timer.pause()
        self.assertFalse(self.timer.running)
        self.assertTrue(self.timer.paused)

    def test_resume_after_pause(self):
        self.timer.start()
        self.timer.pause()
        self.timer.start()
        self.assertTrue(self.timer.running)
        self.assertFalse(self.timer.paused)

    def test_stop(self):
        self.timer.start()
        self.timer.stop()
        self.assertFalse(self.timer.running)
        self.assertIsNotNone(self.timer.end_time)

    def test_elapsed_time(self):
        self.timer.start()
        elapsed_time = self.timer.elapsed_time()
        self.assertGreaterEqual(elapsed_time, 0)

    def test_max_duration(self):
        self.timer.set_max_duration(10)  # Set max duration to 10 minutes
        self.assertEqual(self.timer.max_duration, 600)  # 10 minutes in seconds

    def test_get_timer_value(self):
        self.timer.start()
        timer_value = self.timer.get_timer_value()
        self.assertTrue(timer_value)

    def test_display_elapsed_time(self):
        self.timer.start()
        self.timer.display_elapsed_time()
        # It's challenging to test the display function, so you may want to add a print statement for manual testing.

if __name__ == "__main__":
    unittest.main()
