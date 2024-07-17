import sys
sys.path.append("project")
from task import Task
from datetime import datetime, date
import sqlite3
import os

import random

class Database:
	'''This class is used to create SQLite3 database files and manage inormation stored in them'''

	def __init__(self, filename: str) -> None:
		'''Creates a SQLite database if it does not exist and store it in the project folder'''
		project_folder = os.path.dirname(__file__)
		db_path = os.path.join(project_folder, filename)
		self.filename = db_path
		conn = sqlite3.connect(self.filename)
		cursor = conn.cursor()
		

		self._conn = conn
		self._cursor = cursor

	def create_table_todo(self) -> None:
		'''creates the tasks table if it doesn't exist already'''
		table_sql = '''
		    CREATE TABLE IF NOT EXISTS todo (
		        id INTEGER PRIMARY KEY,
		        title TEXT NOT NULL,
		        description TEXT,
		        estimated_duration INTEGER,
		        priority_level INTEGER,
		        color_code TEXT,
		        due_date DATE,
				progress INTEGER,
		        date_added DATE,
		        date_edited DATE,
		        is_started BOOL,
		        is_finished BOOL
		    )
		'''
		self._cursor.execute(table_sql)
		self._conn.commit()

	def create_table_user_settings(self) -> None:
		'''creates the user settings table if it doesn't exist already'''
		table_sql = '''
			CREATE TABLE IF NOT EXISTS UserSettings (
			id INTEGER PRIMARY KEY,
		    map_seed INTEGER,
		    nature_points INTEGER,
		    user_points_trend INTEGER
		); 
		'''

		self._cursor.execute(table_sql)
		self._conn.commit()

		# initial user data
		initial_points = 5
		initial_points_trend = 0
		map_seed = random.randint(1, 1000)
		sql_initial_data = '''
			INSERT INTO UserSettings (map_seed, nature_points, user_points_trend) VALUES (?, ?, ?);
			'''

		# select first row
		self._cursor.execute("SELECT * FROM UserSettings")

		# Check if any rows are returned
		# to see if initial user data was already added
		if self._cursor.fetchone() is None:
			# Insert initial data
			self._cursor.execute(sql_initial_data, (map_seed, initial_points, initial_points_trend))
			self._conn.commit()


	def create_table_characters(self) -> None:
		'''creates the characters table if it doesn't exist already'''
		table_sql = '''
		    CREATE TABLE IF NOT EXISTS todo (
		        id INTEGER PRIMARY KEY AUTOINCREMENT,
		        x_pos INTEGER,
		        y_pos INTEGER,
		        name TEXT,
		        state TEXT,
		        animation_num INTEGER,
		        orientation TEXT,
		        move_time INTEGER
		    )
		'''
		self._cursor.execute(table_sql)
		self._conn.commit()

	def add_task(self, task: Task) -> None:
		'''Adds a new task to the database'''
		task_tup = (task.title,
			  			task.description,
						task.est_duration,
						task.priority,
						task.color,
						task.due_date,
						task.progress,
						date.today(),
						task.date_edited,
						task.is_started,
						task.is_finished)

		sql_insert_cmd = '''
		    INSERT INTO todo 
		    	(title,
		        description,
		        estimated_duration,
		        priority_level,
		        color_code,
		        due_date,
				progress,
		        date_added,
		        date_edited,
		        is_started,
		        is_finished)
		    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		'''

		self._cursor.execute(sql_insert_cmd, task_tup)
		self._conn.commit()


	def delete_task(self, task: Task) -> None:
		'''Deletes the specified task from the database'''
		self._cursor.execute("DELETE FROM todo WHERE id = ?", (task.id,))
		self._conn.commit()

	def edit_task(self, task: Task) -> None:
		'''Updates the data of an existing task in the database'''
		task_tup = (task.title,
			  			task.description,
						task.est_duration,
						task.priority,
						task.color,
						task.due_date,
						task.progress,
						task.date_added,
						date.today(),
						task.is_started,
						task.is_finished,
						task.id)

		sql = """
			UPDATE todo
			SET title = ?,
				description = ?,
				estimated_duration = ?,
				priority_level = ?,
				color_code = ?,
				due_date = ?,
				progress = ?,
				date_added = ?,
				date_edited = ?,
				is_started = ?,
				is_finished = ?
			WHERE id = ?
		"""
		self._cursor.execute(sql, task_tup)
		self._conn.commit()

	def retrieve_tasks(self) -> list[Task]:
		'''Returns a list of tasks that are stored in the database'''
		# Execute a SELECT statement to retrieve all tasks
		self._cursor.execute('SELECT * FROM todo')
		# Fetch all the rows as a list of tuples
		rows = self._cursor.fetchall()

		tasks = []

		# Iterate through the rows and create task objects
		for row in rows:
			#converting dates stored as strings into date objects
			due_date = row[6]
			if due_date:
				due_date = datetime.strptime(due_date, '%Y-%m-%d').date()

			date_added = datetime.strptime(row[8], '%Y-%m-%d').date()
			date_edited = datetime.strptime(row[9], '%Y-%m-%d').date()

			task = Task(id=row[0],
			   				title=row[1], 
		    				description=row[2], 
		    				est_duration=row[3], 
		    				priority=row[4],
		    				color=row[5],
		    				due_date=due_date,
							progress=row[7],
		    				date_added=date_added,
		    				date_edited=date_edited,
		    				is_started=row[10],
		    				is_finished=row[11])
			tasks.append(task)

		return tasks


	def get_user_data(self):
		sql_get = '''SELECT * FROM UserSettings;'''

		self._cursor.execute(sql_get)

		# Fetch the user data (on the first row)
		first_row = self._cursor.fetchone()

		# Check if a row was found
		if first_row:
			map_seed = first_row[1]  
			nature_points = first_row[2]
			# user_points_trend = first_row[3]
			user_points_trend = 0
			print(f"seed {map_seed}, points {nature_points}")
			return map_seed, nature_points, user_points_trend
		else:
			print('user data not found; user database empty')
			return None, 1, 0


	def set_user_data(self, user_nature_points, user_points_trend=None):
		if user_points_trend is not None:
			sql = """
				UPDATE UserSettings
				SET nature_points = ?,
				user_points_trend = ?
				WHERE id = 1;
				"""
			user_variables = (user_nature_points, user_points_trend)
		else:
			sql = """
				UPDATE UserSettings
				SET nature_points = ?
				WHERE id = 1;
				"""
			user_variables = (user_nature_points,)

		self._cursor.execute(sql, user_variables)
		self._conn.commit()

	# add character data to the database
	# takes a Character object
	def add_character(self, char):
		sql = """
				id INTEGER PRIMARY KEY AUTOINCREMENT,
		        x_pos INTEGER,
		        y_pos INTEGER,
		        name TEXT,
		        state TEXT,
		        animation_num INTEGER,
		        orientation TEXT,
		        move_time INTEGER"""



