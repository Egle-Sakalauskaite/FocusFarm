import sys
sys.path.append("project")
from database import Database
from task import Task
from datetime import date
import unittest


class TestDatabase(unittest.TestCase):
	def test_init_db(self):
		db_filename = 'test_database.db'
		db = Database(db_filename)
		self.assertIsNotNone(db)
		self.assertIsNotNone(db._conn)
		self.assertIsNotNone(db._cursor)
		db.create_table_todo()

		return db


	def test_add_task(self):
		db = self.test_init_db()
		test_title = 'test'
		test_description = 'test'
		test_est_duration = 10
		test_priority = 4
		test_color = 'white'
		test_due_date = date.today()
		test_progress = 0
		test_date_added = date.today()
		test_date_edited = date.today()
		test_is_started = False
		test_is_finished = False

		test_task = Task(
			title=test_title, 
			description=test_description, 
			est_duration=test_est_duration, 
			priority=test_priority,
			color=test_color,
			due_date=test_due_date,
			progress=test_progress,
			date_added=test_date_added,
			date_edited=test_date_edited,
			is_started=test_is_started,
			is_finished=test_is_finished,
			)

		self.assertIsNotNone(test_task)
		db.add_task(test_task)
		retrieved_tasks = db.retrieve_tasks()
		test_task = retrieved_tasks[0]

		self.assertEqual(test_task.title, test_title)
		self.assertEqual(test_task.description, test_description)
		self.assertEqual(test_task.est_duration, test_est_duration)
		self.assertEqual(test_task.priority, test_priority)
		self.assertEqual(test_task.color, test_color)
		self.assertEqual(test_task.due_date, test_due_date)
		self.assertEqual(test_task.progress, test_progress)
		self.assertEqual(test_task.date_added, test_date_added)
		self.assertEqual(test_task.date_edited, test_date_edited)
		self.assertEqual(test_task.is_started, test_is_started)
		self.assertEqual(test_task.is_finished, test_is_finished)
		self.assertIsNotNone(test_task.id)
	

	def test_edit_task(self):
		db = self.test_init_db()
		self.test_add_task()
		test_title = 'test2'
		test_description = 'test2'
		test_est_duration = 15
		test_priority = 3
		test_color = 'yellow'
		test_due_date = date.today()
		test_progress = 5
		test_date_added = date.today()
		test_date_edited = date.today()
		test_is_started = True
		test_is_finished = True

		test_task_2 = Task(
			title=test_title, 
			description=test_description, 
			est_duration=test_est_duration, 
			priority=test_priority,
			color=test_color,
			due_date=test_due_date,
			progress=test_progress,
			date_added=test_date_added,
			date_edited=test_date_edited,
			is_started=test_is_started,
			is_finished=test_is_finished,
			)

		retrieved_tasks = db.retrieve_tasks()
		test_task = retrieved_tasks[1]

		test_task_2.id = test_task.id

		db.edit_task(test_task_2)

		self.assertEqual(test_task_2.title, test_title)
		self.assertEqual(test_task_2.description, test_description)
		self.assertEqual(test_task_2.est_duration, test_est_duration)
		self.assertEqual(test_task_2.priority, test_priority)
		self.assertEqual(test_task_2.color, test_color)
		self.assertEqual(test_task_2.due_date, test_due_date)
		self.assertEqual(test_task_2.progress, 15)
		self.assertEqual(test_task_2.date_added, test_date_added)
		self.assertEqual(test_task_2.date_edited, test_date_edited)
		self.assertEqual(test_task_2.is_started, test_is_started)
		self.assertIsNotNone(test_task_2.id)

	
if __name__ == '__main__':
	unittest.main()



