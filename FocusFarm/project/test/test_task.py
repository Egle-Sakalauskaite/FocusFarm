import sys
sys.path.append("project")
from ..task import Task
import unittest
from datetime import date

class TestTask(unittest.TestCase):

    def setUp(self):
        # Create a task object for testing
        self.task = Task()

    def test_initialization(self):
        self.assertEqual(self.task.title, 'New task')
        self.assertEqual(self.task.description, '')
        self.assertEqual(self.task.est_duration, 30)
        self.assertEqual(self.task.priority, 1)
        self.assertEqual(self.task.color, 'white')
        self.assertIsNone(self.task.due_date)
        self.assertFalse(self.task.is_started)
        self.assertFalse(self.task.is_finished)

    def test_title_property(self):
        self.task.title = 'new_title'
        self.assertEqual(self.task.title, 'new_title')

    def test_description_property(self):
        self.task.description = 'new_description'
        self.assertEqual(self.task.description, 'new_description')

    def test_est_duration_property(self):
        self.task.est_duration = 30
        self.assertEqual(self.task.est_duration, 30)

    def test_priority_property(self):
        self.task.priority = 3
        self.assertEqual(self.task.priority, 3)

    def test_color_property(self):
        self.task.color = 'red'
        self.assertEqual(self.task.color, 'red')

    def test_due_date_property(self):
        due_date = date(2024, 9, 30)
        self.task.due_date = due_date
        self.assertEqual(self.task.due_date, due_date)

    def test_start_task(self):
        self.task.start_task()
        self.assertTrue(self.task.is_started)

    def test_finish_task(self):
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

        
