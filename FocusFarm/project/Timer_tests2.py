import sys
sys.path.append("project")
from Timer_class import Timer
import unittest
from datetime import date

class TestTimer(unittest.TestCase):
    def setUp(self):
        self.timer = Timer()

    def test_invalid_stop(self):
        # Test stopping the timer without initialization
        with self.assertRaises(ValueError):
            self.timer.stop()

    def test_invalid_pause(self):
        # Test pausing the timer without initialization
        with self.assertRaises(ValueError):
            self.timer.pause()

    def test_max_duration_zero(self):
        # Test setting a max duration of 0
        self.timer.set_max_duration(0)
        self.assertIsNone(self.timer.max_duration)

    def test_short_max_duration(self):
        # Test setting a very short max duration (1 second)
        self.timer.set_max_duration(0.01667)  # 1 second in minutes
        expected_max_duration = 1
        tolerance = 0.01  # Define a small tolerance value
        self.assertAlmostEqual(self.timer.max_duration, expected_max_duration, delta=tolerance)

    def test_toggle_running(self):
        # Test toggling between running and paused states
        self.timer.start()
        self.assertTrue(self.timer.running)
        self.assertFalse(self.timer.paused)
        self.timer.toggle_running()  # Pause
        self.assertFalse(self.timer.running)
        self.assertTrue(self.timer.paused)
        self.timer.toggle_running()  # Resume
        self.assertTrue(self.timer.running)
        self.assertFalse(self.timer.paused)

    def test_elapsed_time_paused(self):
        # Test elapsed_time while paused
        self.timer.start()
        self.timer.pause()
        elapsed_time = self.timer.elapsed_time()
        self.assertEqual(elapsed_time, 0)

    def test_max_duration_reached(self):
        # Test what happens when max duration is reached
        self.timer.start()
        self.timer.set_max_duration(1)  # 1 second
        elapsed_time = self.timer.elapsed_time()
        self.assertEqual(elapsed_time, 0.0)

    def test_display_elapsed_time_format(self):
        # Test the format of the displayed elapsed time
        self.timer.start()
        self.timer.display_elapsed_time()
        # Add assertions to check the format of the printed output

    def test_boundary_conditions(self):
        # Test boundary conditions
        self.timer.start()
        elapsed_time = self.timer.elapsed_time()
        # Add assertions to check behavior as time approaches limits

if __name__ == "__main__":
    unittest.main()
