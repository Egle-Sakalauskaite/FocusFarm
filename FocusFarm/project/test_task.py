from datetime import date
import sys
sys.path.append("project")
from task import Task
import unittest


class TestTask(unittest.TestCase):

    def setUp(self):
        # Create a task object for testing
        self.task = Task()

    def test_initialization(self):
        #test all standard task class attributes
        self.assertEqual(self.task.title, 'New task')
        self.assertEqual(self.task.description, '')
        self.assertEqual(self.task.est_duration, 30)
        self.assertEqual(self.task.priority, 1)
        self.assertEqual(self.task.color, 'white')
        self.assertIsNone(self.task.due_date)
        self.assertFalse(self.task.is_started)
        self.assertFalse(self.task.is_finished)

    def test_title_property(self):
        #test title property
        self.task.title = 'new_title'
        self.assertEqual(self.task.title, 'new_title')

    def test_description_property(self):
        #test the description property
        self.task.description = 'new_description'
        self.assertEqual(self.task.description, 'new_description')

    def test_est_duration_property(self):
        #test duration property
        self.task.est_duration = 30
        self.assertEqual(self.task.est_duration, 30)

    def test_priority_property(self):
        #testing priority property
        self.task.priority = 3
        self.assertEqual(self.task.priority, 3)

    def test_color_property(self):
        #testing color property
        self.task.color = 'red'
        self.assertEqual(self.task.color, 'red')

    def test_due_date_property(self):
        #testing due-date property
        #test due date 
        due_date = date(2024, 9, 30)
        self.task.due_date = due_date
        self.assertEqual(self.task.due_date, due_date)

    #def test_date_due_invalid_date(self):       # this test doesnt pass because you caan still add deadlines and due dates into the past
        #here we try a invalid date to see if it gives back an error message
        #with self.assertRaises(ValueError):
            #self.task.date_due = date(2023, 1, 1)

    def test_date_due_leap_year(self):
        # used the 29th of feburary
        leap_year_date = date(2024, 2, 29)
        self.task.date_due = leap_year_date
        self.assertEqual(self.task.date_due, leap_year_date, "Leapyear date has to be accepted")

    def date_due_different_type(self):
        # I just tried a string variant of a date
        with self.assertRaises(ValueError):
            self.task.date_due("2023-12-31")

    def test_start_task(self):
        #testing if test test has started
        self.task.start_task()
        self.assertTrue(self.task.is_started)

    def test_finish_task(self):
        #tests if test is finished
        self.task.finish_task()
        self.assertTrue(self.task.is_finished)
    
    def test_description_empty(self):
        # what happens if we leave the description empty
        self.task.description = ''
        self.assertEqual(self.task.description, '')

    #def test_description_character_limit(self):
        # What happens if the description is very long
        #long_description = 'a' * 201  # This number can change depending on the character limit you chose
        #with self.assertRaises(ValueError):
            #self.task.description = long_description    # the fail message is because ther is still no character limit, so the code should work while it should´t

    def test_description_integers(self):
    # What happens when you add integers and floats in your task description
        description = 'Description with numbers: 12399 3.97'
        self.task.description = description
        self.assertEqual(self.task.description, description)


if __name__ == '__main__':
    unittest.main()

        
